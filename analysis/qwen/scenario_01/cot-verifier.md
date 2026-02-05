## Check-list  
`llm: Qwen` `prompt: pos-verifier` `scenario: 01`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [ ] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [x] Attributes are associated with the correct entities.
- [ ] Relationship types (1:1, 1:N, N:N) are correct.
- [x] There are no relationships not required by the domain (“spurious relationships”).
- [ ] There are no duplicated or inconsistent attributes.
- [x] There are no unnecessary entities.
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
- [x] Highly specific entities were avoided (preference for general concepts).
- [ ] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [ ] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- Missing `Contract` entity to relate `Employee` to `Hospital`.
- Missing `Physician`.
- Missing `Nurse`.
- Missing `Resident`.
- Missing `Dependent` entity; “employees may have dependents who are also patients” is underspecified.

#### Attributes
- `personnel_id` in `DepartmentCoordinator` is inappropriate; only employees should be allowed to perform this role.
- Missing `crm` attribute for `Physician`.
- Missing `coren` attribute for `Nurse`.
- Missing `responsible` attribute for `Resident`.
- Missing authorization (string) to map visitors who do not meet the normally permitted conditions.

#### Relationship
- The relationship between `DepartmentCoordinator` and `Personnel` is inferred via `personnel_id` but not explicitly modeled (cardinality is also missing).

#### Cardinality
- The cardinality between `Personnel` and `Patient` is modeled as `1:N` but should be `1:1` (the same applies to `Employee` and `Visitor`).
- The cardinality between `IdentificationCard` and `Visitor` is incorrect: it is `1:1` but should be `1:N`, since movement logs must be preserved.

#### Business Rule
- Missing phone records for `Personnel` (ideally modeled as a separate entity).
- The rule “a nurse cannot be a physician” is not enforced in the model (requires a posterior checking rule).
- It is not possible to record detailed in-hospital movement for all individuals.
