# Decision Note: Sekeron AI Capability & Recommendation System

## 1. Supported Decision
This system supports the **candidate shortlisting decision** for hirers. It evaluates whether an artist's portfolio genuinely backs up their profile claims, assesses their capabilities objectively across category-specific dimensions, and matches these capabilities against incomplete, vague hirer intents. It produces an initial rank of the top 2 candidates and formulates high-impact clarifying questions to refine the match.

## 2. Scope & Non-Goals
**In Scope:**
* Multimodal analysis of images, audio, and video to extract demonstrated capabilities.
* Natural language interpretation of conversational hirer briefs.
* Separation of "profile claims" from "demonstrated evidence".
* Providing an explicit confidence score and handling damaged/incomplete profiles gracefully.

**Non-Goals:**
* Inferring character, reliability, popularity, or professionalism from portfolios.
* Web scraping or cross-referencing artists online.
* Providing a user-facing frontend or real-time web application.
* Training custom models (we utilize zero-shot/few-shot capabilities of frontier multimodal LLMs).

## 3. Capability Dimensions
We evaluate artists based on evidence-backed category-specific dimensions:

**Photographers:**
1. *Technical Skill:* Exposure, sharpness, dynamic range.
2. *Lighting:* Natural vs. studio, control of shadows.
3. *Composition:* Framing, rule of thirds, perspective.
4. *Genre/Subject:* Portraits, landscapes, events, product, etc.

**Musicians:**
1. *Genre/Style:* Rock, classical, electronic, acoustic, etc.
2. *Instrumentation/Role:* Vocalist, guitarist, producer, multi-instrumentalist.
3. *Production Quality:* Mix clarity, mastering level.
4. *Pacing/Energy:* Tempo, dynamic variation.

**Video Editors:**
1. *Editing Style:* Pacing, narrative flow, montage vs. storytelling.
2. *Color Grading:* LUTs used, visual consistency, mood.
3. *Technical Quality:* Transitions, resolution, graphic overlays.
4. *Genre Context:* Corporate, cinematic, music video, wedding.

## 4. Main Assumptions & Risks
* **Assumption:** The Google Gemini 2.5 Flash model's multimodal zero-shot capabilities are sufficient to accurately assess raw media (audio/video/images) without domain-specific fine-tuning.
* **Risk:** LLMs are prone to hallucinating evidence. *Mitigation:* The system strictly prompts the model to cite specific timestamps (video/audio) or image characteristics when generating an evidence claim.
* **Risk:** Incomplete or corrupted media. *Mitigation:* The media extraction pipeline uses graceful error handling (e.g., if a file is unreadable, it flags the dimension as 'unknown' rather than crashing the pipeline).
