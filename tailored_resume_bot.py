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

openai.api_key = openai_api_key

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

def tailor_application_pdf(job_desc, company_details, pdf_file):
    # Extract text from the uploaded PDF resume
    resume_text = extract_text_from_pdf(pdf_file)

    # Get the current date for insertion in the cover letter
    current_date = datetime.datetime.now().strftime("%B %d, %Y")

    # Construct an enhanced prompt with humanization and detail-preservation instructions
    prompt = f"""
    You are an expert career advisor with extensive experience in crafting resumes and cover letters that are optimized for Applicant Tracking Systems (ATS), while sounding naturally human-written. The candidate has provided their full resume, and it is essential that every detail is preserved in the final tailored version. Do not omit or shorten any information; instead, reorganize and reformat it if necessary to meet ATS standards.

    Based on the details provided below, please generate:

    1. A tailored resume that:
       - Is in plain text with clear, capitalized section headings (e.g., PROFESSIONAL SUMMARY, EDUCATION, EXPERIENCE, SKILLS).
       - Uses hyphenated bullet points for lists.
       - Incorporates industry- and role-specific keywords from the job description.
       - Reads as if it were written by a human, using a natural, conversational tone with subtle personal touches.
       - **Preserves all the information from the candidate's original resume without omitting any details.**

    2. A complete cover letter that:
       - Is ATS-friendly and in plain text.
       - Starts with the candidate's contact information.
       - Includes today's date ({current_date}) in place of any placeholder.
       - Uses a human, engaging tone—avoid overly formal or mechanical language.
       - Is fully tailored to the job description and company details.

    Here are the details:

    Job Description:
    {job_desc}

    Company Details:
    {company_details}

    Candidate's Current Resume:
    {resume_text}

    Generate a tailored resume and a complete cover letter that meet all the above requirements.
    """

    # Call the OpenAI Chat API using the new prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert career advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1200,  # Increase token count if needed to capture more details
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

iface = gr.Interface(
    fn=tailor_application_pdf,
    inputs=[
        gr.Textbox(lines=10, placeholder="Paste the job description here...", label="Job Description"),
        gr.Textbox(lines=5, placeholder="Enter company details...", label="Company Details"),
        gr.File(label="Upload Resume PDF")
    ],
    outputs=gr.Textbox(label="Tailored Resume & Cover Letter"),
    title="ATS-Optimized Resume Tailoring Bot",
    description="Upload your resume PDF along with job and company details. The bot will extract your resume text and generate a tailored, ATS-friendly resume and cover letter that incorporates industry keywords."
)

iface.launch(share=True, debug=True, server_name='0.0.0.0')