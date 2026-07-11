## Check-list  
`llm: GPT` `prompt: zero` `scenario: 03`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [x] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [ ] Attributes are associated with the correct entities.
- [x] Relationship types (1:1, 1:N, N:N) are correct.
- [ ] There are no relationships not required by the domain (“spurious relationships”).
- [ ] There are no duplicated or inconsistent attributes.
- [ ] There are no unnecessary entities.
- [ ] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [x] Entity names are clear, descriptive, and unambiguous.
- [x] Attribute names accurately reflect their content.
- [ ] The layout supports readability (subareas separated by context).
- [x] Primary and foreign keys follow a consistent pattern.
- [ ] There are no multiple names for the same concept.

### 1.4. Simplicity
- [x] Absence of entities with too many attributes (e.g., > 12).
- [x] Absence of unnecessary complex relationships.
- [ ] Decomposition of large models into logical submodels.
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [x] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [ ] Anticipated domain changes can be implemented with minimal impact.
- [ ] Highly specific entities were avoided (preference for general concepts).
- [ ] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- There are unnecessary entities for `City` and `State`, since the specification does not require them as independent entities. This information could be handled inside `Address`.
- Missing entities or subtypes for `Visitor`, `Physician`, `Nurse`, `Resident`, `AdministrativeStaff`, `Researcher` and `VipPatient`.
- These roles were treated as attributes of `Person`, but they should be modeled as entities or subtypes because they have specific rules, relationships and constraints.
- Positive point: the model includes `EmployeeContract`, which helps represent the relationship between employees and hospitals.

#### Attributes
- There are boolean attributes such as `is_patient` and similar role indicators, even though some corresponding entities also exist. This creates redundancy and inconsistency.
- `Employee` does not have a clear `role` attribute, and the necessary employee subtypes are also missing.
- `rg` and `birth_date` in `Person` should be marked as `NOT NULL`, according to the specification.
- `IdentificationCard` does not have an attribute for the color that visually identifies the access type.
- `TimeClockRecord` does not properly store clock-in and clock-out times.
- `ShiftSwap` does not store the coordinator who approved the shift exchange.
- The model does not store historical information for cases where an identification card is lost.

#### Relationship
- The relationship between `Resident` and the responsible `Physician` is missing or not clear enough.
- The relationship between `ShiftSwap` and the coordinator who approved the exchange is missing.
- The use of role attributes in `Person` weakens the relationships that should exist between `Person` and its specific roles, such as `Patient`, `Visitor`, `Physician`, `Nurse`, `Resident` and `Researcher`.
- The model does not clearly support the historical relationship between a lost card and the person who used or owned it.

#### Cardinality
- No specific cardinality problem was clearly identified in the notes.
- However, because several required relationships are missing or unclear, some cardinalities cannot be properly verified.

#### Business Rule
- The rule that a `Researcher` can only be a `Physician` or a `Nurse` is not clear enough in the model.
- The model does not properly support the business rule for lost identification cards, since it does not keep the required history.
- The model does not clearly enforce the distinction between different roles of a person, especially when a person can be an employee, patient, visitor or companion.
- The missing `NOT NULL` constraints violate the requirement that name, address, phone, CPF, RG and birth date must be mandatory for all people who access the hospital.
