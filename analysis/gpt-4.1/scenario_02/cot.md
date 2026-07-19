## Check-list  
`llm: GPT` `prompt: CoT` `scenario: 02`

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
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [ ] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [x] Anticipated domain changes can be implemented with minimal impact.
- [x] Highly specific entities were avoided (preference for general concepts).
- [x] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes
- Adds non-requested but useful attributes (reasonable to assume usefulness).
- Plausible assumption of the `"Resident 1--* ResidentSupervision"` cardinality, although the specification suggests `1:1`.
- Main issue: difficulty in maintaining integrity due to redundant attributes that could be inferred.

#### Entity
- `PersonRole` is not required for the specified scenario, but it may facilitate the described security team by allowing more flexible role assignment.

#### Attributes
- `hire_date` and `termination_date` should belong to `EmploymentContract`, not `Employee`.
- The specification allows `phone` to be multivalued (thus requiring a separate entity); however, `primary_phone` and `secondary_phone` are a practical alternative.
- `is_active` in `IdentificationCard` is redundant given `assignment_end_ts` in `CardAssignment`.
- Within scope, `is_personalized` in `CardAssignment` is synonymous with `has_photo` in `IdentificationCard`, making it redundant.
- `employee_id` and `card_id` in `TimeClockRecord` reduce temporal-interval queries but introduce integrity risks; the same applies to `matched_schedule_id`.
- In `VisitorAccess`, `hospital_id` can be inferred from `hospital_department_id`, and `visitor_id` from `card_id`.
- `patient_id` in `VisitorAccess` is not ideal, as some visits are not patient-related.
- `matched_schedule_id` should not be stored in `TimeClockRecord`, as it increases maintenance complexity.

#### Relationship
- Redundant relationships: `"Hospital 1--* VisitorAccess"`, `"Visitor 1--* VisitorAccess"`.
- `TimeClockRecord` should record the location where the time entry occurred.

#### Cardinality
- The cardinality between `Person` and `Employee` is incorrect; a person should have multiple associated contracts (including inactive ones for logging). Correct cardinality: `1:1`.
- Other `1:N` relationships that should be `1:1`:
  - `"Employee 1--* Physician"`
  - `"Employee 1--* Nurse"`
  - `"Person 1--* Patient"`
  - `"Patient 1--* EmployeeDependent"`

#### Business Rule
- Difficulty in tracking individual movement. Detailed tracking exists only for patients and visitors; employee tracking is indirectly supported via time clock records.
- The model does not distinguish between a department coordinator and the person responsible for each operational shift, although the specification requires it.
