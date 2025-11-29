# Policy Rules Engine Landscape Analysis

A comparative analysis of existing policy rules engines, microsimulation platforms, and rules-as-code tools to inform Cosilico Core's design.

---

## Summary Matrix

### Calculation/Simulation Engines

| System | Origin | License | Primary Use | Multi-target | Scale |
|--------|--------|---------|-------------|--------------|-------|
| **OpenFisca** | France | AGPL-3.0 | Microsimulation | Python only | Medium |
| **EUROMOD** | EU/JRC | Proprietary* | Microsimulation | C#/Stata | Large |
| **Tax-Calculator** | US/PSL | MIT | Federal tax | Python only | Medium |
| **TRIM3** | US/Urban | Proprietary | Benefits | Internal | Large |
| **Catala** | France/Inria | Apache 2.0 | Law encoding | Python/C | Small |
| **RegelRecht** | Netherlands | EUPL-1.2 | Law execution | Python/Go | PoC |

### DMN/Decision Engines

| System | Origin | License | Conformance | Language |
|--------|--------|---------|-------------|----------|
| **Drools DMN** | Apache KIE | Apache 2.0 | Level 3 | Java |
| **Camunda DMN** | Camunda | Apache 2.0 | Level 2 | Java |
| **dmn-js** | bpmn.io | Custom | Editor only | JavaScript |

### Business Rules Engines

| System | Origin | License | Algorithm | Language |
|--------|--------|---------|-----------|----------|
| **Drools** | Red Hat | Apache 2.0 | RETE | Java |
| **Nools** | Community | MIT | RETE | JavaScript |
| **json-rules-engine** | Community | ISC | Forward chain | JavaScript |

### Knowledge Representation (Non-calculation)

| System | Origin | License | Use Case |
|--------|--------|---------|----------|
| **Blawx** | Canada/Gov | MIT | Visual rules encoding, explanations |

*EUROMOD has limited open access for researchers

---

## 1. Microsimulation Engines

### 1.1 OpenFisca

**Overview**: The pioneering open-source policy-as-code framework, originally developed for France.

**Website**: https://openfisca.org/

**GitHub**: https://github.com/openfisca/openfisca-core

**Strengths**:
- First-mover: Established community and ecosystem
- Flexible formula system in Python
- Good time-handling for policy changes
- Tracer infrastructure for debugging

**Limitations**:
- Runtime dependency discovery (no static analysis)
- Memory explosion with multiple scenarios
- Python-only target
- AGPL license (viral, enterprise-unfriendly)
- 15-year-old architecture

**Relevance to Cosilico**: Direct predecessor. We need to solve all the problems OpenFisca couldn't while maintaining the ergonomic formula syntax.

---

### 1.2 EUROMOD

**Overview**: The official EU tax-benefit microsimulation model covering 28 member states.

**Website**: https://euromod-web.jrc.ec.europa.eu/

**Documentation**: https://euromod-web.jrc.ec.europa.eu/overview/what-is-euromod

**Strengths**:
- Comprehensive EU coverage
- Well-funded (JRC backing)
- Strong academic validation
- Connectors for Stata, Python, R
- Handles cross-country comparisons

**Limitations**:
- Proprietary core engine (C#)
- Limited to EU jurisdictions
- Closed development process
- Requires application for access
- GUI-based (harder to automate)

**Relevance to Cosilico**: Proves demand for cross-jurisdiction modeling. Their EU-wide parameter database is a good model for jurisdiction modularity.

---

### 1.3 Tax-Calculator (PSLmodels)

**Overview**: US federal income and payroll tax microsimulation model.

**Website**: https://taxcalc.pslmodels.org/

**GitHub**: https://github.com/PSLmodels/Tax-Calculator

**Strengths**:
- Clean MIT license
- Well-documented
- Validates against TAXSIM
- Active community (PSL ecosystem)
- Good test coverage

**Limitations**:
- Federal-only (no states)
- Tax-only (no benefits)
- Python-only
- Limited parameter flexibility
- Seeking maintainers

**Relevance to Cosilico**: Good model for open-source governance and TAXSIM validation approach. Their parameter system is cleaner than OpenFisca's.

---

### 1.4 TRIM3 (Urban Institute)

**Overview**: Comprehensive US transfer income microsimulation model, in use since the 1970s.

**Website**: https://trim.urban.org/

**Documentation**: https://www.urban.org/research/data-methods/data-analysis/quantitative-data-analysis/microsimulation/transfer-income-model-trim

**Strengths**:
- 50+ years of development
- Covers cash + in-kind transfers
- State-level variations
- Used for official government estimates
- Corrects for benefit underreporting

**Limitations**:
- Proprietary (contractor access only)
- Not publicly available
- Web interface only
- No API for integration
- Slow iteration on new policies

**Relevance to Cosilico**: The gold standard for benefit modeling in the US. We should aim to match their coverage while being open-source.

---

### 1.5 Budget Lab (Yale)

**Overview**: Modern tax microsimulation platform from Yale.

**Website**: https://budgetlab.yale.edu/research/tax-microsimulation-budget-lab

**Strengths**:
- Modern infrastructure
- Academic rigor
- Good data partnerships
- Active research output

**Limitations**:
- Not open source
- Limited to tax (not benefits)
- Internal use only

**Relevance to Cosilico**: Shows continued demand for modern microsimulation tools even from well-resourced institutions.

---

## 2. Rules-as-Code Tools

### 2.1 Catala

**Overview**: A domain-specific programming language designed for formalizing law, based on default logic.

**Website**: https://catala-lang.org/

**GitHub**: https://github.com/CatalaLang/catala

**Paper**: [Catala: A Programming Language for the Law](https://arxiv.org/pdf/2103.03198)

**Developer**: Denis Merigoux (Inria), collaborating with French tax administration (DGFiP)

**Strengths**:
- Mathematically rigorous (default logic as first-class feature)
- Literate programming (law + code together, lawyer-reviewable)
- Compiles to Python and C
- Formal verification possible (F* proof assistant)
- Apache 2.0 license
- Strong academic backing (Inria)
- Found bug in French official implementation of family benefits!
- Tested on real legislation (US IRC §121, French family benefits)

**Limitations**:
- Learning curve (OCaml-based, functional paradigm)
- Small ecosystem (research project, v1.0.0 released Nov 2025)
- **Not designed for microsimulation scale** - single household focus
- **No vectorization support** - compiles to scalar Python/C, not NumPy
- No time-varying parameter model (legislation changes over time)
- No entity hierarchy (Person → TaxUnit → Household aggregations)
- Explicitly warns against use for "simplified legal models" - wants full law encoding

**Technical Innovation**:
- Default logic as first-class feature (unique among PLs)
- "Definition-under-conditions" mirrors legal reasoning
- Enables legal professionals to review code
- Supports exceptions and overrides naturally

**Could Catala Meet Cosilico's Needs?**

| Requirement | Catala | Gap |
|-------------|--------|-----|
| Encode tax/benefit law | ✅ Excellent | - |
| Legal citations | ✅ Literate programming | - |
| Compile to Python | ✅ Yes | - |
| Compile to JS | ❌ No | Would need to add |
| Vectorized/batch (millions) | ❌ No | Fundamental architecture gap |
| Time-varying parameters | ❌ No | Would need to add |
| Entity hierarchies | ❌ No | Would need to add |
| Bi-temporal (knowledge dates) | ❌ No | Would need to add |
| Jurisdiction modularity | ❌ No | Would need to add |

**Assessment**: Catala is excellent for what it does - high-assurance single-case legal computation with formal verification. But it's fundamentally **not designed for microsimulation**. Processing 37 million French households requires millisecond-per-household performance, which Catala achieves via scalar code. But microsimulation needs vectorized batch processing of millions simultaneously, which Catala doesn't support.

**Relationship to Cosilico**:
- **Don't fork/extend Catala** - different goals, OCaml codebase
- **Learn from Catala** - default logic, literate programming, law structure
- **Potentially integrate** - could use Catala for high-assurance rules, compile output to our vectorized runtime
- **Complementary** - Catala for benefit administration (single case), Cosilico for microsimulation (batch)

**Relevance to Cosilico**:
- Adopt their "default logic" concepts for override handling
- Consider literate programming approach for law-code co-location
- Their "definition-under-conditions" maps to our variable model
- Different scale targets: Catala = single case correctness, Cosilico = population-scale simulation

---

### 2.2 RegelRecht (Netherlands)

**Overview**: Dutch government proof-of-concept for executable legislation.

**GitHub**: https://github.com/MinBZK/poc-machine-law

**Blog**: https://anneschuth.nl/2025/01/25/machine-law.html

**Strengths**:
- Government-backed (MinBZK)
- YAML-based law specifications
- Covers multiple Dutch benefit programs
- Includes formal verification
- MCP server for AI integration
- EUPL-1.2 license (permissive)

**Limitations**:
- Proof-of-concept stage
- Netherlands-specific
- Limited scale testing
- Python/Go stack (no JS target)

**Technical Innovation**:
- Laws as interconnected systems (not silos)
- Cross-organization rule execution
- AI/LLM integration for explanations

**Relevance to Cosilico**:
- Very aligned vision for benefit administration
- Their cross-program approach matches our jurisdiction model
- Worth tracking closely and potentially collaborating

---

### 2.3 Blawx

**Overview**: User-friendly web-based tool for encoding rules in declarative logic.

**Website**: https://dev.blawx.com/

**GitHub**: https://github.com/Lexpedite/blawx

**Developer**: Jason Morris (Government of Canada)

**Strengths**:
- Visual/drag-drop interface (accessible to non-programmers)
- Explanation generation (shows reasoning)
- Hypothetical reasoning support
- MIT license
- Government of Canada adoption

**Limitations**:
- Not production-ready
- Prolog-based (s(CASP))
- No scale/performance focus
- Single-scenario design

**Technical Innovation**:
- Block-based visual programming for law
- Answer explanations linked to law sections
- Scenario explorer

**Relevance to Cosilico**:
- Excellent explanation generation model
- Visual interface could complement our DSL
- Government adoption proves demand

---

### 2.4 18F/GSA Approach

**Overview**: US government digital services team's philosophy on rules implementation.

**Blog Posts**:
- [Implementing Rules Without Rules Engines](https://18f.gsa.gov/2018/10/09/implementing-rules-without-rules-engines/)
- [Exploring a New Way to Make Eligibility Rules Easier](https://18f.gsa.gov/2018/10/16/exploring-a-new-way-to-make-eligibility-rules-easier-to-implement/)

**Key Insight**: "If you've got rules, you're going to need a rules engine" is a false assumption. Rules can be implemented in general-purpose languages without overhead.

**Strengths**:
- Practical government experience
- Avoids vendor lock-in
- Open source philosophy
- Cross-functional team approach

**Limitations**:
- No specific tool/framework produced
- Philosophy, not implementation

**Relevance to Cosilico**:
- Validates our Python-based formula approach
- Emphasizes code-as-policy for auditability
- Supports avoiding complex rules engine abstractions

---

## 3. Decision Model and Notation (DMN)

DMN is an OMG standard for modeling executable business decisions. Unlike Blawx (which is more of a knowledge representation tool), DMN engines actually execute calculations.

### 3.1 DMN Standard

**Specification**: https://www.omg.org/dmn/

**Expression Language**: FEEL (Friendly Enough Expression Language)

**Key Concepts**:
- Decision Tables: Tabular rules with inputs, outputs, hit policies
- Decision Requirement Diagrams: Visual dependency graphs
- Boxed Expressions: Structured expressions (context, invocation, etc.)
- FEEL: Expression language with natural naming (spaces allowed)

**Conformance Levels**:
- Level 1: Decision tables only
- Level 2: S-FEEL (simplified expressions)
- Level 3: Full FEEL + all boxed expressions

**Relevance to Cosilico**: DMN's decision table format and FEEL expressions are worth studying. However, DMN is designed for business decisions, not tax/benefit calculations with time-varying parameters.

---

### 3.2 Drools DMN Engine

**Overview**: Apache KIE's conformance level 3 DMN implementation.

**Website**: https://drools.org/learn/dmn.html

**Documentation**: https://kie.apache.org/docs/components/drools/drools_dmn/

**Strengths**:
- Full DMN 1.1-1.4 support
- Conformance level 3 (complete FEEL)
- Open source (Apache 2.0)
- Production-ready
- Good tooling

**Limitations**:
- Java ecosystem only
- Heavy dependency
- Not designed for vectorized computation
- No time-varying parameter model

**Relevance to Cosilico**: Best-in-class DMN implementation. We should study their FEEL interpreter design. Consider supporting DMN import for decision tables.

---

### 3.3 Camunda DMN Engine

**Overview**: Lightweight DMN engine from Camunda BPM platform.

**GitHub**: https://github.com/camunda/camunda-engine-dmn

**Website**: https://camunda.com/platform/decision-engine/

**Tax Use Case**: [Deloitte uses Camunda DMN for tax consultations](https://camunda.com/blog/2021/06/how-deloitte-digitizes-tax-and-legal-consultations-with-dmn/)

**Strengths**:
- Proven for tax/legal use cases (Deloitte, BeOne)
- Cloud-native option (Zeebe)
- Good tooling (Modeler)
- Enterprise support available

**Limitations**:
- Java-centric
- Commercial features in Camunda 8
- Not designed for microsimulation scale
- Single-decision focus

**Relevance to Cosilico**: Validates that DMN works for tax calculations. Their chatbot UI pattern is interesting for benefit administration.

---

### 3.4 dmn-js

**Overview**: JavaScript DMN viewer/editor from bpmn.io.

**GitHub**: https://github.com/bpmn-io/dmn-js

**Website**: https://bpmn.io/toolkit/dmn-js/

**Demo**: https://demo.bpmn.io/dmn

**Strengths**:
- Pure JavaScript/browser
- Good UI components
- Active development
- Can embed in apps

**Limitations**:
- Viewer/editor only (no execution engine)
- Would need separate FEEL interpreter
- DMN 1.3 only

**Relevance to Cosilico**: Useful for building DMN import/export. Could provide familiar UI for decision table authoring.

---

## 4. Business Rules Engines

### 4.1 Drools

**Overview**: Enterprise-grade business rules management system from Red Hat.

**Website**: https://drools.org/

**GitHub**: https://github.com/kiegroup/drools

**Strengths**:
- Mature, production-ready
- RETE algorithm optimization
- Decision tables support
- Complex event processing
- Enterprise adoption
- Apache 2.0 license

**Limitations**:
- Java ecosystem only
- Heavy/complex
- Overkill for policy rules
- Not designed for microsimulation

**Relevance to Cosilico**: Good reference for optimization techniques (RETE), but too enterprise-focused for our needs.

---

### 3.2 Nools

**Overview**: JavaScript implementation of Drools' RETE algorithm.

**GitHub**: https://github.com/noolsjs/nools

**Website**: http://noolsjs.com/

**Strengths**:
- JavaScript native
- RETE algorithm
- Familiar JS syntax

**Limitations**:
- Maintenance unclear
- Limited adoption
- Basic feature set

**Relevance to Cosilico**: Shows demand for JS rules engines. We should evaluate RETE for our JS generator optimization.

---

### 3.3 json-rules-engine

**Overview**: Lightweight JavaScript rules engine with JSON rule definitions.

**GitHub**: https://github.com/CacheControl/json-rules-engine

**Strengths**:
- Simple JSON syntax
- Node.js native
- Good documentation

**Limitations**:
- Not designed for tax/benefits
- No time-varying rules
- Single evaluation focus

**Relevance to Cosilico**: Good reference for JSON-serializable rule definitions.

---

## 4. Key Differentiators for Cosilico

Based on this landscape analysis, Cosilico should differentiate by:

### 4.1 What Others Don't Have

| Gap | Current State | Cosilico Solution |
|-----|--------------|-------------------|
| **Multi-target compilation** | All are single-runtime | Python, JS, WASM, SQL, Spark |
| **Static analysis** | Runtime dependency discovery | Compile-time DAG |
| **Bi-temporal parameters** | Single time dimension | Effective + knowledge time |
| **First-class citations** | URLs as strings | Semantic law layer |
| **Jurisdiction modularity** | Monolithic packages | Composable packages |
| **Scale + accessibility** | Pick one | Both (compile for each) |
| **Permissive license + benefits** | AGPL or closed | Apache 2.0 |

### 4.2 What to Learn From Each

| System | Lesson for Cosilico |
|--------|---------------------|
| **OpenFisca** | Formula syntax, period handling, tracer |
| **EUROMOD** | Cross-jurisdiction parameter model |
| **Tax-Calculator** | TAXSIM validation, clean parameters |
| **TRIM3** | Comprehensive benefit coverage |
| **Catala** | Default logic, literate programming |
| **RegelRecht** | Cross-program integration, AI explanations |
| **Blawx** | Explanation generation, visual tools |
| **Drools** | RETE optimization, decision tables |

### 4.3 Technical Strategy

1. **Core formula language**: Python (like OpenFisca) for accessibility
2. **Law structure**: Default logic concepts (like Catala) for natural override handling
3. **Multi-target IR**: Compile once, deploy anywhere
4. **Jurisdiction model**: Hierarchical packages with inheritance and bi-directional references
5. **Explanation system**: Graph-based tracing with law citations
6. **Scale strategy**: Different execution backends for different scales

---

## 5. Potential Collaborators/Integrations

### High Priority

- **RegelRecht team (Anne Schuth)**: Very aligned vision, complementary jurisdictions
- **Catala team (Denis Merigoux)**: Could use Catala for high-assurance rules
- **PSLmodels**: Tax-Calculator integration, shared infrastructure

### Medium Priority

- **18F/USDS**: Government deployment expertise
- **Beeck Center (Georgetown)**: Rules as Code network
- **EUROMOD team**: Parameter sharing, validation data

### Lower Priority (Different Focus)

- **Blawx/Jason Morris**: Visual interface, different technical stack
- **Drools community**: Enterprise patterns, different domain

---

## 6. Open Questions

1. **Catala integration**: Should we support Catala as an input language for high-assurance rules?

2. **RegelRecht collaboration**: Is there potential for shared infrastructure with the Dutch team?

3. **Jurisdiction inheritance direction**: The user noted that dependencies go both ways (federal → state → local, but also SALT deduction going state → federal). How do we model bidirectional dependencies elegantly?

4. **AI/LLM integration**: RegelRecht has MCP server for AI. Should Cosilico support this pattern for explainability?

5. **Formal verification**: Catala supports formal proofs. Is this important for benefit administration use case?

---

## 7. Microdata Infrastructure (Orthogonal but Related)

Microdata construction is separate from the rules engine but deeply connected - it determines what the engine must handle.

### 7.1 PolicyEngine Data Tools

PolicyEngine has developed a sophisticated microdata infrastructure:

**policyengine-us-data**: Enhanced CPS microdata
- Combines multiple data sources (CPS, SCF, PUF)
- Imputes missing variables
- Creates analysis-ready datasets
- GitHub: https://github.com/PolicyEngine/policyengine-us-data

**microdf**: Weighted DataFrame operations
- Pandas extension for survey data
- Calculates weighted means, medians, Gini
- Distributional analysis tools
- GitHub: https://github.com/PolicyEngine/microdf

**microcalibrate**: Survey weight calibration
- Adjusts weights to match population targets
- Uses L0/L1 regularization for sparse adjustments
- GitHub: https://github.com/PolicyEngine/microcalibrate

**microimpute**: ML-based imputation
- Fills missing variables in survey data
- Multiple imputation methods
- GitHub: https://github.com/PolicyEngine/microimpute

### 7.2 Implications for Cosilico

| Microdata Need | Engine Requirement |
|---------------|-------------------|
| **Scale** | Process 100M+ records efficiently |
| **Iteration** | Fast recalculation during calibration |
| **Weighting** | Support weighted aggregation in engine |
| **Imputation** | Define which variables are "inputtable" |
| **Panel data** | Cross-period calculations, state tracking |

### 7.3 Synthetic Panel / Dynamic Microsimulation

Future goal: local dynamic long-term microdata with synthetic panel construction.

**Key challenges**:
- **Demographic transitions**: Birth, death, marriage, divorce
- **Economic mobility**: Income changes, job transitions
- **Policy feedback**: Behavior responses to policy changes
- **Cross-period references**: Pension calculations, benefit cliffs

**Engine support needed**:
- Efficient cross-period variable access (`income(-1)`, `income(-5)`)
- State tracking across simulation years
- Vectorized operations on panel dimensions
- Lazy evaluation for unused periods

**Related tools**:
- DYNASIM (Urban Institute): Dynamic microsimulation
- PENSIM (SSA): Pension-focused dynamic model
- LINDA (Sweden): Longitudinal individual database

### 7.4 Interface Design

Cosilico should define clear interfaces between:

```python
# Microdata layer (external)
class MicrodataSet:
    """Interface for microdata inputs."""
    def get_variable(self, name: str, period: Period) -> np.ndarray: ...
    def get_weight(self) -> np.ndarray: ...
    def n_records(self) -> int: ...

# Engine layer (Cosilico)
class Engine:
    """The rules engine."""
    def calculate(self, variables: List[str], data: MicrodataSet) -> Results: ...

# Results layer (external)
class Results:
    """Calculation outputs."""
    def to_dataframe(self) -> pd.DataFrame: ...
    def aggregate(self, method: str, weight: bool = True) -> Dict: ...
```

This separation means:
1. Microdata tools remain in separate packages (policyengine-us-data, etc.)
2. Engine is data-source agnostic
3. Clean interface for testing, validation, swapping data sources

---

## References

- [PolicyEngine GitHub](https://github.com/PolicyEngine)
- [OpenFisca Documentation](https://openfisca.org/doc/)
- [EUROMOD Overview](https://euromod-web.jrc.ec.europa.eu/overview/what-is-euromod)
- [Tax-Calculator Documentation](https://taxcalc.pslmodels.org/)
- [TRIM3 Overview](https://www.urban.org/research/data-methods/data-analysis/quantitative-data-analysis/microsimulation/transfer-income-model-trim)
- [Catala Paper](https://arxiv.org/pdf/2103.03198)
- [RegelRecht PoC](https://github.com/MinBZK/poc-machine-law)
- [Blawx GitHub](https://github.com/Lexpedite/blawx)
- [18F Rules Implementation](https://18f.gsa.gov/2018/10/09/implementing-rules-without-rules-engines/)
- [Drools Documentation](https://drools.org/)
