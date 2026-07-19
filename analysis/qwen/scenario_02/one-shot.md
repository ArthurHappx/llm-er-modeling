## Check-list  
`llm: GPT` `prompt: CoT` `scenario: 02`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [ ] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [ ] Attributes are associated with the correct entities.
- [ ] Relationship types (1:1, 1:N, N:N) are correct.
- [ ] There are no relationships not required by the domain (“spurious relationships”).
- [x] There are no duplicated or inconsistent attributes.
- [ ] There are no unnecessary entities.
- [x] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [x] Entity names are clear, descriptive, and unambiguous.
- [x] Attribute names accurately reflect their content.
- [ ] The layout supports readability (subareas separated by context).
- [x] Primary and foreign keys follow a consistent pattern.
- [ ] There are no multiple names for the same concept.

### 1.4. Simplicity
- [x] Absence of entities with too many attributes (e.g., > 12).
- [x] Absence of unnecessary complex relationships.
- [x] Decomposition of large models into logical submodels.
- [x] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [x] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [ ] Anticipated domain changes can be implemented with minimal impact.
- [x] Highly specific entities were avoided (preference for general concepts).
- [ ] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- `Physician` exists, but it is not modeled as a role that `Person` can assume. It has no relationship with `Person` and is only related to `Resident`.
- `Nurse` exists, but it has no relationship with any other entity, which makes it isolated in the model.
- `Researcher` exists, but it also has no relationship with any other entity.
- Missing `EmployeeDependent` entity or an equivalent structure to represent employee dependents who may also be patients.
- Missing `Contract` entity, even though the specification requires employees, especially physicians, to work in multiple hospitals with different contract types.
- Missing `TimeClockRecord` entity, so the model cannot register employee clock-in and clock-out records.
- Missing capacity representation. There is no attribute or entity to represent hospital or department capacity.

#### Attributes
- Positive point: the model respects constraints such as `NOT NULL` and other minimum constraints.
- `Person` is missing some required personal data, such as birth date and phone/contact information.
- `Physician` does not have professional identification, such as `crm`.
- `Nurse` does not have professional identification, such as `coren`.
- `Patient` does not clearly represent VIP status.
- The patient status does not clearly cover all required values: waiting for care, in care, hospitalized, under observation, in surgery and discharged.
- `IdentificationCard` does not have visual access color.
- There is no attribute for department or hospital capacity.
- Since `TimeClockRecord` is missing, there are no attributes for employee clock-in, clock-out, date, card used or hospital/unit of the record.

#### Relationship
- `Physician`, `Nurse` and `Researcher` are not properly connected to `Person`, so the model does not clearly support the idea that a person can assume these roles.
- The relationship that restricts `Researcher` to being either a `Physician` or a `Nurse` is missing.
- The relationship between employee and dependent is missing.
- The model does not show that employee dependents can also be patients.
- There is no relationship between `Employee`, `Hospital` and `Contract`, because `Contract` is missing.
- There is no relationship involving `TimeClockRecord`, because the entity is missing.
- The model does not support full access history because `AccessLog` is missing.
- The temporary assignment between `IdentificationCard` and patients/visitors is missing or unclear.

#### Cardinality
- The cardinality between `Person` and `Physician` cannot be validated because `Physician` is not related to `Person`.
- The cardinality between `Person` and `Nurse` cannot be validated because `Nurse` is isolated.
- The cardinality between `Person` and `Researcher` cannot be validated because `Researcher` is isolated.
- The cardinality between `Employee` and `Contract` cannot be represented because `Contract` is missing.
- The cardinality between `Hospital` and `Contract` cannot be represented because `Contract` is missing.
- The cardinality between `Employee` and `TimeClockRecord` cannot be represented because `TimeClockRecord` is missing.
- The cardinality involving employee dependents cannot be verified because there is no `EmployeeDependent` entity or equivalent relationship.

#### Business Rule
- The model does not clearly support the rule that a person can assume multiple roles, because some role entities are disconnected from `Person`.
- The model does not enforce that a researcher must be a physician or a nurse.
- The model does not support employee contracts with different hospitals and different contract types.
- The model does not support employee time tracking, since `TimeClockRecord` is missing.
- The model cannot generate workload reports by day, week or month without time clock records.
- The model cannot verify if an employee exceeded the expected working time.
- The model cannot properly support occupancy reports or capacity alerts because capacity is not represented.
- The model cannot generate alerts when a department reaches 60%, 80% or 100% capacity.