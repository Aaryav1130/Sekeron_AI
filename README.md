# Sekeron AI Intern Assessment - Stage 3

This repository contains the implementation for the Sekeron Stage 3 Practical Assessment: **Artist Intelligence & Recommendation Challenge**.

## 1. Approach & Architecture
We built an evidence-backed intelligence pipeline driven by Google's **Gemini 2.5 Flash** multimodal model. The system operates strictly via the CLI, using `rich` for an impactful terminal dashboard that honors the "no frontend" constraint while providing an excellent demo experience.

1. **Media Selection (`src/media_extractor.py`):** Rather than uploading hundreds of gigabytes of media, we perform intelligent sampling. We extract 3 temporal keyframes from video files, subset images logically, and pass them to the multimodal model.
2. **AI Intelligence (`src/ai_engine.py`):** The engine processes both the profile text (claims) and media (evidence). Using Pydantic schemas, it strictly outputs JSON enforcing a split between claimed skills vs. demonstrated evidence.
3. **Recommender (`src/recommender.py`):** Takes vague intents, identifies gaps, matches based on *evidence* (not claims), and generates targeted clarifying questions.

## 2. Setup & Execution

**Prerequisites:** Python 3.10+

```bash
# 1. Clone/navigate to directory
cd Sekeron_Project

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 3. Install dependencies
pip install pydantic rich google-generativeai opencv-python pillow python-dotenv

# 4. Set your API Key
# Copy .env.example to .env and insert your Google Gemini API Key
copy .env.example .env
```

**Dataset:** Place the provided Google Drive dataset into `data/artists/` and `data/briefs/`.

### Running the Pipeline

You can run the full end-to-end demo:
```bash
python -m src.main --mode demo_all
```

Or run step-by-step:
1. `python -m src.main --mode analyze_artists`
2. `python -m src.main --mode recommend`
3. `python -m src.main --mode rerank`

## 3. Evaluation & Limitations

**Honest Limitations:**
* **Hallucination Risk:** Multimodal LLMs occasionally hallucinate details in dense video/audio. We mitigated this by requiring the model to provide specific `evidence_citations` (file timestamps) for every claim.
* **Corrupted Media:** In real-world data, files get corrupted. The pipeline gracefully degrades: if OpenCV fails to read a video, the system records "Unknown" confidence instead of crashing.
* **Cost vs Accuracy:** We used Gemini 2.5 Flash for speed and cost efficiency (100% free tier). For production, upgrading to Gemini 1.5 Pro would yield deeper nuances in long-form video analysis.
