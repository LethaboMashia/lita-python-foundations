# SQL Injection: Attack and Cure

A hands-on demonstration of SQL injection against a Python/SQLite login function, and the parameterised-query fix that closes it.

## What SQL injection is

Every SQL query is part **command** (SELECT, WHERE, AND, the quote marks) and part **data** (the actual values). The quote mark is the fence between them: text inside quotes is data, everything outside is command.

SQL injection happens when user input is glued directly into the query string, and that input contains a quote mark. The quote closes the data string early, and whatever comes after it is read as command instead of data — the attacker's text crosses the fence.

**The attack string used here:** `' OR '1'='1`

## Why login_unsafe is vulnerable

`login_unsafe` builds its query like this:

```python
query = "SELECT * FROM users WHERE email = '" + email + "' AND password = '" + pw + "'"
```

With `email='attacker@evil.com'` and `pw="' OR '1'='1"`, the final string the database actually receives is:

```sql
SELECT * FROM users WHERE email = 'attacker@evil.com' AND password = '' OR '1'='1'
```

Trace it: the leading `'` in the password closes the password string early. `OR '1'='1'` is now outside the quotes, so it's read as grammar. The WHERE clause becomes "email matches AND password is empty, OR 1=1" — and `1=1` is always true, so every row matches. `fetchone()` returns the first row in the table, regardless of which email or password was real.

**Real output from this build:** the attack logged in as `alice@example.com` with no real password known, proving the exploit works.

## How login_safe fixes it

`login_safe` builds the same query with placeholders:

```python
query = "SELECT * FROM users WHERE email = ? AND password = ?"
cursor.execute(query, (email, pw))
```

This sends the query in two separate deliveries:
1. **The template first** — SQLite receives `... WHERE email = ? AND password = ?` with no data in it at all, and locks the grammar. It decides, permanently, that there are exactly two data slots.
2. **The values second** — `email` and `pw` arrive afterward, labelled as data, and get dropped into the already-fixed slots.

Because the grammar is locked before the data exists, nothing in the data can add a new `OR`, close a string, or change the grammar. The same attack string is just compared as a literal password — it matches no row, and login correctly fails.

**Real output from this build:** `login_safe` returned `None` for the identical payload that broke `login_unsafe`.

## Why parameterising is a cure and escaping is only a patch

Escaping tries to clean dangerous characters out of the data *after* it's already near the grammar — scanning for quotes and adding backslashes. It's a patch: easy to miss a case, and different databases escape differently.

Parameterising removes data from the grammar-building step entirely. The grammar is finalised before any user input exists, so there's no point in the process where data could ever become command. That's a structural fix, not a cleanup step.

## How to run
1. `pip install pytest`
2. `python demo_attack.py` — runs the live exploit against both versions
3. `pytest -v` — runs the automated proof

I built a working SQL injection demo against my own vulnerable login function, then fixed it with parameterised queries. I can trace exactly why the glued-string version breaks — the attacker's quote mark closes the password string early and the rest becomes part of the WHERE clause — and why binding values with `?` placeholders prevents it structurally, not just by cleaning input. All my real projects use parameterised queries for this reason.