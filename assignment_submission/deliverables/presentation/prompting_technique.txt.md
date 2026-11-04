### 1. Primary Technique: Prompt Chaining / Sequential Task Decomposition

Instead of dumping the entire assignment into one massive prompt, you broke the project into sequential, dependent stages—giving one phase at a time, reviewing the output, and then initiating the next phase:

* **Prompt 1:** Exploration & Inventory (`2 Explore the original files... Put details in a file or folder named inventory.`)
* **Prompt 2:** Preprocessing & Leakage Prevention (`3 Prepare data in response to findings... Save output in a file or folder named findings.`)
* **Prompt 3:** Model Selection & Evaluation (`4 Compare and assess methods... Save to file or folder named comparisons.`)
* **Prompt 4:** Visual & Error Communication (`5 Explain the result visually... Put results in a file or folder called explanation.`)
* **Prompt 5:** Workflow Consolidation (`...create one master file or folder, named automation...`)
* **Prompt 6 & 7:** Problem Framing (`Problem statement: Focused Research Question...`)
* **Prompt 8 & 9:** Formal Reporting (`Can you write me a 6 page report in MS Word (.docx)...`)
* **Prompt 10:** Dissemination (`...build me a PowerPoint slide show with about 12 to 15 slides... with short video clip...`)

*In prompt engineering literature, this is known as Prompt Chaining or Workflow Pipeline Prompting—it prevents LLM context degradation and guarantees high quality at each intermediate checkpoint.*

---

### 2. Constraint-Based / Directive Prompting

You embedded strict positive and negative operational guardrails into your instructions:

* **Negative Constraints (What *not* to do):**
    * `"Do not remove an unusual value merely because it looks extreme."`
    * `"Check that no feature reveals the answer or was measured after it."`
    * `"Avoid interpreting an association as proof of cause."`
* **Positive Constraints (What *must* be done):**
    * `"Keep original files in data/raw."`
    * `"Split the data before fitting an imputer, encoder, scaler..."`
    * `"Include at least three labeled visuals: one about data quality... one distribution... one about the chosen result..."`
    * `"Captions should state the unit, sample size, what is plotted, and the conclusion you draw."`

---

### 3. Template-Guided / Exemplar Prompting

You pasted concrete structural Markdown tables into your prompts to define the required schema of the response:

* **Supplying the decision schema:**
  ```text
  Observed finding | Possible decision | What to document
  Blood pressure contains '?' | Convert '?' to missing... | Count affected rows...
  ```
* **Supplying the report rubric:**
  ```text
  Report section | Required evidence | Points
  ```

*This guided the agent to return structured tabular changelogs and audit logs rather than unstructured paragraphs.*

---

### 4. Output-Constrained / Goal-Oriented Prompting

Every prompt explicitly governed the deliverable format, naming convention, and size bounds:

* **File and folder specifications:** `inventory`, `findings`, `comparisons`, `explanation`, `automation`, `report.docx`, `presentation.pptx`.
* **Structural parameters:** `"aim for a clear 4 to 6 page report"`, `"PowerPoint slide show with about 12 to 15 slides"`, `"1 or 2 slides have a short video clip"`.

---

### 5. Interactive Human-in-the-Loop Steering & Audit Probing

You actively steered and audited the agent's execution:

* **Feasibility checks:** `"Or is that too much?"`
* **Format flexibility:** `"Can you go straight to .PDF or create as a .MD...?"`
* **Verification and defense questions:** `"How was missing data handled?"` and `"What type of prompting technique was used?"`

#### Summary Name

If you need to cite this technique for a rubric, write-up, or defense, you can call it:

**"Iterative Prompt Chaining with Specification-Guided Constraints and Template Framing"** (or **"Sequential Task-Decomposed Prompting"**).


<br>


