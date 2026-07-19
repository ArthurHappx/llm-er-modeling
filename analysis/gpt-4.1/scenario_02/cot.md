## Check-list  
`llm: GPT` `prompt: CoT` `scenario: 02`

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
- [x] There are no duplicated or inconsistent attributes.
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
- Missing representation for administrative staff.
- Missing `AccessLog` entity, which is necessary to record entries, exits, access attempts, denied access and blocked access.
- Missing structure to represent identification card loss.
- `Contract`, `WorkSchedule`, `TimeClockRecord`, `AvailabilityException`, `CardFailure` and `PatientMovement` are present, which is a positive point.
- The model represents the main person roles, such as `Patient`, `Visitor`, `Employee`, `Physician`, `Nurse`, `Resident` and `Researcher`.

#### Attributes
- Missing complete patient status values, such as waiting for care, in care, hospitalized, under observation, in surgery and discharged.
- Missing visitor classification, which is required to define access restrictions.
- Missing unique identification number for `IdentificationCard`.
- Missing visual access color for `IdentificationCard`.
- Missing attributes to clearly represent temporary card assignment to patients and visitors.
- Missing card assignment history.
- Missing contract type, such as CLT, PJ, plantonist or diarist.
- Missing clear attributes to show that the contract controls the employee schedule.
- Missing data to support manual validation using official document and ID/registration number.
- Missing status or attribute to mark defective cards as inoperative.
- Missing data to represent defective card replacement.

#### Relationship
- The relationship between `Address` and `Person` is not clear enough, since addresses should apply to all people, not only employees.
- `PatientMovement` is not clearly related to `Department/Sector`, which weakens the history of patient movement between sectors.
- The model does not clearly represent that dependents of employees can also be patients.
- The model does not clearly support companion cases for visitors.
- The temporary relationship between `IdentificationCard` and patients/visitors is missing or unclear.
- The relationship between `Hospital` and `Contract` has unclear cardinality.
- The model does not include relationships related to `AccessLog`, since this entity is missing.

#### Cardinality
- The cardinality between `Hospital` and `Contract` is not clearly represented as `1:N`.
- Because `AccessLog` is missing, the cardinality between `Person` and access records cannot be validated.
- Because card assignment history is unclear, the cardinality between `IdentificationCard` and card assignment/history cannot be fully validated.

#### Business Rule
- The model does not clearly enforce that a researcher must be a physician or a nurse.
- The model does not fully support card loss rules, such as immediate registration, automatic invalidation, access blocking, access log registration and security alert.
- The model does not fully support defective card rules, since inoperative status and card replacement are not clearly represented.
- The model does not fully support access history queries by sector and person type.
- The model does not clearly guarantee workload reports by day, week and month.
- `AvailabilityException` exists, but it is not clear whether it is considered when validating employee schedules.