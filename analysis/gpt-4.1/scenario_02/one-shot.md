## Check-list  
`llm: GPT` `prompt: zero` `scenario: 01`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [ ] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [x] Attributes are associated with the correct entities.
- [x] Relationship types (1:1, 1:N, N:N) are correct.
- [ ] There are no relationships not required by the domain (“spurious relationships”).
- [ ] There are no duplicated or inconsistent attributes.
- [ ] There are no unnecessary entities.
- [ ] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [x] Entity names are clear, descriptive, and unambiguous.
- [x] Attribute names accurately reflect their content.
- [ ] The layout supports readability (subareas separated by context).
- [ ] Primary and foreign keys follow a consistent pattern.
- [ ] There are no multiple names for the same concept.

### 1.4. Simplicity
- [x] Absence of entities with too many attributes (e.g., > 12).
- [x] Absence of unnecessary complex relationships.
- [ ] Decomposition of large models into logical submodels.
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [x] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [ ] Anticipated domain changes can be implemented with minimal impact.
- [x] Highly specific entities were avoided (preference for general concepts).
- [x] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

### Notes

#### Entity
- Missing representation for `Nurse`, even though nurses are required by the specification.
- Missing representation for `Researcher`, or at least a researcher role associated with `Physician` or `Nurse`.
- Missing representation for administrative staff.
- Missing access log entity, such as `AccessLog` or `AccessEvent`, to record entries, exits, access attempts and blocked access.
- The model includes `Contract`, but its relationship with `Employee` and `Hospital` is not clear.
- The model includes a scheduling structure, but it is not clear whether it supports fixed schedules, flexible schedules, shifts and occasional physician activities.

#### Attributes
- The patient status is represented, but it is not clear whether it covers all states required by the specification.
- `PatientMovement` does not clearly record discharge, date and time of movement.
- `Visitor` does not have visitor type or visitor classification.
- Missing justification for visitor companion cases.
- `IdentificationCard` does not have access type or visual access color.
- `IdentificationCard` does not clearly distinguish temporary cards from personalized cards.
- Missing photo field for personalized employee cards.
- `TimeClockRecord` is not related to the card used or to the hospital/unit where the record happened.
- `CardFailure` does not record the failure date/time or the person responsible for manual verification.
- Missing data to support manual validation using official document and ID/registration number.
- Missing status to mark a defective card as inoperative.

#### Relationship
- The relationship between employee, dependent and patient is incomplete.
- The optional relationship between visitor and patient is not fully clear.
- The temporary assignment between `IdentificationCard` and patients/visitors is not clear.
- The history of card assignments is not clearly represented.

#### Cardinality
- The cardinality between `Hospital` and `Contract` is missing or unclear.
- The cardinality between `IdentificationCard` and card assignment/history is missing or unclear.
- The optional relationship between visitor and patient is not clearly represented.

#### Business Rule
- The model does not clearly enforce that a researcher must be a physician or a nurse.
- The model does not clearly support special authorization for visitors outside visiting hours.
- The model does not fully represent companion rules.
- The model does not clearly show that employee dependents can also be patients.
- The model does not fully support card loss rules: automatic invalidation, access blocking, logging and security alert.
- The model does not fully support card failure rules: manual validation, legal value of entry/exit, marking the card as inoperative and replacement.
- The model does not guarantee complete access history queries by person, date, department and type.
- The model does not guarantee complete workload reports by day, week and month.
- The model does not clearly prevent an employee from being scheduled in two hospital units at the same time.