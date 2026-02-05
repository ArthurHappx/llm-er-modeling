## Check-list  
`llm: GPT` `prompt: pos-verifier` `scenario: 01`

### 1.1. Completeness
- [x] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
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
- [x] The layout supports readability (subareas separated by context).
- [x] Primary and foreign keys follow a consistent pattern.
- [x] There are no multiple names for the same concept.

### 1.4. Simplicity
- [x] Absence of entities with too many attributes (e.g., > 12).
- [ ] Absence of unnecessary complex relationships.
- [x] Decomposition of large models into logical submodels.
- [x] Limited depth of generalization/specialization hierarchies (e.g., > 3).
- [ ] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [x] Anticipated domain changes can be implemented with minimal impact.
- [x] Highly specific entities were avoided.
- [x] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes
- Adds reasonable, non-specified but useful attributes.
- Cardinality `"Resident 1--* ResidentSupervision"` is plausible, although the specification suggests `1:1`.
- Main issue: integrity maintenance due to redundant attributes that could be inferred.

#### Entity
- `PersonRole` is not required by the scenario but increases flexibility for role assignment.

#### Attributes
- `hire_date` and `termination_date` belong to `EmploymentContract`, not `Employee`.
- `phone` may be multivalued; `primary_phone` and `secondary_phone` are a practical alternative.
- `is_active` in `IdentificationCard` is redundant given `assignment_end_ts`.
- `is_personalized` in `CardAssignment` is redundant with `has_photo`.
- `employee_id`, `card_id`, and `matched_schedule_id` in `TimeClockRecord` ease queries but risk integrity.
- In `VisitorAccess`, `hospital_id` and `visitor_id` can be inferred.
- `patient_id` in `VisitorAccess` is inadequate for non-patient visits.
- `matched_schedule_id` should not be stored in `TimeClockRecord`.

#### Relationship
- Redundant relationships:
  - `"Hospital 1--* VisitorAccess"`
  - `"Visitor 1--* VisitorAccess"`
- `TimeClockRecord` should store the access location.

#### Cardinality
- `1:N` that should be `1:1`:
  - `"Employee 1--* Physician"`
  - `"Employee 1--* Nurse"`
  - `"Person 1--* Patient"`
  - `"Person 1--* Employee"`
  - `"Patient 1--* EmployeeDependent"`

#### Business Rule
- Movement tracking is detailed for patients and visitors; employee tracking is indirect via time clock records.
