# Day 1 — Bytecode Autopsy

**Python version:** 3.14 (64-bit)

**Mental model:** CPython is a *stack machine*. Bytecode instructions push values onto an evaluation stack, pop them off to operate, and push results back. Reading a disassembly = tracking what each instruction pushes, pops, or where it jumps. In 3.14's dis format, jump targets are shown as labels (`L1:`, `L2:`) instead of raw byte offsets.

---

## 1. get_vat_rate — constant return

```text
 4           RESUME                   0

 5           LOAD_CONST               0 (0.15)
             RETURN_VALUE
```

- `RESUME 0` — internal bookkeeping emitted at the start of every function (supports tracing, debugging, generator resumption). Pushes nothing, pops nothing.
- `LOAD_CONST 0 (0.15)` — pushes constant index 0 from the function's constants table (the value 0.15) onto the stack. The number was baked into the code object at compile time — no runtime lookup.
- `RETURN_VALUE` — pops the top of the stack and returns it to the caller.

(Note: Python 3.12 fused these two into a single `RETURN_CONST` instruction; 3.14 went back to the explicit push-then-return pair.)

---

## 2. make_pilot_quote — closure

The outer function's variable `monthly_rate` must survive after the outer function returns, because the inner function still needs it. CPython solves this by storing it in a **cell** — a small container object — instead of a plain local.

### 2a. Outer

```text
 --          MAKE_CELL                0 (monthly_rate)

 7           RESUME                   0

 8           LOAD_FAST_BORROW         0 (monthly_rate)
             BUILD_TUPLE              1
             LOAD_CONST               0 (<code object quote>)
             MAKE_FUNCTION
             SET_FUNCTION_ATTRIBUTE   8 (closure)
             STORE_FAST               1 (quote)

10           LOAD_FAST_BORROW         1 (quote)
             RETURN_VALUE
```

- `MAKE_CELL 0 (monthly_rate)` — before the body runs, the parameter is converted from a plain local into a cell, because the compiler already knows an inner function will capture it. No stack effect.
- `RESUME 0` — bookkeeping.
- `LOAD_FAST_BORROW 0 (monthly_rate)` — pushes the **cell itself** (not the value inside it). Two version notes: (1) older Python used a dedicated `LOAD_CLOSURE` opcode here — per the official dis docs, `LOAD_CLOSURE` "pushes a reference to the cell" and is now a pseudo-instruction that the compiler replaces with a plain fast-local load, which is why it doesn't appear in the output; (2) the `_BORROW` suffix is a 3.14 optimisation meaning the value is pushed as a *borrowed reference* — the interpreter skips reference-count bookkeeping because it knows the local still owns the object.
- `BUILD_TUPLE 1` — pops 1 item (the cell), pushes a tuple containing it. A closure is always a tuple of cells.
- `LOAD_CONST 0 (<code object quote>)` — pushes the inner function's *compiled code object*. The body was compiled once at module compile time; only the function object gets created at runtime.
- `MAKE_FUNCTION` — pops the code object, pushes a new bare function object.
- `SET_FUNCTION_ATTRIBUTE 8 (closure)` — pops the closure tuple and the function, attaches the tuple as the function's closure, pushes the function back. (In 3.12 this was folded into `MAKE_FUNCTION 8 (closure)`; 3.13+ split it into its own instruction.) This is the moment the closure is born.
- `STORE_FAST 1 (quote)` — pops the finished function into local slot `quote`.
- `LOAD_FAST_BORROW 1 (quote)` — pushes it back onto the stack.
- `RETURN_VALUE` — pops it and returns it to the caller, cell and all.

### 2b. Inner (captured: `creative_tier_quote = make_pilot_quote(3500)`)

```text
 --          COPY_FREE_VARS           1

 8           RESUME                   0

 9           LOAD_DEREF               1 (monthly_rate)
             LOAD_FAST_BORROW         0 (months)
             BINARY_OP                5 (*)
             RETURN_VALUE
```

- `COPY_FREE_VARS 1` — at function entry, copies 1 closure cell from the function object into the running frame so the body can reach it. No stack effect.
- `RESUME 0` — bookkeeping.
- `LOAD_DEREF 1 (monthly_rate)` — the star of the show. Per the official dis docs, `LOAD_DEREF` loads the cell in the given slot and **pushes the value contained in the cell**. Compare it with the very next instruction: `months` is loaded with `LOAD_FAST_BORROW` because it's an ordinary local, but `monthly_rate` needs `LOAD_DEREF` because it's a **free variable** — a value dereferenced out of a cell captured from the enclosing function.
- `LOAD_FAST_BORROW 0 (months)` — pushes the local parameter.
- `BINARY_OP 5 (*)` — pops two values, multiplies them, pushes the result.
- `RETURN_VALUE` — pops the result and returns it.

### Connection to the E in LEGB

Python resolves names Local → Enclosing → Global → Built-in, and the disassembly shows each scope has its own opcode: **L** = `LOAD_FAST` (/ `LOAD_FAST_BORROW`), **E** = `LOAD_DEREF`, **G/B** = `LOAD_GLOBAL`. So "enclosing scope" is not a runtime search outward through frames — the compiler decided at compile time that `monthly_rate` is a free variable and emitted `LOAD_DEREF` for it. The whole cell pipeline (`MAKE_CELL` in the outer → closure tuple attached via `SET_FUNCTION_ATTRIBUTE` → `COPY_FREE_VARS` at inner entry → `LOAD_DEREF` at use) **is the E in LEGB, implemented**. It's also why the closure keeps working after `make_pilot_quote` has returned: the value doesn't live in the outer function's dead frame, it lives in the cell, which the inner function keeps alive.

---

## 3. total_invoices — loop

```text
12           RESUME                   0

13           LOAD_SMALL_INT           0
             STORE_FAST               1 (total)

14           LOAD_FAST_BORROW         0 (invoices)
             GET_ITER
     L1:     FOR_ITER                11 (to L2)
             STORE_FAST               2 (amount)

15           LOAD_FAST_BORROW_LOAD_FAST_BORROW 18 (total, amount)
             BINARY_OP                0 (+)
             STORE_FAST               1 (total)
             JUMP_BACKWARD           13 (to L1)

14   L2:     END_FOR
             POP_ITER

16           LOAD_FAST_BORROW         1 (total)
             RETURN_VALUE
```

- `RESUME 0` — bookkeeping.
- `LOAD_SMALL_INT 0` — pushes the integer 0. A 3.14 specialisation: small integers get their own instruction instead of a constants-table lookup (`LOAD_CONST`), because they're so common.
- `STORE_FAST 1 (total)` — pops it into local `total`. Together: `total = 0`.
- `LOAD_FAST_BORROW 0 (invoices)` — pushes the list parameter.
- `GET_ITER` — pops the list, pushes an *iterator* over it. Every for loop asks the object for an iterator first; it never walks the list directly.
- `L1: FOR_ITER 11 (to L2)` — asks the iterator for its next value. If there is one, pushes it and execution falls through; if the iterator is exhausted, jumps forward to label `L2`, exiting the loop. This instruction is the loop's entry point and its exit gate.
- `STORE_FAST 2 (amount)` — pops the produced value into `amount` — the `for amount in ...` binding.
- `LOAD_FAST_BORROW_LOAD_FAST_BORROW 18 (total, amount)` — a 3.14 **superinstruction**: two consecutive local loads fused into one instruction for speed. Pushes `total`, then pushes `amount`.
- `BINARY_OP 0 (+)` — pops both, adds them, pushes the sum.
- `STORE_FAST 1 (total)` — pops the sum back into `total`. These three lines are `total = total + amount`.
- `JUMP_BACKWARD 13 (to L1)` — **the instruction that makes it a loop**: an unconditional jump backwards to `L1`, i.e. back to `FOR_ITER`, which either produces the next value or exits. Without this one instruction the body would run once and fall through.
- `L2: END_FOR` — cleanup target when the iterator is exhausted.
- `POP_ITER` — pops the exhausted iterator off the stack (in 3.12 this was a generic `POP_TOP` folded into `END_FOR`; 3.14 gives it its own explicit instruction).
- `LOAD_FAST_BORROW 1 (total)` / `RETURN_VALUE` — push the final total, pop and return it.

**Answer to the task question:** the jump instruction that makes the loop loop is `JUMP_BACKWARD 13 (to L1)`, targeting the `FOR_ITER` at `L1`. The loop's entire control structure is that pair: `FOR_ITER`'s conditional forward jump out (`to L2`), and `JUMP_BACKWARD`'s unconditional jump back in.