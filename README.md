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

## Requirements

- **Python 3.x**
- **OpenAI API Key:**  
  Set up in your Colab environment’s secrets under the label `"openai"`.
- **Python Libraries:**
  - `gradio`
  - `openai==0.28`
  - `PyPDF2`

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/tailored-resume-bot.git
   cd tailored-resume-bot
