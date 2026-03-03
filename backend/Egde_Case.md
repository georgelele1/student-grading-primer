# Edge Case Documentation

## Edge Case Identified
Handling invalid or out-of-range marks when creating or updating a student.

The primer specification states that a student has a `mark` field (integer), but it does not specify:

- Whether the mark is required
- What range of values is acceptable
- How to handle non-integer input (e.g., strings or floats)
- What to do if the mark is omitted

This ambiguity creates potential inconsistencies and unexpected database states.

---

## How I Chose to Handle It

I implemented the following rules:

1. `mark` is optional when creating a student.
2. If `mark` is omitted, it defaults to `0`.
3. If `mark` is provided:
   - It must be an integer.
   - It must be within the range **0–100**.
4. Non-integer values (e.g.`"abc"`, `true`) are rejected.
5. Out-of-range values (e.g. `-10`, `150`) are rejected.
6. All validation failures return HTTP status `404` as required by the specification.

---

## Why This Approach

- Marks logically represent academic scores, which are typically between 0 and 100.
- Allowing invalid values (e.g. negative numbers or strings) would compromise data integrity.
- Defaulting missing marks to 0 ensures database consistency while still allowing partial data input.
- Strict validation prevents corrupted statistics in `/stats`.

This approach ensures:
- Persistent and valid data
- Consistent API behavior
- Protection against malformed client input