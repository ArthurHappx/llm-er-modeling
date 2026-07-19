## Check-list  
`llm: GPT` `prompt: pos-verifier` `scenario: 02`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [ ] Are there sufficient attributes to characterize each entity?
- [ ] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [ ] Attributes are associated with the correct entities.
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
- [ ] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [x] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- Missing `Physician`, even though physicians are required by the specification.
- Missing `Nurse`, even though nurses are required by the specification.
- Missing `Resident`, even though residents are required and should be supervised by physicians.
- Missing `Researcher`, even though researchers are required and must be restricted to physicians or nurses.
- Missing representation for administrative staff.
- Missing `Contract` entity, so the model cannot represent employees working in multiple hospitals with different contract types.
- Missing entity or event to represent identification card loss.
- Missing entity or structure to represent card failure.
- Missing `AccessLog` entity, which is necessary to register entries, exits, access attempts, blocked access and access history.

#### Attributes
- The only hospital location information is `state`, which is insufficient to represent the hospital address or location properly.
- No constraints are applied to the attributes, including `NOT NULL`, `UNIQUE` or other integrity constraints.
- `Person` is missing required information such as birth date.
- `Physician`, `Nurse`, `Resident`, `Researcher` and administrative staff are not represented, so their specific attributes are also missing.
- `IdentificationCard` does not have a unique identification number.
- `IdentificationCard` does not have visual access color.
- The model does not clearly support personalized employee cards with photo.
- Since there is no card loss structure, the model lacks attributes for loss date, invalidation, replacement and security alert.
- Since there is no card failure structure, the model lacks attributes for failure reason, reading attempt, manual verification, responsible staff member and inoperative status.

#### Relationship
- The relationship between `Department` and `Employee` is incorrect; it is modeled as `N:1`, but a department should be able to have multiple employees.
- Since `Physician`, `Nurse`, `Resident` and `Researcher` are missing, the model cannot relate these roles to `Person`.
- The model does not represent the relationship between `Resident` and supervising `Physician`.
- The model does not represent the relationship restricting `Researcher` to `Physician` or `Nurse`.
- There is no relationship between `Employee`, `Hospital` and `Contract`, because `Contract` is missing.
- `PatientMovement` is not clearly connected to `Hospital` and `Department/Sector`, which weakens the movement history.
- The relationship between visitor and patient is missing or unclear.
- The companion relationship is missing or unclear.
- The model does not include relationships for card loss.
- The model does not include relationships for card failure.
- The model does not include relationships for access history because `AccessLog` is missing.

#### Cardinality
- The cardinality between `Department` and `Employee` is incorrect, since it is modeled as `N:1`.
- The cardinality between `Employee` and `Contract` cannot be represented because `Contract` is missing.
- The cardinality between `Hospital` and `Contract` cannot be represented because `Contract` is missing.
- The cardinality between `Resident` and supervising `Physician` cannot be represented because the required entities/relationships are missing.
- The cardinality between `Person` and `AccessLog` cannot be represented because `AccessLog` is missing.
- The cardinality between `IdentificationCard` and card loss/failure records cannot be represented because those structures are missing.
- The optional relationship between `Visitor` and `Patient` is not clearly represented.
- The optional relationship between visitor and companion role is not clearly represented.

#### Business Rule
- The model does not enforce that a researcher must be a physician or a nurse.
- The model does not support physicians working in multiple hospitals with different contracts.
- The model does not support different contract types such as CLT, PJ, plantonist or diarist.
- The model does not support the full card loss workflow: immediate registration, automatic invalidation, new card issue, access blocking, logging and security alert.
- The model does not support the full card failure workflow: failure reason, reading attempt, manual verification, legal-value entry/exit, inoperative status and replacement.
- The model does not support complete access history because `AccessLog` is missing.
- The model does not support access history queries by person, date, department and person type.
- The model does not enforce required data integrity rules because no constraints were applied.
- The incorrect `Department`–`Employee` cardinality weakens the representation of hospital staffing.