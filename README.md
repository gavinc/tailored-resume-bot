# Tailored Resume and Cover Letter Bot

This project is a bot that tailors resumes and cover letters based on user-provided job descriptions, company details, and an uploaded PDF resume. It leverages the OpenAI API and Gradio to generate outputs that are optimized for Applicant Tracking Systems (ATS) while still sounding naturally human.

## Features

- **ATS-Optimized Resume:** Generates plain text resumes with clear section headings and hyphenated bullet points.
- **Detail Preservation:** Extracts and preserves all information from the candidate's original PDF resume.
- **Humanized Tone:** Produces output with a natural, conversational tone and subtle personal touches.
- **Tailored Cover Letter:** Creates a cover letter that includes dynamic elements such as today's date and is fully customized to the job and company details.
- **Interactive Web UI:** Uses Gradio to provide a user-friendly interface.

## Requirements

- Python 3.x
- OpenAI API Key (set via Colab secrets with the label "openai")
- Python libraries:
  - `gradio`
  - `openai==0.28`
  - `PyPDF2`

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/tailored-resume-bot.git
   cd tailored-resume-bot
