# Tailored Resume and Cover Letter Generator

This project is a custom-built tool designed to help job seekers generate a tailored resume and cover letter. The application extracts all details from an original PDF resume and uses user-provided job descriptions and company information to reformat and optimize the content for Applicant Tracking Systems (ATS) while retaining a natural, human tone.

## Features

- **ATS-Friendly Output:**  
  Produces plain-text resumes with clear, capitalized section headings and bullet points to ensure compatibility with automated screening systems.

- **Detail Preservation:**  
  Extracts and preserves every detail from the original PDF resume, reorganizing and reformatting as needed without omitting any information.

- **Custom Tailoring:**  
  Incorporates industry- and role-specific keywords from the job description to highlight relevant skills and experiences.

- **Natural, Human Tone:**  
  Generates resumes and cover letters that read naturally, with subtle personal touches that help convey a unique professional identity.

- **Interactive Web Interface:**  
  Built using Gradio, the tool provides a user-friendly interface accessible through any modern browser, making it easy to generate customized documents on the go.

- **Facts & Tweaks System:**  
  Add persistent "facts" (truths about the user) and situational "tweaks" (instructions or preferences) that are injected into every generation. All facts/tweaks are stored in a SQLite database and can be edited at any time.

- **Persistent Job Submissions & Review Workflow:**  
  Every job application is stored in a database, including all inputs, outputs, and the state of the application (pending, approved, rejected, applied). Reviewers can view, edit, and regenerate any submission using the current facts/tweaks, and update the state and reviewer notes.

- **Job URL & State Tracking:**  
  Each submission includes a job URL (where to apply) and a workflow state. Reviewer notes can be added for each submission.

- **Recruiter/Company Selection:**  
  Specify whether the application is direct to the company or via a recruiter/agency. The cover letter prompt is adjusted accordingly.

- **Advanced Reviewer Workflow:**  
  Reviewers can:
  1. Open any submission for review
  2. View all details, resume, and cover letter
  3. Edit facts/tweaks
  4. Regenerate outputs with the latest facts/tweaks
  5. Approve, reject, or mark as applied

## Requirements

- **Python 3.x**
- **OpenAI API Key:**  
  Set up in your Colab environment's secrets under the label `"openai"` or in a `.env` file as `OPENAI_API_KEY`.
- **Python Libraries:**
  - `gradio`
  - `openai==0.28`
  - `PyPDF2`
  - `python-dotenv`
  - `sqlite3` (standard library)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/tailored-resume-bot.git
   cd tailored-resume-bot
   ```

2. **Setup:**

   - Place your OpenAI API key in a `.env` file as `OPENAI_API_KEY=...` or set it in Colab secrets as `openai`.
   - (Optional) Place default `cv.pdf` and `resume.pdf` in the project directory for quick reuse.

3. **Usage:**

- To launch the application:

  ```bash
  python tailored_resume_bot.py
  ```

- Open the provided URL in your browser to access the Gradio interface.

### Main Workflow

- **Job Description:** Paste the job description into the provided textbox.
- **Application Method:** Select whether you are applying direct to company or via recruiter/agency. If via recruiter, enter the recruiter/agency name.
- **Job URL:** Enter the URL where the job can be applied for.
- **Company Name/Job Title:** These are auto-extracted if possible, but can be entered manually.
- **Resume PDF:** Upload your PDF resume, or use the default if present.
- **Facts & Tweaks:** Add persistent facts and situational tweaks in the dedicated tab. These will be included in every generation.
- **Generate:** Click to generate a tailored resume/CV and cover letter. Download or view the results.

### Reviewer Workflow

- **Submissions Management Tab:**
  - View all previous submissions, including job details, resume, cover letter, state, and reviewer notes.
  - Select a submission to review all details.
  - Edit facts/tweaks as needed (in the Facts & Tweaks tab).
  - Regenerate resume/cover letter for any submission using the current facts/tweaks.
  - Update the state (pending, approved, rejected, applied) and reviewer notes.

### Facts & Tweaks Tab

- Add, edit, or delete persistent facts and situational tweaks.
- All changes are stored in SQLite and affect all future generations.

## Code Overview

- `tailored_resume_bot.py`: Main application logic, Gradio UI, and all backend features.
- `facts_tweaks.db`: SQLite database for facts, tweaks, and submissions.

## Advanced Features

- Regenerate any previous submission with the latest facts/tweaks.
- Reviewer workflow for approval and tracking.
- Recruiter/company selection for cover letter direction.
- Persistent, auditable job application history.

---

**For more details, see the code and in-app documentation.**
