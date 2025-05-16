# -*- coding: utf-8 -*-
"""
tailored-resume-bot

Supports both Google Colab and local/server execution:

- **Colab:**
    1. Before running, execute this in a separate cell:
        !pip install gradio openai==0.28 PyPDF2 python-dotenv
    2. Set your OpenAI API key in Colab secrets as 'openai'.

- **Local/Server:**
    1. Create a .env file with OPENAI_API_KEY=your-key
    2. Dependencies are managed via requirements.txt and python-dotenv is used for env loading.

This approach respects the original author's Colab-first intent, but allows local/server use as well.
"""

import os
import tempfile
import sqlite3

# Detect if running in Google Colab
try:
    import google.colab  # type: ignore
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    print("""
[INFO] Detected Google Colab environment.\n"
"If you see import errors, run this in a Colab cell first:\n"
"    !pip install gradio openai==0.28 PyPDF2 python-dotenv\n"
"""
    )
    openai_api_key = os.environ.get("openai")
else:
    from dotenv import load_dotenv
    load_dotenv()
    openai_api_key = os.environ.get("OPENAI_API_KEY")

import gradio as gr
import openai
import PyPDF2
import datetime
import json
import re

openai.api_key = openai_api_key

def init_db():
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, text TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tweaks (id INTEGER PRIMARY KEY, text TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        job_description TEXT,
        company_details TEXT,
        company_name TEXT,
        job_title TEXT,
        job_url TEXT,
        mode TEXT,
        tone TEXT,
        emphasis TEXT,
        facts TEXT,
        tweaks TEXT,
        resume_pdf_path TEXT,
        tailored_resume TEXT,
        cover_letter TEXT,
        notes TEXT,
        state TEXT DEFAULT 'pending',
        reviewer_notes TEXT
    )''')
    conn.commit()
    conn.close()

def get_facts():
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('SELECT text FROM facts')
    facts = [row[0] for row in c.fetchall()]
    conn.close()
    return facts

def get_tweaks():
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('SELECT text FROM tweaks')
    tweaks = [row[0] for row in c.fetchall()]
    conn.close()
    return tweaks

def add_fact(fact):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('INSERT INTO facts (text) VALUES (?)', (fact,))
    conn.commit()
    conn.close()

def add_tweak(tweak):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('INSERT INTO tweaks (text) VALUES (?)', (tweak,))
    conn.commit()
    conn.close()

def remove_fact(fact):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('DELETE FROM facts WHERE text = ?', (fact,))
    conn.commit()
    conn.close()

def remove_tweak(tweak):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('DELETE FROM tweaks WHERE text = ?', (tweak,))
    conn.commit()
    conn.close()

init_db()

def facts_tweaks_section():
    facts = get_facts()
    tweaks = get_tweaks()
    facts_str = '\n'.join(f'- {f}' for f in facts) if facts else '(none)'
    tweaks_str = '\n'.join(f'- {t}' for t in tweaks) if tweaks else '(none)'
    return f"FACTS (persistent):\n{facts_str}\n\nTWEAKS (situational):\n{tweaks_str}"

def update_facts_tweaks_display():
    return facts_tweaks_section()

def add_fact_ui(fact):
    if fact.strip():
        add_fact(fact.strip())
    return update_facts_tweaks_display()

def add_tweak_ui(tweak):
    if tweak.strip():
        add_tweak(tweak.strip())
    return update_facts_tweaks_display()

def remove_fact_ui(fact):
    remove_fact(fact)
    return update_facts_tweaks_display()

def remove_tweak_ui(tweak):
    remove_tweak(tweak)
    return update_facts_tweaks_display()

def extract_text_from_pdf(pdf_file):
    # Check if pdf_file is a file-like object (has a seek method)
    if not hasattr(pdf_file, "seek"):
        # If it's a path-like string, open it as a binary file.
        with open(pdf_file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    else:
        # Use the file-like object directly.
        pdf_file.seek(0)  # Reset file pointer to the beginning
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

def estimate_token_count(*args):
    # Simple token estimation: 1 token ≈ 4 chars (for English)
    total_chars = sum(len(str(a)) for a in args)
    return total_chars // 4

def split_outputs(llm_output):
    # Naive split: look for 'COVER LETTER' or similar divider
    if 'COVER LETTER' in llm_output:
        parts = llm_output.split('COVER LETTER', 1)
        resume = parts[0].strip()
        cover_letter = 'COVER LETTER' + parts[1].strip()
        return resume, cover_letter
    return llm_output, ''

def get_default_pdf_file(mode):
    # Return the default file path for the selected mode
    if mode == "CV" and os.path.exists("cv.pdf"):
        return "cv.pdf"
    elif mode == "Resume" and os.path.exists("resume.pdf"):
        return "resume.pdf"
    return None

def store_submission(job_description, company_details, company_name, job_title, job_url, mode, tone, emphasis, facts, tweaks, resume_pdf_path, tailored_resume, cover_letter, notes=None, state='pending', reviewer_notes=None):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('''INSERT INTO submissions (timestamp, job_description, company_details, company_name, job_title, job_url, mode, tone, emphasis, facts, tweaks, resume_pdf_path, tailored_resume, cover_letter, notes, state, reviewer_notes)
                 VALUES (datetime('now'),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
              (job_description, company_details, company_name, job_title, job_url, mode, tone, emphasis, json.dumps(facts), json.dumps(tweaks), resume_pdf_path, tailored_resume, cover_letter, notes, state, reviewer_notes))
    conn.commit()
    conn.close()

def extract_company_and_title_from_llm(llm_output):
    # Look for a JSON block in the LLM output
    match = re.search(r'\{\s*"company_name"\s*:\s*"(.*?)"\s*,\s*"job_title"\s*:\s*"(.*?)"\s*\}', llm_output, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def tailor_application_pdf(job_desc, company_details, pdf_file, tone, emphasis, mode, company_name, job_title, job_url):
    import time
    # If no file uploaded, use the default for the selected mode
    if pdf_file is None:
        default_path = get_default_pdf_file(mode)
        if default_path:
            pdf_file = default_path
    resume_text = extract_text_from_pdf(pdf_file)
    facts = get_facts()
    tweaks = get_tweaks()
    facts_tweaks_str = ''
    if facts:
        facts_tweaks_str += 'FACTS (persistent):\n' + '\n'.join(f'- {f}' for f in facts) + '\n'
    if tweaks:
        facts_tweaks_str += 'TWEAKS (situational):\n' + '\n'.join(f'- {t}' for t in tweaks) + '\n'
    prompt_base = f"Job Description:\n{job_desc}\nCompany Details:\n{company_details}\nResume:\n{resume_text}\n{facts_tweaks_str}"
    token_est = estimate_token_count(prompt_base)
    if token_est > 6000:
        yield (None, None, None, None, None, f"[Warning] Your input may exceed the model's context window. Please shorten your resume or job description.")
        return
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    resume_prompt = f"""
You are an expert career advisor with extensive experience in crafting resumes and CVs that are optimized for Applicant Tracking Systems (ATS), while sounding naturally human-written. The candidate has provided their full resume, and it is essential that every detail is preserved in the final tailored version. Do not omit or shorten any information; instead, reorganize and reformat it if necessary to meet ATS standards.

Tone: {tone}
Section Emphasis: {emphasis}
Mode: {mode}

{facts_tweaks_str}
Sample Output Format:
====================
{mode.upper()}
[...]
====================

Based on the details provided below, please generate a tailored {mode.lower()} that:
- Is in plain text with clear, capitalized section headings (e.g., PROFESSIONAL SUMMARY, EDUCATION, EXPERIENCE, SKILLS).
- Uses hyphenated bullet points for lists.
- Incorporates industry- and role-specific keywords from the job description.
- Reads as if it were written by a human, using a {tone} tone with subtle personal touches.
- **Preserves all the information from the candidate's original resume without omitting any details.**
- Emphasizes: {emphasis}
- For CV mode, include all possible details and extended sections (e.g., publications, presentations, research, etc.)

Here are the details:

Job Description:
{job_desc}

Company Details:
{company_details}

Candidate's Current Resume:
{resume_text}

Generate a tailored {mode.lower()} that meets all the above requirements.
"""
    try:
        model = "gpt-4o" if "gpt-4o" in openai.Model.list().data else "gpt-3.5-turbo"
        print(f"[DEBUG] Using model: {model}")
        print(f"[DEBUG] Resume prompt sent to LLM:\n{resume_prompt[:1000]}...\n[truncated]")
        resume_response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert career advisor."},
                {"role": "user", "content": resume_prompt}
            ],
            max_tokens=1800,
            temperature=0.7
        )
        tailored_resume = resume_response.choices[0].message.content.strip()
        print(f"[DEBUG] Tailored resume/CV (first 1000 chars):\n{tailored_resume[:1000]}...\n[truncated]")
        resume_file = tempfile.NamedTemporaryFile(delete=False, suffix="_resume.txt", mode="w", encoding="utf-8")
        resume_file.write(tailored_resume)
        resume_file.close()
        yield (tailored_resume, None, resume_file.name, None, None, None)
        # --- Second API call: Generate Cover Letter ---
        # Ask for structured output for company_name and job_title
        cover_prompt = f"""
You are an expert career advisor. Write a complete, ATS-friendly cover letter in plain text, tailored to the job description and company details below. Use the candidate's tailored {mode.lower()} as a reference for skills, experience, and achievements to highlight. The cover letter should:
- Start with the candidate's contact information.
- Include today's date ({current_date}) in place of any placeholder.
- Use a {tone}, engaging tone—avoid overly formal or mechanical language.
- Be fully tailored to the job description and company details.
- Reference and align with the tailored {mode.lower()} provided.
- At the top of your response, output a JSON object with the following fields: company_name, job_title, extracted from the job description if possible. Example: {"company_name": "Acme Corp", "job_title": "Senior Data Scientist"}

{facts_tweaks_str}
Job Description:
{job_desc}

Company Details:
{company_details}

Tailored {mode}:
{tailored_resume}

Generate a complete cover letter that meets all the above requirements.
"""
        print(f"[DEBUG] Cover letter prompt sent to LLM:\n{cover_prompt[:1000]}...\n[truncated]")
        cover_response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert career advisor."},
                {"role": "user", "content": cover_prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )
        cover_letter_full = cover_response.choices[0].message.content.strip()
        print(f"[DEBUG] Cover letter (first 1000 chars):\n{cover_letter_full[:1000]}...\n[truncated]")
        # Try to extract company_name and job_title from the LLM output
        extracted_company, extracted_title = extract_company_and_title_from_llm(cover_letter_full)
        # If not found, use user input or prompt for it
        final_company = extracted_company or company_name
        final_title = extracted_title or job_title
        if not final_company or not final_title:
            # Prompt user to enter missing info (handled in UI)
            yield (tailored_resume, None, resume_file.name, None, None, f"[Action Required] Please enter missing company name and/or job title.")
            return
        # Remove the JSON block from the cover letter before saving/displaying
        cover_letter = re.sub(r'^\{.*?\}\s*', '', cover_letter_full, flags=re.DOTALL)
        cover_file = tempfile.NamedTemporaryFile(delete=False, suffix="_cover_letter.txt", mode="w", encoding="utf-8")
        cover_file.write(cover_letter)
        cover_file.close()
        # Store submission
        store_submission(job_desc, company_details, final_company, final_title, job_url, mode, tone, emphasis, facts, tweaks, str(pdf_file), tailored_resume, cover_letter)
        yield (tailored_resume, cover_letter, resume_file.name, cover_file.name, None, None)
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in tailor_application_pdf: {e}")
        traceback.print_exc()
        yield (None, None, None, None, None, f"[Error] {str(e)}")

def get_facts_with_ids():
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('SELECT id, text FROM facts')
    facts = c.fetchall()
    conn.close()
    return facts

def get_tweaks_with_ids():
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('SELECT id, text FROM tweaks')
    tweaks = c.fetchall()
    conn.close()
    return tweaks

def edit_fact(fact_id, new_text):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('UPDATE facts SET text = ? WHERE id = ?', (new_text, fact_id))
    conn.commit()
    conn.close()

def edit_tweak(tweak_id, new_text):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('UPDATE tweaks SET text = ? WHERE id = ?', (new_text, tweak_id))
    conn.commit()
    conn.close()

def facts_tweaks_advanced_ui():
    facts = get_facts_with_ids()
    tweaks = get_tweaks_with_ids()
    facts_display = [f"{fid}: {text}" for fid, text in facts]
    tweaks_display = [f"{tid}: {text}" for tid, text in tweaks]
    return facts_display, tweaks_display

def add_fact_advanced(fact):
    if fact.strip():
        add_fact(fact.strip())
    return facts_tweaks_advanced_ui()

def add_tweak_advanced(tweak):
    if tweak.strip():
        add_tweak(tweak.strip())
    return facts_tweaks_advanced_ui()

def delete_fact_advanced(fact_id):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('DELETE FROM facts WHERE id = ?', (fact_id,))
    conn.commit()
    conn.close()
    return facts_tweaks_advanced_ui()

def delete_tweak_advanced(tweak_id):
    conn = sqlite3.connect('facts_tweaks.db')
    c = conn.cursor()
    c.execute('DELETE FROM tweaks WHERE id = ?', (tweak_id,))
    conn.commit()
    conn.close()
    return facts_tweaks_advanced_ui()

def edit_fact_advanced(fact_id, new_text):
    edit_fact(fact_id, new_text)
    return facts_tweaks_advanced_ui()

def edit_tweak_advanced(tweak_id, new_text):
    edit_tweak(tweak_id, new_text)
    return facts_tweaks_advanced_ui()

# --- Gradio UI for facts/tweaks management ---
facts_input = gr.Textbox(label="Add Fact (persistent)")
tweaks_input = gr.Textbox(label="Add Tweak (situational)")
facts_list = gr.Dataframe(headers=["ID", "Fact"], datatype=["number", "str"], label="Facts List", interactive=True)
tweaks_list = gr.Dataframe(headers=["ID", "Tweak"], datatype=["number", "str"], label="Tweaks List", interactive=True)

with gr.Blocks() as demo:
    gr.Markdown("## ATS-Optimized Resume & CV Tailoring Bot with Facts & Tweaks")
    with gr.Tab("Resume/CV & Cover Letter"):
        job_desc = gr.Textbox(lines=10, placeholder="Paste the job description here...", label="Job Description")
        company_details_mode = gr.Radio(["Direct to Company", "Via Recruiter/Agency"], value="Direct to Company", label="Application Method")
        recruiter_name = gr.Textbox(lines=1, placeholder="Recruiter/Agency Name (if applicable)", label="Recruiter/Agency Name", visible=False)
        def toggle_recruiter_field(method):
            return gr.update(visible=(method == "Via Recruiter/Agency"))
        company_details_mode.change(toggle_recruiter_field, inputs=company_details_mode, outputs=recruiter_name)
        # Hidden textbox to hold computed company_details
        company_details = gr.Textbox(visible=False)
        def company_details_value(method, recruiter):
            if method == "Via Recruiter/Agency" and recruiter.strip():
                return f"Via recruiter/agency: {recruiter.strip()}"
            return "Direct to company"
        # Update company_details whenever mode or recruiter changes
        company_details_mode.change(company_details_value, inputs=[company_details_mode, recruiter_name], outputs=company_details)
        recruiter_name.change(company_details_value, inputs=[company_details_mode, recruiter_name], outputs=company_details)
        pdf_file = gr.File(label="Upload Resume PDF")
        tone = gr.Radio(["Formal", "Friendly", "Conversational"], value="Formal", label="Tone")
        emphasis = gr.Textbox(lines=2, placeholder="e.g. Skills, Experience", label="Section Emphasis (comma-separated)")
        mode = gr.Radio(["Resume", "CV"], value="Resume", label="Mode (Resume or CV)")
        job_url = gr.Textbox(lines=1, placeholder="Enter job URL...", label="Job URL")
        company_name = gr.Textbox(lines=1, placeholder="Company name (auto-extracted if possible)", label="Company Name (optional)")
        job_title = gr.Textbox(lines=1, placeholder="Job title (auto-extracted if possible)", label="Job Title (optional)")
        run_btn = gr.Button("Generate Resume/CV & Cover Letter")
        resume_out = gr.Textbox(label="Tailored Resume/CV (view)")
        cover_out = gr.Textbox(label="Cover Letter (view)")
        resume_file_out = gr.File(label="Download Tailored Resume (.txt)")
        cover_file_out = gr.File(label="Download Cover Letter (.txt)")
        warn_out = gr.Textbox(label="Warnings or Errors")
        run_btn.click(
            tailor_application_pdf,
            inputs=[job_desc, company_details, pdf_file, tone, emphasis, mode, company_name, job_title, job_url],
            outputs=[resume_out, cover_out, resume_file_out, cover_file_out, warn_out],
            api_name="generate"
        )
    with gr.Tab("Facts & Tweaks Management"):
        gr.Markdown("### Manage your persistent facts and situational tweaks.")
        with gr.Row():
            facts_input.render()
            add_fact_btn = gr.Button("Add Fact")
        with gr.Row():
            tweaks_input.render()
            add_tweak_btn = gr.Button("Add Tweak")
        facts_list.render()
        tweaks_list.render()
        # Buttons for delete/edit
        del_fact_id = gr.Number(label="Delete Fact by ID")
        del_fact_btn = gr.Button("Delete Fact")
        edit_fact_id = gr.Number(label="Edit Fact ID")
        edit_fact_text = gr.Textbox(label="New Fact Text")
        edit_fact_btn = gr.Button("Edit Fact")
        del_tweak_id = gr.Number(label="Delete Tweak by ID")
        del_tweak_btn = gr.Button("Delete Tweak")
        edit_tweak_id = gr.Number(label="Edit Tweak ID")
        edit_tweak_text = gr.Textbox(label="New Tweak Text")
        edit_tweak_btn = gr.Button("Edit Tweak")
        # Bindings
        add_fact_btn.click(add_fact_advanced, inputs=facts_input, outputs=[facts_list, tweaks_list])
        add_tweak_btn.click(add_tweak_advanced, inputs=tweaks_input, outputs=[facts_list, tweaks_list])
        del_fact_btn.click(delete_fact_advanced, inputs=del_fact_id, outputs=[facts_list, tweaks_list])
        del_tweak_btn.click(delete_tweak_advanced, inputs=del_tweak_id, outputs=[facts_list, tweaks_list])
        edit_fact_btn.click(edit_fact_advanced, inputs=[edit_fact_id, edit_fact_text], outputs=[facts_list, tweaks_list])
        edit_tweak_btn.click(edit_tweak_advanced, inputs=[edit_tweak_id, edit_tweak_text], outputs=[facts_list, tweaks_list])
        # Initial display
        facts_list.value, tweaks_list.value = facts_tweaks_advanced_ui()
    # Submissions management tab
    with gr.Tab("Submissions Management"):
        gr.Markdown("### Review and manage all job submissions.")
        submissions_table = gr.Dataframe(headers=["ID", "Timestamp", "Job Title", "Company Name", "Job URL", "State", "Reviewer Notes"], datatype=["number", "str", "str", "str", "str", "str", "str"], label="Submissions", interactive=False)
        refresh_btn = gr.Button("Refresh Submissions List")
        # State and notes editing controls
        edit_id = gr.Number(label="Submission ID to Edit")
        new_state = gr.Dropdown(choices=["pending", "approved", "rejected", "applied"], label="Set State")
        reviewer_notes = gr.Textbox(lines=2, label="Reviewer Notes")
        update_btn = gr.Button("Update State/Notes")
        # Submission detail/review section
        detail_id = gr.Number(label="Submission ID to Review")
        load_detail_btn = gr.Button("Load Submission Details")
        detail_job_desc = gr.Textbox(label="Job Description", interactive=False)
        detail_company_details = gr.Textbox(label="Company Details", interactive=False)
        detail_job_url = gr.Textbox(label="Job URL", interactive=False)
        detail_company_name = gr.Textbox(label="Company Name", interactive=False)
        detail_job_title = gr.Textbox(label="Job Title", interactive=False)
        detail_mode = gr.Textbox(label="Mode", interactive=False)
        detail_tone = gr.Textbox(label="Tone", interactive=False)
        detail_emphasis = gr.Textbox(label="Emphasis", interactive=False)
        detail_resume = gr.Textbox(label="Tailored Resume/CV (view)", interactive=False)
        detail_cover = gr.Textbox(label="Cover Letter (view)", interactive=False)
        # Facts/tweaks display and edit
        gr.Markdown("#### Current Facts & Tweaks (edit in Facts & Tweaks tab)")
        facts_display = gr.Textbox(label="Facts", value="", interactive=False)
        tweaks_display = gr.Textbox(label="Tweaks", value="", interactive=False)
        # Regenerate button
        regen_btn = gr.Button("Regenerate Resume/CV & Cover Letter with Current Facts/Tweaks")
        regen_warn = gr.Textbox(label="Warnings or Errors (regen)")
        # Helper functions
        def fetch_submissions():
            conn = sqlite3.connect('facts_tweaks.db')
            c = conn.cursor()
            c.execute('SELECT id, timestamp, job_title, company_name, job_url, state, reviewer_notes FROM submissions ORDER BY timestamp DESC')
            rows = c.fetchall()
            conn.close()
            return rows
        def update_submission_state_and_notes(sub_id, state, notes):
            conn = sqlite3.connect('facts_tweaks.db')
            c = conn.cursor()
            c.execute('UPDATE submissions SET state = ?, reviewer_notes = ? WHERE id = ?', (state, notes, int(sub_id)))
            conn.commit()
            conn.close()
            return fetch_submissions()
        def load_submission_detail(sub_id):
            conn = sqlite3.connect('facts_tweaks.db')
            c = conn.cursor()
            c.execute('SELECT job_description, company_details, job_url, company_name, job_title, mode, tone, emphasis, tailored_resume, cover_letter FROM submissions WHERE id = ?', (int(sub_id),))
            row = c.fetchone()
            conn.close()
            if row:
                return row + (get_facts(), get_tweaks(), "")
            return ("", "", "", "", "", "", "", "", "", "", [], [], "[Error] Submission not found.")
        def regen_submission(sub_id):
            # Load original fields
            conn = sqlite3.connect('facts_tweaks.db')
            c = conn.cursor()
            c.execute('SELECT job_description, company_details, job_url, company_name, job_title, mode, tone, emphasis, resume_pdf_path FROM submissions WHERE id = ?', (int(sub_id),))
            row = c.fetchone()
            conn.close()
            if not row:
                return ("", "", "[Error] Submission not found.")
            job_desc, company_details, job_url, company_name, job_title, mode, tone, emphasis, resume_pdf_path = row
            # Use current facts/tweaks
            facts = get_facts()
            tweaks = get_tweaks()
            # Regenerate using the same function as main UI
            gen = tailor_application_pdf(job_desc, company_details, resume_pdf_path, tone, emphasis, mode, company_name, job_title, job_url)
            # Get final result (streaming not needed here)
            last = None
            for result in gen:
                last = result
            if last:
                resume, cover, _, _, warn, *_ = last + (None,) * (6 - len(last))
                # Optionally, update the DB with new outputs
                conn = sqlite3.connect('facts_tweaks.db')
                c = conn.cursor()
                c.execute('UPDATE submissions SET tailored_resume = ?, cover_letter = ? WHERE id = ?', (resume, cover, int(sub_id)))
                conn.commit()
                conn.close()
                return (resume, cover, warn)
            return ("", "", "[Error] Regeneration failed.")
        refresh_btn.click(lambda: fetch_submissions(), outputs=submissions_table)
        update_btn.click(update_submission_state_and_notes, inputs=[edit_id, new_state, reviewer_notes], outputs=submissions_table)
        load_detail_btn.click(load_submission_detail, inputs=detail_id, outputs=[detail_job_desc, detail_company_details, detail_job_url, detail_company_name, detail_job_title, detail_mode, detail_tone, detail_emphasis, detail_resume, detail_cover, facts_display, tweaks_display, regen_warn])
        regen_btn.click(regen_submission, inputs=detail_id, outputs=[detail_resume, detail_cover, regen_warn])
        # Initial display
        submissions_table.value = fetch_submissions()

demo.launch(share=True, debug=True, server_name='0.0.0.0')