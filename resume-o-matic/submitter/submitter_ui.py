import gradio as gr
from facts_tweaks import (
    list_corrections, create_correction, edit_correction, remove_correction
)
from llm import LLMClient
import datetime
import PyPDF2
import markdown2
import os
import json
import re
import socket
from submission import create_submission

print = lambda *args, **kwargs: __import__('builtins').print(f"[submitter_ui.py {datetime.datetime.now()}]", *args, **kwargs)

def extract_text_from_pdf(pdf_file, mode):
    if not pdf_file:
        fallback = "cv.pdf" if mode == "CV" and os.path.exists("cv.pdf") else "resume.pdf"
        if os.path.exists(fallback):
            pdf_file = fallback
    if not pdf_file:
        return ""
    if not hasattr(pdf_file, "seek") and isinstance(pdf_file, str):
        with open(pdf_file, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    else:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

def build_prompt(job_desc, app_type, recruiter_name, resume_mode, resume_text, corrections, target):
    app_details = f"Application Type: {app_type}"
    if app_type == "Via Recruiter/Agency" and recruiter_name.strip():
        app_details += f" (Recruiter: {recruiter_name.strip()})"
    if target == 'resume':
        prompt = f"""
You are an expert career advisor and resume writer. Given the following job description and resume text, generate a tailored resume in markdown format. Extract the job title and company name from the job description. Return ONLY a JSON object with this structure (no commentary):
{{
  \"job_title\": \"<clean job title>\",
  \"company_name\": \"<clean company name>\",
  \"resume\": \"<markdown resume text>\"
}}
Job Description:\n{job_desc}\n\n{app_details}\n\nResume Text:\n{resume_text}\n\nMode: {resume_mode}\n"""
        if corrections:
            prompt += f"\n---\nPersistent Corrections for resume (apply these to your output):\n"
            for corr in corrections:
                prompt += f"Section: {corr[1]}\nReplace: {corr[2]}\nWith: {corr[3]}\n\n"
        prompt += "\nReturn only the JSON object."
        return prompt
    else:
        prompt = f"""
You are an expert career advisor and cover letter writer. Given the following job description and tailored resume, generate a tailored cover letter in markdown format. Extract the job title and company name from the job description. Return ONLY a JSON object with this structure (no commentary):
{{
  \"job_title\": \"<clean job title>\",
  \"company_name\": \"<clean company name>\",
  \"cover_letter\": \"<markdown cover letter text>\"
}}
Job Description:\n{job_desc}\n\nTailored Resume (markdown):\n{resume_text}\n\nMode: {resume_mode}\n"""
        if corrections:
            prompt += f"\n---\nPersistent Corrections for cover letter (apply these to your output):\n"
            for corr in corrections:
                prompt += f"Section: {corr[1]}\nReplace: {corr[2]}\nWith: {corr[3]}\n\n"
        prompt += "\nReturn only the JSON object."
        return prompt

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def highlight_corrections(text, corrections):
    for corr in corrections:
        orig = corr[2]
        if orig and orig in text:
            text = text.replace(orig, f'<mark style="background: #ffe066;">{orig}</mark>')
    return text

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## ATS-Optimized Resume & CV Tailoring Bot v2 (Submitter)")
        with gr.Column():
            gr.Markdown("### Submit a Job for Resume/CV Tailoring")
            job_desc = gr.Textbox(lines=8, label="Job Description", placeholder="Paste the job description here...")
            job_url = gr.Textbox(lines=1, label="Job URL (link to job posting)", placeholder="https://example.com/job123")
            app_type = gr.Radio(["Direct to Company", "Via Recruiter/Agency"], value="Direct to Company", label="Application Type")
            recruiter_name = gr.Textbox(label="Recruiter/Agency Name (if applicable)", visible=False)
            def toggle_recruiter_field(method):
                return gr.update(visible=(method == "Via Recruiter/Agency"))
            app_type.change(toggle_recruiter_field, inputs=app_type, outputs=recruiter_name)
            resume_mode = gr.Radio(["Resume", "CV"], value="Resume", label="Mode (Resume or CV)")
            resume_file = gr.File(label="Upload Resume/CV PDF")
            generate_btn = gr.Button("Generate Resume/CV & Cover Letter")

        with gr.Tabs() as output_tabs:
            with gr.TabItem("Resume/CV"):
                resume_html = gr.HTML(label="Tailored Resume/CV Output (right-click selected text to correct)")
                corrections_table_r = gr.Dataframe(headers=["ID", "Section", "Original", "Corrected", "Context", "Timestamp"], datatype=["number", "str", "str", "str", "str", "str"], label="Resume/CV Corrections", interactive=False, value=[c for c in list_corrections() if c[4] == 'resume'])
            with gr.TabItem("Cover Letter"):
                cover_html = gr.HTML(label="Tailored Cover Letter Output (right-click selected text to correct)")
                corrections_table_c = gr.Dataframe(headers=["ID", "Section", "Original", "Corrected", "Context", "Timestamp"], datatype=["number", "str", "str", "str", "str", "str"], label="Cover Letter Corrections", interactive=False, value=[c for c in list_corrections() if c[4] == 'cover'])

        correction_bridge = gr.Textbox(visible=False)

        def generate_llm_outputs(job_desc, job_url, app_type, recruiter_name, resume_mode, resume_file):
            resume_text = extract_text_from_pdf(resume_file, resume_mode)
            corrections_r = [c for c in list_corrections() if c[4] == 'resume']
            prompt_resume = build_prompt(job_desc, app_type, recruiter_name, resume_mode, resume_text, corrections_r, target='resume')
            print("Prompt sent to LLM (Resume):\n", prompt_resume[:1000], "... [truncated]")
            try:
                resume_raw = LLMClient().generate_resume(prompt_resume)
                cleaned_resume_raw = extract_json(resume_raw)
                resume_json = json.loads(cleaned_resume_raw)
                job_title = resume_json.get('job_title', '').strip()
                company_name = resume_json.get('company_name', '').strip()
                resume_md = resume_json.get('resume', '').strip()
            except Exception as e:
                print(f"[ERROR] LLM resume JSON parsing failed: {e}\nRaw output: {resume_raw if 'resume_raw' in locals() else ''}")
                return f"[ERROR] Resume LLM output not in expected JSON format: {e}\nRaw output: {resume_raw if 'resume_raw' in locals() else ''}", "", [], []
            corrections_c = [c for c in list_corrections() if c[4] == 'cover']
            prompt_cover = build_prompt(job_desc, app_type, recruiter_name, resume_mode, resume_md, corrections_c, target='cover')
            print("Prompt sent to LLM (Cover Letter):\n", prompt_cover[:1000], "... [truncated]")
            try:
                cover_raw = LLMClient().generate_cover_letter(prompt_cover)
                cleaned_cover_raw = extract_json(cover_raw)
                cover_json = json.loads(cleaned_cover_raw)
                cover_letter_md = cover_json.get('cover_letter', '').strip()
            except Exception as e:
                print(f"[ERROR] LLM cover letter JSON parsing failed: {e}\nRaw output: {cover_raw if 'cover_raw' in locals() else ''}")
                return f"[ERROR] Cover Letter LLM output not in expected JSON format: {e}\nRaw output: {cover_raw if 'cover_raw' in locals() else ''}", "", [], []
            # Store submission with job_url
            create_submission(
                timestamp=datetime.datetime.now().isoformat(),
                job_description=job_desc,
                job_url=job_url,
                company_name=company_name,
                job_title=job_title,
                mode=resume_mode,
                tailored_resume=resume_md,
                cover_letter=cover_letter_md,
                state='pending'
            )
            resume_html_out = highlight_corrections(markdown2.markdown(resume_md), corrections_r)
            cover_html_out = highlight_corrections(markdown2.markdown(cover_letter_md), corrections_c)
            return resume_html_out, cover_html_out, [c for c in list_corrections() if c[4] == 'resume'], [c for c in list_corrections() if c[4] == 'cover']

        generate_btn.click(
            generate_llm_outputs,
            inputs=[job_desc, job_url, app_type, recruiter_name, resume_mode, resume_file],
            outputs=[resume_html, cover_html, corrections_table_r, corrections_table_c]
        )

        gr.Markdown("---")
        reviewer_url = "https://reviewer.gavincowie.com"
        gr.HTML(f'''<button onclick="window.location.href='{reviewer_url}'" style="font-size:1.1em;padding:0.5em 1em;">Go to Submissions Management & Review App</button>''')

    return demo

def main():
    demo = build_ui()
    demo.launch(server_name='0.0.0.0', server_port=7960)

if __name__ == '__main__':
    main() 