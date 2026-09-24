# ADR-013: Contract Verification Phase Plan

**Status:** Accepted

For each baseline contract, verification follows this fixed order:

1. identify legitimate producer and consumer(s);
2. verify ownership and layer placement against the frozen Architecture Map;
3. resolve overlap with existing contracts;
4. implement immutable typed semantics;
5. add known-value, invariant, boundary, and regression tests;
6. bind the implementation in `docs/contracts.md`;
7. execute the corresponding CI gate;
8. record the resulting evidence fingerprint and SHA before declaring PASS.

Skipping step 1 is prohibited because it creates orphan contracts and hidden duplicate semantics.
