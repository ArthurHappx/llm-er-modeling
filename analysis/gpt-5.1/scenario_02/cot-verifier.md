## Check-list  
`llm: GPT` `pos-verifier` `scenario: 02`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [x] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [x] Attributes are associated with the correct entities.
- [ ] Relationship types (1:1, 1:N, N:N) are correct.
- [x] There are no relationships not required by the domain (“spurious relationships”).
- [x] There are no duplicated or inconsistent attributes.
- [x] There are no unnecessary entities.
- [ ] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [x] Entity names are clear, descriptive, and unambiguous.
- [x] Attribute names accurately reflect their content.
- [ ] The layout supports readability (subareas separated by context).
- [x] Primary and foreign keys follow a consistent pattern.
- [x] There are no multiple names for the same concept.

### 1.4. Simplicity
- [x] Absence of entities with too many attributes (e.g., > 12).
- [x] Absence of unnecessary complex relationships.
- [x] Decomposition of large models into logical submodels.
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [x] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [ ] Anticipated domain changes can be implemented with minimal impact.
- [x] Highly specific entities were avoided (preference for general concepts).
- [x] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- Missing representation for administrative staff, even though administrative employees are required by the specification.
- Missing `AccessLog` entity, which is necessary to store access history by person, date, department and person type.
- Missing entity or event to represent identification card loss.
- The model only represents card failure, but it does not properly represent lost cards.
- `Hospital`, `Department`, `Person`, `Patient`, `Visitor`, `Employee`, `Physician`, `Nurse`, `Resident`, `Researcher`, `Contract`, `WorkSchedule`, `TimeClockRecord`, `AvailabilityException`, `PatientMovement` and `CardFailure` are present, which is a positive point.

#### Attributes
- No `NOT NULL`, `UNIQUE` or other relevant constraints are applied to the attributes.
- This is a problem because the specification requires essential personal data, such as name, address, phone, CPF, RG and birth date, to be stored for all people who access the hospital.
- `TimeClockRecord` does not clearly store clock-in and clock-out times.
- `IdentificationCard` does not have a unique identification number.
- `IdentificationCard` does not have access type.
- `IdentificationCard` does not have a visual access color or equivalent attribute.
- `Contract` does not store the contract type, such as CLT, PJ, plantonist or diarist.
- The patient status exists, but it is not clear whether it supports all required values: waiting for care, in care, hospitalized, under observation, in surgery and discharged.
- `Visitor` does not clearly store visitor classification, which is required to determine access restrictions.
- `PatientMovement` exists, but it does not clearly register admission, transfer and discharge as required movement types.
- `CardFailure` is well represented in several aspects, but the model does not clearly support card replacement after failure.

#### Relationship
- The model does not clearly show that a person can be both an employee and a patient.
- The model does not clearly show that a person can be both an employee and a visitor or companion.
- The address relationship should be reviewed, because address must be associated with `Person`, not only with `Employee`.
- `PatientMovement` is not clearly related to `Patient`, which weakens the patient movement history.
- The model does not clearly represent that employee dependents can also be patients.
- Temporary assignment between `IdentificationCard` and patients/visitors is missing or unclear.
- Relationships related to card loss are missing because the model does not include a card loss entity or event.
- Relationships related to `AccessLog` are missing because the model does not include an access log entity.

#### Cardinality
- The cardinality between `Person` and `Phone` is missing or unclear, if phone is modeled as a separate entity.
- The cardinality between `Person` and `AccessLog` cannot be represented because `AccessLog` is missing.
- The cardinality between `Employee` and `AvailabilityException` is unclear or not correctly represented.
- Cardinalities related to card loss cannot be represented because there is no card loss entity or event.
- Some important relationships are present, such as `Hospital` to `Department/Sector`, `Employee` to `Contract`, `Hospital` to `Contract`, `Patient` to `PatientMovement`, `Visitor` to `Visit`, and `IdentificationCard` to card assignment/history.

#### Business Rule
- The model does not support the full identification card loss workflow required by the specification.
- When a card is lost, the system should register the loss, invalidate the card, allow a new card to be issued, block access attempts using the lost card, register those attempts in log and generate a security alert.
- The model does not support complete access history because `AccessLog` is missing.
- The model does not clearly support access history queries by person, date, department and person type.
- The model does not enforce required constraints, which weakens data integrity.
- The model does not fully support department occupancy alerts at 60%, 80% and 100%.
- The model does not clearly support workload reports by day, week and month.
- `AvailabilityException` exists, but it is not clear whether it is considered when validating employee schedules.