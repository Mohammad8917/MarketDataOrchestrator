# ADR-012: Consumer Before Contract Implementation

**Status:** Accepted

A contract MUST NOT be implemented merely to satisfy the registry.

Before implementation, its consumer(s), producer(s), ownership boundary, and dependency direction MUST be identified. If no legitimate consumer exists, the contract is recorded as an orphan and remains NOT VERIFIED unless an architecture decision explicitly authorizes an interface-only contract.

This rule applies to every baseline contract, including `validation_result`.

