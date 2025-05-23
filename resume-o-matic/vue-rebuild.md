# Reviewer UI: Vue Rebuild Spec

This document is the authoritative, clean-room specification for rebuilding the reviewer/admin interface as a Vue-based (frontend) app, with Python (FastAPI or Flask) backend, using the existing shared SQLite database as the API contract. If it is not specified here, it will not be built.

---

## 1. **General Principles**
- The reviewer interface is a web dashboard for reviewing, updating, and managing resume/cover letter submissions.
- The backend is Python (FastAPI or Flask), exposing REST endpoints for all DB operations.
- The frontend is Vue 3 (Composition API preferred), using REST to interact with the backend.
- The database schema is the single source of truth for data fields and types.
- All business logic (state transitions, cleaning, etc.) must be implemented in the backend.

---

## 2. **Core Features & UI Components**

### 2.1. **Submissions Table (Top Section)**
- **Scrollable table** (shows 5 rows at a time, scrolls for more)
- **Columns (in order):**
  1. **Status** (colored label: red=rejected, green=approved, orange=pending, blue=applied)
     - Status is a clickable button; clicking it loads the submission details below (same as dropdown)
  2. **Job Title** (as a clickable link to the job_url)
  3. **Company**
  4. **Reviewer Notes**
- **Behavior:**
  - Clicking the status cell loads the details for that submission in the detail panel below.
  - Table is always in sync with the database (after any update, refresh, or deletion).

### 2.2. **Submission Selector**
- **Dropdown** listing all submissions (label: "Job Title at Company (ID: X)")
- Selecting a submission loads its details in the detail panel below.
- Dropdown is always in sync with the database and table.

### 2.3. **Submission Detail Panel**
- **Fields displayed/edited:**
  - **Job Description** (readonly, multiline)
  - **Tailored Resume/CV** (readonly, multiline)
  - **Cover Letter** (editable, multiline, with Save button)
  - **Reviewer Notes** (editable, single line or multiline)
  - **State** (dropdown: pending, approved, rejected, applied)
- **Buttons:**
  - **Update State/Notes**: Saves state and reviewer notes to DB
  - **Delete Submission**: Deletes the submission from DB
  - **Regenerate Resume/CV & Cover Letter**: Triggers backend regeneration (API call)
  - **Save Cover Letter**: Saves the edited cover letter to DB (with AI punctuation cleaning)

### 2.4. **Corrections Table**
- **Readonly table** of corrections (if present)
- Columns: ID, Section, Original, Corrected, Context, Timestamp

---

## 3. **Database/API Contract**
- All data is stored in a SQLite DB with the following relevant fields for each submission:
  - id (int, PK)
  - timestamp (str)
  - job_description (str)
  - company_details (str)
  - company_name (str)
  - job_title (str)
  - job_url (str)
  - mode (str)
  - tone (str)
  - emphasis (str)
  - resume_pdf_path (str)
  - tailored_resume (str)
  - cover_letter (str)
  - notes (str)
  - state (str: pending, approved, rejected, applied)
  - reviewer_notes (str)
- All CRUD operations must be exposed as REST endpoints.
- All text fields (resume, cover letter) must be cleaned for AI tell-tale punctuation (see below) on save.

---

## 4. **AI Punctuation Cleaning (Backend)**
- On every save of resume or cover letter, the backend must:
  - Replace emdash/endash (with or without spaces) with ' - '
  - Replace curly single quotes (‘ ’) with '
  - Replace curly double quotes (“ ”) with "
  - Collapse multiple spaces to one
- A one-time endpoint must be available to clean all existing submissions in the DB.

---

## 5. **Event/Interaction Logic**
- **Table and dropdown are always in sync.**
- **Clicking a status cell or selecting from the dropdown loads the detail panel.**
- **All updates (state, notes, cover letter) immediately update the table and dropdown.**
- **Deleting a submission removes it from the table and dropdown, and clears the detail panel.**
- **Regenerate button triggers backend logic and updates the detail panel on completion.**

---

## 6. **Styling/UX**
- Use modern, clean, dark theme (match current Gradio look if possible)
- Table rows are not editable inline (all edits via detail panel)
- Status labels are colored and visually distinct
- All links open in a new tab
- All actions have clear feedback (success/error)

---

## 7. **Out of Scope**
- No facts/tweaks system in v2
- No inline table editing
- No user authentication (unless specified later)
- No Gradio components in reviewer UI

---

## 8. **Future/Optional**
- Modal or inline correction UX (see `rebuild.md` for next iteration)
- Sorting/filtering for the table
- Reviewer activity log

---

## 9. **Filesystem & Repository Structure**

- The Vue-based reviewer interface should be developed as a separate subproject within the main repo, to keep concerns cleanly separated.
- Recommended structure:

```
tailored-resume-bot/
├── v2/                        # Existing v2 Python backend (Gradio, DB, etc.)
├── reviewer-vue/              # NEW: Vue-based reviewer interface (this spec)
│   ├── backend/               # Python FastAPI/Flask backend for reviewer API
│   │   ├── app.py             # Main backend app (REST API)
│   │   ├── db.py              # DB access layer (shared schema)
│   │   ├── models.py          # Pydantic models/schemas
│   │   ├── requirements.txt   # Backend dependencies
│   │   └── ...
│   └── frontend/              # Vue 3 frontend
│       ├── src/
│       │   ├── components/
│       │   ├── views/
│       │   ├── App.vue
│       │   └── main.js
│       ├── public/
│       ├── package.json
│       └── ...
├── .env                       # Shared environment config (if needed)
├── README.md
├── vue-rebuild.md             # This spec
└── ...
```

- **Backend**: `reviewer-vue/backend/` should expose REST endpoints for all reviewer operations, using the same SQLite DB as the rest of the project.
- **Frontend**: `reviewer-vue/frontend/` is a standard Vue 3 project, consuming the backend API.
- **Deployment**: The reviewer app can be run as a separate service/container, or integrated into the main deployment as needed.
- **Docs**: All reviewer-specific docs/specs should live in `reviewer-vue/` or at the project root as appropriate.

---

## 10. **Deployment & Subdomain Requirements**

- The Vue-based reviewer interface (`reviewer-vue`) must be deployed as a new service in the existing `docker-compose.yml`.
- It must be accessible at the subdomain: `reviewer-vue.gavincowie.com`.
- **Traefik Integration:**
  - The service must include appropriate Traefik labels for routing, e.g.:
    - `traefik.enable=true`
    - `traefik.http.routers.reviewer-vue.rule=Host(`reviewer-vue.gavincowie.com`)`
    - `traefik.http.services.reviewer-vue.loadbalancer.server.port=PORT` (where PORT is the internal port)
    - Add any necessary middleware (e.g., HTTPS redirect, auth if needed)
- **Cloudflare DNS:**
  - The subdomain `reviewer-vue.gavincowie.com` must be created/managed via Cloudflare API automation.
  - Document the required Cloudflare API steps/scripts for DNS record creation.
- **Docker Compose:**
  - Add a new service block for `reviewer-vue` (backend and frontend, or as a single container if using a full-stack image).
  - Ensure the service is on the correct Docker network for Traefik to route traffic.
  - Mount the shared SQLite DB as needed (read/write access for backend).
- **Environment Variables:**
  - Document any required env vars for Traefik, Cloudflare, or the app itself.
- **README/Docs:**
  - Update project documentation to include deployment, subdomain, and DNS setup steps.

---

**This document is the full spec for the Vue-based reviewer interface. If a feature or behavior is not listed here, it will not be built.** 