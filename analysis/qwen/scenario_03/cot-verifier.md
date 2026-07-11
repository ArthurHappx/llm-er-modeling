## Check-list  
`llm: Qwen` `prompt: pos-verifier` `scenario: 03`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [ ] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [x] Attributes are associated with the correct entities.
- [ ] Relationship types (1:1, 1:N, N:N) are correct.
- [ ] There are no relationships not required by the domain (“spurious relationships”).
- [x] There are no duplicated or inconsistent attributes.
- [ ] There are no unnecessary entities.
- [ ] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [x] Entity names are clear, descriptive, and unambiguous.
- [x] Attribute names accurately reflect their content.
- [x] The layout supports readability (subareas separated by context).
- [x] Primary and foreign keys follow a consistent pattern.
- [x] There are no multiple names for the same concept.

### 1.4. Simplicity
- [x] Absence of entities with too many attributes (e.g., > 12).
- [x] Absence of unnecessary complex relationships.
- [ ] Decomposition of large models into logical submodels.
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [x] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [ ] Anticipated domain changes can be implemented with minimal impact.
- [ ] Highly specific entities were avoided (preference for general concepts).
- [x] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- Missing `AccessLog` entity to store access history and record access attempts.
- The absence of `AccessLog` also affects the history of `IdentificationCard`, since access attempts should be registered.
- The model includes an entity related to capacity, but the capacity information cannot be properly consulted because it is not clearly represented in the model.

#### Attributes
- Although some attributes are present, several required attributes are not marked as `NOT NULL`.
- Required attributes of `Person` should be marked as `NOT NULL`.
- `Resident` does not have a supervisor properly represented.
- Missing field in `IdentificationCard` to reference the person’s photo.
- Missing alert/status attribute to indicate issues such as a lost card; the model only indicates whether the card is active or inactive.

#### Relationship
- The relationship indicating that a person can have one or more visitors is incorrect, since this does not represent the real business rule.
- Missing proper relationship or structure to connect access attempts, identification cards, and the person using the card.

#### Cardinality
- The cardinality between `Person` and `Visitor` is incorrect, since a person should not simply have one or more visitors in that way.

#### Business Rule
- The model does not properly handle identification card failures.
- The model does not store required information about card failure, such as the person who used the card, failure reason, reading attempt, manual validation, or how to mark the card as defective.
- The model does not properly support access history because there is no `AccessLog`.
- The model does not adequately enforce the required `NOT NULL` constraints.

