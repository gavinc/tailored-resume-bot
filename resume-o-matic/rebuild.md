# Tailored Resume Bot: Technical Improvement Plan

## Phase 1: Immediate Improvements (v1, completed)
- [x] Add sample output format in the prompt for consistent structure
- [x] Separate resume and cover letter generation into two API/model calls
- [x] Add user-selectable tone (formal, friendly, etc.) and section emphasis
- [x] Warn users if input length risks exceeding model context window
- [x] Upgrade to GPT-4o for higher quality (if available/cost-acceptable)
- [x] Allow download of tailored resume and cover letter as separate text or PDF files
- [x] Add user-friendly error messages for API failures or bad uploads
- [x] Add configuration for output format, section order, and keyword strategy
- [x] Add job URL, recruiter/company selection, and state tracking
- [x] Add persistent facts/tweaks system and reviewer workflow

## Phase 2: Advanced/Completed Improvements (v1, completed)
- [x] Highlight or mark keywords from the job description in the output
- [x] Add support for local LLMs via LMStudio REST API for privacy/cost
- [x] Allow user to select model (OpenAI vs. local)
- [x] Evaluate and optionally switch to `pdfplumber` or `pdfminer.six` for more robust text extraction
- [x] Add error handling for failed or partial PDF extraction
- [x] Support multi-language output (optional)
- [x] Clearly inform users that data is sent to OpenAI (unless using local model)
- [x] Ensure API keys are never exposed in logs or UI
- [x] Add option to purge user data after processing
- [x] Modularize code for easier maintenance and extension
- [x] Support for additional document types (e.g., DOCX)
- [x] Add unit and integration tests for core functions
- [x] Add pre-commit hooks and linting (PEP8 compliance)
- [x] Document all functions and modules

---

## v2 Roadmap (in `v2/` subdirectory)
- [ ] Modularize all code: db.py, llm.py, ui.py, facts_tweaks.py, submission.py, main.py
- [ ] Implement a migration script: `migrate_v1_to_v2.py` to copy/transform v1 data
- [ ] Use a new database: `v2/facts_tweaks_v2.db`
- [ ] Implement remaining improvements and new features in v2 modules
- [ ] Run v2 server on a new port (e.g., 7862) for side-by-side operation
- [ ] Add v2/README.md and update documentation
- [ ] Plan and test migration/rollback
- [ ] NEXT ITERATION: Implement a Gradio custom component (React) for true inline/modal correction UX (right-click, modal at cursor, robust event handling)

---

**Prioritize improvements based on user feedback and business goals.** 