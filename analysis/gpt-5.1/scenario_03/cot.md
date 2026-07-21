## Check-list  
`llm: GPT` `prompt: CoT` `scenario: 03`

### 1.1. Completeness
- [ ] Have all domain entities been identified?
- [ ] Are all required relationships represented in the diagram?
- [x] Are there sufficient attributes to characterize each entity?
- [x] Do the cardinalities correctly represent the business rules?
- [ ] Does the model cover all requirements identified in the scope?

### 1.2. Correctness
- [x] Attributes are associated with the correct entities.
- [x] Relationship types (1:1, 1:N, N:N) are correct.
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
- Missing entity to register identification card loss.
- The model only includes an entity for card failure, but the specification also requires handling lost identification cards.


#### Attributes
- Required attributes are not marked as `NOT NULL`.
- The model fails to enforce mandatory data required by the specification, such as name, address, phone, CPF, RG and birth date for all people who access the hospital.
- Missing attributes or status fields to represent card loss, invalidation and replacement history.

#### Relationship
- Since the card loss entity is missing, the model also lacks the necessary relationships between lost cards, people, replacement cards and access logs.
- The relationship structure for handling card lifecycle events is incomplete.

#### Cardinality
- No specific cardinality issue was identified in the notes.

#### Business Rule
- The model does not support the business rule for loss of identification cards.
- When a card is lost, the system should invalidate the card, allow a new card to be issued, block future access attempts with the lost card and register these attempts in an access log.
- The model does not properly maintain the required history of active, replaced, lost, expired or invalidated cards.
- The model does not enforce the mandatory `NOT NULL` constraints required by the specification.