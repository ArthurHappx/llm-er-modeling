## Check-list  
`llm: GPT` `prompt: zero` `scenario: 01`

### 1.1. Completeness
- [x] Have all domain entities been identified?
- [x] Are all required relationships represented in the diagram?
- [x] Are there sufficient attributes to characterize each entity?
- [ ] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [ ] Attributes are associated with the correct entities.
- [ ] Relationship types (1:1, 1:N, N:N) are correct.
- [ ] There are no relationships not required by the domain (“spurious relationships”).
- [ ] There are no duplicated or inconsistent attributes.
- [ ] There are no unnecessary entities.
- [ ] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [x] Entity names are clear, descriptive, and unambiguous.
- [x] Attribute names accurately reflect their content.
- [ ] The layout supports readability (subareas separated by context).
- [x] Primary and foreign keys follow a consistent pattern.
- [x] There are no multiple names for the same concept.

### 1.4. Simplicity
- [ ] Absence of entities with too many attributes (e.g., > 12).
- [x] Absence of unnecessary complex relationships.
- [x] Decomposition of large models into logical submodels.
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [ ] Absence of n-ary relationships where two binary ones would suffice.

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
- `DepartmentType` does not need to be an entity; there is no justification for it in the specification.
- `Role` and `PersonRole` should not be present when `Nurse`, `Physician`, `Employee`, `Visitor`, and `Resident` entities already exist, as this increases integrity risks.
- The specification induces the registration of `EmployeeDependent` as a `Patient`, creating ambiguity.
- `DepartmentShiftResponsibility` is somewhat flawed (`is_coordinator` introduces integrity issues).

#### Attributes
- The specification requests contact phone numbers, but the model restricts them to `primary_phone` and `secondary_phone`.
- `hire_date` and `termination_date` should not be attributes of `Employee`, as the contract already stores this information.
- Difficulty in identifying whether a visitor left the hospital or merely moved to another department.
- `Shift` is used ambiguously (in both `DepartmentShiftResponsibility` and `EmployeeSchedule`).

#### Cardinality
- A `1:N` cardinality between `Department` and `DepartmentShiftResponsibility` seems inappropriate; nothing in the model specifies that a coordinator cannot act in more than one department (possibly not simultaneously).
- A `1:N` cardinality between `Person` and its specializations is incorrect; it should be `1:1`.

#### Business Rule
- Querying access history by person, date, department, and type is incomplete for `Employee`.
