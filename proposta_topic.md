<!-- Bozza per Blackboard, da consegnare entro ven 30/10 23:59. Completare il cognome di Edoardo. -->

**20875 Software Engineering: project topic**
Lorenzo Faella, Edoardo ______

**An eligibility engine for Italian business incentives**

incentivi.gov.it lists about 6,000 public incentives; 747 of them are open to businesses today. Its search filters by category, but it never tells a company whether it actually qualifies. We are building a tool that answers that question bando by bando. For each one it gives eligible, not eligible or "can't tell", and names the requirement that decided it.

The pipeline is written in Python. It downloads the official open-data export, normalises it and turns every bando into a rule file checked against a JSON Schema.
- **What works today:** a first version on the structured fields, tested against an independent implementation that reads the raw export directly.
- **The hard part:** requirements that exist only in free text, such as de minimis limits, headcount or years in business. We plan to extract them with an LLM and measure the extraction against a sample we label by hand.

On top of the engine, a questionnaire chooses the question that settles the most bandi. On the structured fields alone, the right first question (region) already settles 84% of bandi, against 18% for the portal's filter order. There, a good fixed order is as good as an adaptive one. We want to measure whether adaptivity starts to pay off once the extracted requirements multiply the possible questions.

Deliverables: the pipeline, the engine with its tests, and a small web demo.
