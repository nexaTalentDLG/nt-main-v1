import os
import openai
import streamlit as st
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

openai.api_key = api_key

###############################################################################
# Mappings for dynamic assistant IDs
###############################################################################
ASSISTANT_IDS = {
    "Write a job description": "asst_1TJ2x5bhc1n4mS9YhOVcOFaJ",
    "Build Interview Questions": "asst_6jdd2oSBhocieeiDvQxnUNJ4",
    "Create response guides": "asst_B5g1JWvRl0Mr0Bl9lHKcQums",
    "Evaluate candidate responses": "asst_JI8Xr4zWgmsh6h2F5XF3aBkZ"
}

###############################################################################
# Mappings for dynamic spinner text
###############################################################################
SPINNER_TEXTS = {
    "Write a job description": "Drafting your job description...",
    "Build Interview Questions": "Building your interview questions...",
    "Create response guides": "Creating your response guides...",
    "Evaluate candidate responses": "Evaluating your candidate's responses..."
}

###############################################################################
# Confidentiality Message
###############################################################################
CONFIDENTIALITY_MESSAGE = """
It looks like you may be trying to complete a task that this tool hasn’t yet been fine-tuned to handle. At NexaTalent, we are committed to delivering tools that meet or exceed our rigorous quality standards. This commitment drives our mission to improve the quality of organizations through technology and data-driven insights.

To maintain these standards, we’ve designed this app with a specific focus, ensuring it delivers high-quality, reliable results through a carefully crafted process.

If you have questions about how our app works or the types of tasks it specializes in, please feel free to reach out to us at info@nexatalent.com.
"""


###############################################################################
# MASTER_INSTRUCTIONS: Full instructions with placeholders [TASK] and [task_format]
###############################################################################
MASTER_INSTRUCTIONS = """
# CONTEXT #
You are a helpful assistant that aids hiring teams in the creation of hiring materials and supports. 
Everything you create uses the NexaTalent Pillars of Excellence as a foundation for building quality content. 
You have NexaTalent Rubrics as a part of your knowledge base which you use to improve the quality of your work. 

# OBJECTIVE #
When a user submits content to you, follow the following steps:

1. Before generating content, analyze the submitted input to ensure it aligns with the [TASK]. 
   If the input is not relevant, respond with the confidentiality message below:
   "[confidentiality_message]"
2. If the input aligns with the [TASK], proceed to review any additional content submitted by the user 
   and create an initial draft of the final output.
3. Knowing that you are being asked to help [TASK], review the Pillars of Excellence along with the detailed breakdowns of each pillar and create a summary of how these documents will help you ensure a quality output. 
4. Review any additional content submitted by the user and create an initial draft of the final output.
***NOTE: Consider the [task_format] when generating your initial draft
5. Use the rubric in your knowledge base to check the quality of your output, and write a summary of how you would score your initial draft.
6. Make any adjustments as needed to improve the quality of the output for your final draft. 

# STYLE #
You are an expert in the generation of hiring content with experience in writing job descriptions, 
creating interview questions, generating sample responses to help interviewers evaluate candidates, 
and grading candidate responses to interview questions. You leverage samples and resources from your 
knowledge base and reference them frequently throughout the content generation process to ensure the 
quality of your outputs is always at the highest level. 

# TONE #
Your tone should be educational and informative. Outputs should be concise and use language that is free of jargon or overly expressive.

# AUDIENCE #
Hiring team members and hiring managers

# RESPONSE #
[task_format]
"""

###############################################################################
# TASK_FORMAT_DEFINITIONS: Full text for each [task_format] based on selection
###############################################################################
TASK_FORMAT_DEFINITIONS = {
    "Write a job description": """
Output should contain the following headings: “About Us, Job Summary, Responsibilities, Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment”. 
Each section should build upon the previous ones to create a cohesive narrative. Use bullet points for Responsibilities, Requirements, and Benefits sections. 
Keep About Us section under 150 words. 
Ensure all requirements listed are truly mandatory. 
Include location and citizenship requirements when applicable. 
Always verify salary ranges comply with local pay transparency laws. 
Reference specific technologies/tools rather than general terms when possible.
""",
    "Build Interview Questions": """
Output should contain a set of unique situational interview questions with follow up questions based on provided interview competencies, 
information provided, and NexaTalent Pillars of Excellence. Each question should be formatted as follows:
[Competency being assessed]
[Main question]
[Follow up question 1] - bulleted under main
[Follow up question 2] - bulleted under main
""",
    "Create response guides": """
Output should contain a set of sample responses based on NexaTalent rubric in your knowledge base. 
For each question you should write 5 sample responses that align with levels 1 through 5 in the NexaTalent rubric. 
These will be labeled concern, mild-concern, mixed, mild-strength, or strength respectively in your final output. 
You should generate one set of samples for each Main Question set, considering follow-up questions as part of the sample responses.
""",
    "Evaluate candidate responses": """
Output should be a numerical score between 1-5 grading the candidates overall performance. This should be followed with a justification paragraph. 
There will also be a score of 1-5 for each individual question with justifications for the scoring.
For scoring you will use the NexaTalent Rubric for Candidate Evaluation to assess and grade responses.
For justification paragraphs you will cite examples from the candidates response and connect them to the rubric as appropriate.
"""
}

###############################################################################
# Streamlit UI
###############################################################################
st.title("NexaTalent AI")
st.subheader("Your assistant for generating high-quality hiring content.")

# User selects a task
task = st.selectbox(
    "Select a task:",
    [
        "Write a job description",
        "Build Interview Questions",
        "Create response guides",
        "Evaluate candidate responses"
    ]
)

# User selects input method
input_method = st.radio(
    "How would you like to provide additional notes or information?",
    ("Paste text", "Upload file")
)

user_notes = ""
if input_method == "Paste text":
    user_notes = st.text_area("Enter additional notes or information:")
else:
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "md", "rtf", "docx", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
            user_notes = string_data.read()

###############################################################################
# Generate Button
###############################################################################
if st.button("Generate"):
    if not user_notes.strip():
        st.warning("Please provide text or upload a file with valid content.")
    else:
        # Dynamically select assistant ID and spinner text
        assistant_id = ASSISTANT_IDS[task]
        spinner_text = SPINNER_TEXTS[task]

        with st.spinner(spinner_text):
            chosen_task_format = TASK_FORMAT_DEFINITIONS[task]
            final_instructions = (
                MASTER_INSTRUCTIONS
                .replace("[TASK]", task)
                .replace("[task_format]", chosen_task_format.strip())
                .replace("[confidentiality_message]", CONFIDENTIALITY_MESSAGE)
                + "\n\n"
                "# ADDITIONAL NOTE #\n"
                "Only provide the final output per the #RESPONSE# section. "
                "Do not include any chain-of-thought, steps, or internal reasoning."
            )

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": f"USER NOTES:\n{user_notes}"}
                    ],
                    ###max_tokens=1000,
                    temperature=0.7
                )

                final_response = response.choices[0].message.content.strip()
                final_response = final_response.strip('"')  # Remove extra quotes if present

                # Check if the response contains the confidentiality message
                if final_response.strip() == CONFIDENTIALITY_MESSAGE.strip():
                    st.warning(CONFIDENTIALITY_MESSAGE)

                else:
                    st.text_area("Response", value=final_response, height=400)
            except Exception as e:
                st.error(f"An error occurred: {e}")
