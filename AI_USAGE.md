# AI Usage Transparency

In accordance with the assessment rules, this document transparently details the use of AI tools in constructing this solution.

### Tools Used
* **Google Gemini 2.5 Flash:** Used as the core reasoning and multimodal extraction engine in `src/ai_engine.py` and `src/recommender.py`.
* **Coding Assistant (Agent):** Assisted in generating boilerplate code, Pydantic schemas, and laying out the `rich` TUI dashboard.

### What the AI Produced
* **Data extraction logic:** The multimodal prompts and strict JSON generation configs were heavily modeled using AI assistance to ensure consistent structured output.
* **Architecture scaffolding:** The module breakdown (`schemas.py`, `ai_engine.py`, `media_extractor.py`) was conceptualized collaboratively with the coding assistant.

### What I Personally Verified and Changed
* **Constraint Adherence:** I explicitly prevented the AI from building a web frontend, guiding it instead to build a robust CLI tool using `rich` to satisfy the demo requirement without breaking the "no frontend" rule.
* **Schema Design:** I manually designed the category-specific dimensions (e.g., distinguishing between a photographer's lighting constraints vs a video editor's pacing metrics) in `decision_note.md` and enforced them in the Pydantic schema.
* **Evidence Handling:** I specifically engineered the prompt in `ai_engine.py` to force the model to decouple `profile_claims` from `demonstrated_evidence` and to explicitly cite timestamps/files. The AI did not initially do this securely without my manual prompting logic.
