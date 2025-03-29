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

2. **Setup:**

Make sure your OpenAI API key is stored securely in your Colab environment’s secrets with the label "openai". The project is set up to load the key automatically.

3. **Usage:**

- To launch the application:
Run the Main Script python tailor_application.py

After running the script, a shareable URL will be provided. Open the URL in your browser to access the Gradio interface.

Job Description: Paste the job description into the provided textbox.

Company Details: Enter the details about the company.

Resume PDF: Upload your PDF resume.

Once you submit the form, the tool will generate a tailored resume and a complete cover letter based on the provided inputs.

4. **Run in Google Colab:**
You can also try the project directly in Google Colab. Click the link below to open the notebook:

[Run in Google Colab](https://colab.research.google.com/drive/1ACShlegW1IR-4TSE2bfI1Wz_-gAsvUlv?usp=sharing) 

5. **Code Overview:**
tailor_application.py:
Contains the main function tailor_application_pdf, which:

Uses PyPDF2 to extract text from a PDF resume.

Constructs a detailed prompt for the OpenAI API.

Generates a tailored resume and cover letter that meet the ATS and human-readability requirements.

Gradio Interface:
Provides a simple and intuitive web interface for user inputs and displays the generated output.
