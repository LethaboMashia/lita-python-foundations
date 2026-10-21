# Predictions — AI-01 S1: Vector Toolkit and FAQ Matcher
*Worked out by hand, with reasoning, before writing a single line of code.*

## Why This Exercise Matters
Every one of these five operations — add, scale, length, dot product, cosine similarity — looks like simple arithmetic in isolation, but together they form the entire mathematical foundation underneath how modern NLP systems compare meaning. A FAQ matcher that uses cosine similarity isn't doing anything conceptually different from what a recommendation engine, a search ranking algorithm, or a semantic embedding model does under the hood. Working through these by hand first, rather than jumping straight to NumPy, is what actually builds the intuition for *why* cosine similarity is the right tool for comparing text meaning, rather than just memorizing a formula.

## add([2,5], [4,1])
Vector addition is defined elementwise: each corresponding pair of components is summed independently, with no interaction between dimensions.
`[2+4, 5+1]` = **[6, 6]**

Geometrically, this is the "tip-to-tail" rule: placing the second vector's tail at the first vector's tip, the sum is the vector from the origin to the new tip. This is also exactly how you'd combine two independent forces, displacements, or feature contributions — the operation has no special-casing per dimension, which is precisely what makes it generalize cleanly to vectors of any length (3D physics, or a 300-dimension word embedding).

## scale(3, [2,-1,4])
Scalar multiplication distributes across every component: multiply each one independently by the scalar.
`[3×2, 3×(-1), 3×4]` = **[6, -3, 12]**

Scaling stretches or shrinks a vector's magnitude *without changing its direction* (unless the scalar is negative, which flips it 180°). This property — direction-preservation under positive scaling — is exactly what makes cosine similarity meaningful later: two vectors pointing the same way but of different lengths (e.g. a short sentence and a long paragraph discussing the same topic) should be considered "similar in meaning" even though their raw magnitudes differ wildly. Cosine similarity is specifically designed to be invariant to this kind of scaling.

## length([6,8])
Magnitude (the Euclidean norm) is the square root of the sum of squared components — a direct generalization of the Pythagorean theorem from 2D right triangles into n-dimensional space.
`√(6² + 8²)` = `√(36 + 64)` = `√100` = **10**

This isn't a coincidence that it matches the classic 3-4-5 triangle scaled by 2 (6-8-10) — it's the same geometric relationship, just applied to an arbitrary vector rather than a drawn triangle. The squaring-then-rooting matters because it guarantees the result is always non-negative and treats positive and negative components symmetrically (a component of -8 contributes the same magnitude as +8), which is essential for "length" to mean what we intuitively expect it to mean regardless of which quadrant the vector points into.

## dot([1,2,3], [4,5,6])
The dot product sums the elementwise products across all dimensions.
`(1×4) + (2×5) + (3×6)` = `4 + 10 + 18` = **32**

The dot product is the single most important building block in this whole exercise: it's the mechanism by which two vectors' *alignment* gets measured as one number. A large positive dot product means the vectors point in generally similar directions; a dot product of zero means they're perpendicular (no shared direction at all); a negative dot product means they point in broadly opposite directions. Every later calculation — length (a vector dotted with itself, then square-rooted) and cosine similarity (dot product normalized by both lengths) — is built directly on top of this single operation.

## cosine([3,4], [4,3])
Cosine similarity is defined as the dot product divided by the product of both vectors' magnitudes: `cos(θ) = (a·b) / (|a| × |b|)`.

- dot = `(3×4) + (4×3)` = `12 + 12` = `24`
- |a| = `√(3²+4²)` = `√25` = `5`
- |b| = `√(4²+3²)` = `√25` = `5`
- cosine = `24 / (5×5)` = `24/25` = **0.96** — matches the given hint exactly.

The reason this formula specifically divides by the magnitudes (rather than just using the raw dot product) is to strip out the effect of vector *length* and isolate purely the *angle* between them — which is what "similarity" should mean when comparing meaning rather than comparing raw intensity. [3,4] and [4,3] are mirror images of each other across the diagonal line y=x, which intuitively should register as "pointing in a very similar direction" without being identical — a cosine similarity of 0.96 (close to the maximum of 1.0, but not exactly 1.0) captures exactly that intuition numerically.

## cosine([1,0], [0,1])
These are the two standard basis vectors of 2D space — one pointing purely along the x-axis, the other purely along the y-axis.
- dot = `(1×0) + (0×1)` = `0`
- cosine = `0 / (1×1)` = **0.0**

Perpendicular vectors always produce a cosine similarity of exactly 0, with no exceptions, because this is the geometric definition cosine similarity is built on: it literally equals cos(θ), the trigonometric cosine of the angle between the two vectors, and cos(90°) = 0 as a mathematical identity, not an approximation. This is the critical reference point for understanding the whole scale: 1.0 means identical direction, 0.0 means no directional relationship whatsoever (orthogonal), and -1.0 would mean exactly opposite directions. Every cosine similarity score the FAQ matcher produces later should be interpreted against this three-point scale.

## FAQ Matcher Predictions

**"open time please"** — I expect this to successfully match an "opening hours"-style FAQ despite being grammatically broken, and this is actually the single most important behavior the whole exercise is testing. Cosine similarity operates purely on vocabulary overlap in vector space — it has no concept of grammar, word order, or sentence correctness. As long as "open" and "time" appear as meaningful, non-trivial dimensions in the vector representation and the target FAQ's question contains semantically related vocabulary (even just "opening" and "hours"), the shared signal across those dimensions should produce a dot product — and therefore a cosine score — well above whatever threshold the matcher uses. This is precisely why cosine similarity, rather than exact string matching, is the right tool for a real-world FAQ system: real users don't type grammatically perfect queries.

**"hello"** — I expect this to fall below the matching threshold and correctly trigger the fallback response, and I expect this to be the correct, intended behavior rather than a flaw. A single greeting word has essentially zero semantic overlap with any FAQ about hours, pricing, policies, or whatever topics the actual FAQ list covers — its vector representation should be close to orthogonal (low cosine similarity, closer to the 0.0 reference point established above) against every FAQ entry. A well-designed matcher needs a fallback precisely because real users will sometimes type things that aren't questions at all, and silently forcing a best-available match in that case (rather than admitting "I don't understand that") would be a worse user experience than an honest fallback message.