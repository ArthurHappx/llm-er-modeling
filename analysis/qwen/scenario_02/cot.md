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
- [ ] There are no duplicated or inconsistent attributes.
- [ ] There are no unnecessary entities.
- [ ] Minimum constraints (UNIQUE, NOT NULL) have been correctly mapped.

### 1.3. Clarity
- [ ] Entity names are clear, descriptive, and unambiguous.
- [ ] Attribute names accurately reflect their content.
- [ ] The layout supports readability (subareas separated by context).
- [ ] Primary and foreign keys follow a consistent pattern.
- [ ] There are no multiple names for the same concept.

### 1.4. Simplicity
- [ ] Absence of entities with too many attributes (e.g., > 12).
- [ ] Absence of unnecessary complex relationships.
- [ ] Decomposition of large models into logical submodels.
- [ ] Minimization of very deep generalization/specialization hierarchies (e.g., > 3).
- [ ] Absence of n-ary relationships where two binary ones would suffice.

### 1.5. Flexibility
- [ ] Anticipated domain changes can be implemented with minimal impact.
- [ ] Highly specific entities were avoided (preference for general concepts).
- [ ] Subtypes were used only when necessary.

### 1.6. Implementability
- [ ] No requirements demand complex triggers or external logic.
- [ ] Attribute types are compatible with the target DBMS.

---

### Notes

#### Entity
- 
#### Attributes
- 

#### Relationship
- 

#### Cardinality
- 

#### Business Rule
- 