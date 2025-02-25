import os
import openai
import streamlit as st
import requests
import json
from io import StringIO
from dotenv import load_dotenv
import re
from datetime import datetime
from zoneinfo import ZoneInfo  # For timezone support

# Try importing google.generativeai with error handling
try:
    import google.generativeai as genai
except ImportError:
    st.error("Required package 'google-generativeai' is not installed. Please install it using: pip install google-generativeai")
    st.stop()

# Load environment variables
load_dotenv()

# Debug environment variables loading
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.write("Loading from .env failed. Checking Streamlit secrets...")
    if hasattr(st.secrets, "GOOGLE_API_KEY"):
        google_api_key = st.secrets.GOOGLE_API_KEY
        os.environ["GOOGLE_API_KEY"] = google_api_key  # Set it in environment variables

if not google_api_key:
    st.error("Google API key not found in either .env or Streamlit secrets.")
    st.stop()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

openai.api_key = api_key

###############################################################################
# Helper function for timestamp in PST with 12-hour format
###############################################################################
def get_current_timestamp():
    # Returns timestamp in PST (America/Los_Angeles) in 12-hour format with AM/PM
    return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%m/%d/%Y %I:%M:%S %p")

###############################################################################
# Consent Tracker Setup (Updated webhook)
###############################################################################
CONSENT_TRACKER_URL = "https://script.google.com/macros/s/AKfycbyWRsvUxUNvj90eKtH_-XAfNwn9l4Xc_koh2wkccPct_0bpxA4T7DQNRu3VdAPyC_cGNw/exec"

def log_consent(email):
    """
    Logs the timestamp, email address, and consent status ("I agree")
    to a Google Form via the provided webhook.
    """
    timestamp = get_current_timestamp()
    data = {
        "timestamp": timestamp,
        "email": email,
        "consent": "I agree",
        "ip_address": ""
    }
    try:
        response = requests.post(CONSENT_TRACKER_URL, json=data)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to log consent. Status code: {response.status_code}")  # Log to console
            return None
    except Exception as e:
        print(f"Consent logging error: {str(e)}")  # Log to console
        return None

# Ensure consent is tracked in session state.
if "consent" not in st.session_state:
    st.session_state.consent = False

# Display consent UI if consent is not yet given.
if not st.session_state.consent:
    consent_container = st.empty()  # Create a container for the consent UI.
    with consent_container.container():
        st.markdown("## NexaTalent Consent Agreement")
        st.write('This version of the NexaTalent app is currently in a testing phase. By entering your email and pressing **I understand and accept** you agree to the following:')

        # Generate today's date in PST in a readable format.
        today = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%B %d, %Y")
        user_agreement_text = f"""EARLY QUALITATIVE TESTING AGREEMENT & MUTUAL NON-DISCLOSURE AGREEMENT
Effective Date: {today}
Parties: This agreement is between NexaTalent ("Provider") and the individual accepting these terms ("Tester").
This Agreement sets forth the terms under which the Tester is granted access to NexaTalent's pre-alpha product for qualitative testing while ensuring confidentiality and proper handling of proprietary information.

SECTION 1: EARLY QUALITATIVE TESTING AGREEMENT
This section governs the Tester's participation in NexaTalent's pre-alpha testing phase, where feedback will be collected to refine product usability, functionality, and experience.
1. Confidentiality
   The Tester acknowledges that all materials, discussions, prototypes, designs, test data, feedback, documentation, and any related information provided before, during, or after the testing phase are confidential and proprietary to NexaTalent.
   Tester agrees not to share, copy, disclose, or distribute any information related to the Testing Session, including but not limited to screenshots, descriptions, recordings, discussions, or findings.
   Any and all insights, feedback, reports, or analysis generated during testing become the exclusive intellectual property of NexaTalent.
   These confidentiality obligations remain in effect for three (3) years from the date of acceptance or until NexaTalent publicly releases the Product, whichever is later.
   Any breach of confidentiality may result in immediate termination of this Agreement and legal action as permitted by law.
2. Scope of Testing
   The Tester agrees to evaluate the Product using NexaTalent's designated platforms (e.g., Streamlit app, Google Sheets, email feedback forms). Testing includes:
   - Completing assigned tasks as instructed.
   - Logging and documenting identified issues.
   - Providing structured feedback via feedback forms, discussions, or debrief sessions.
3. Data Handling & Privacy
   NexaTalent is committed to responsible data management and Tester privacy:
   - Tester feedback will be anonymized before being included in reports or presentations.
   - Personal information required for testing will be minimized and stored securely.
   - While NexaTalent takes reasonable precautions to protect data, the company is not liable for unintended data breaches or cybersecurity incidents.
4. No Compensation
   The Tester acknowledges that participation is voluntary and that they will not receive financial compensation for any activities related to the Testing Session, including past, current, or future testing engagements.
5. Limitations of Liability
   The Product is provided "as is" and may contain bugs, incomplete features, or unexpected performance issues.
   NexaTalent is not responsible for any damage to the Tester's device, loss of data, or other issues resulting from participation in testing.
   NexaTalent, its employees, officers, and affiliates are not liable for any damages resulting from unforeseen data breaches or technical failures.
6. Termination
   Either party may terminate this Agreement with written notice.
   Upon termination, the Tester must return or destroy all confidential materials related to the Product as directed by NexaTalent.
   Even after termination, the Tester remains bound by the three (3)-year confidentiality obligation outlined in Section 1.
7. Dispute Resolution
   Any disputes arising under this Agreement will be resolved through binding arbitration in Washington State under the rules of the American Arbitration Association.
   Both parties waive any rights to litigate in court, except to enforce arbitration awards or seek injunctive relief.

SECTION 2: MUTUAL NON-DISCLOSURE AGREEMENT
This section ensures that confidential and proprietary information shared between NexaTalent and the Tester remains protected and undisclosed to third parties.
1. Definition of Confidential Information
   "Confidential Information" includes, but is not limited to:
   - Business, financial, customer, product, and service details.
   - Intellectual property, trade secrets, inventions, and methodologies.
   - Any documentation, schematics, prototypes, test results, or discussions related to NexaTalent's operations or products.
   - Any third-party confidential information provided by NexaTalent.
2. Exclusions from Confidential Information
   Confidential Information does not include information that:
   - Becomes publicly available without violation of this Agreement.
   - Is legally obtained from a third party without confidentiality obligations.
   - Was already known by the Tester prior to disclosure, as evidenced by written records.
   - Is independently developed by the Tester without using NexaTalent's confidential information.
3. Tester Obligations
   The Tester agrees to:
   - Maintain strict confidentiality regarding all disclosed information.
   - Use the information solely for testing purposes and not for any personal, competitive, or commercial advantage.
   - Not disclose, share, or distribute any confidential materials to third parties without NexaTalent's prior written consent.
4. Required Disclosure by Law
   If legally compelled to disclose confidential information, the Tester must:
   - Provide prompt written notice to NexaTalent.
   - Limit disclosure to only the portion required by law.
5. Return or Destruction of Confidential Information
   Upon termination of this Agreement, or at NexaTalent's request, the Tester must:
   - Return or permanently delete all confidential information in their possession.
   - Provide written certification confirming destruction of all copies.
6. Term & Survival
   This Agreement remains in effect for three (3) years from the date of acceptance.
   Confidentiality obligations related to trade secrets continue indefinitely.
7. Governing Law & Dispute Resolution
   This Agreement is governed by the laws of Washington State.
   Any disputes will be resolved through binding arbitration in Seattle, WA under the American Arbitration Association.

ACKNOWLEDGMENT & ACCEPTANCE
By clicking "I understand and accept", you acknowledge that:
 ✅ You have read, understood, and agree to the Early Qualitative Testing Agreement and the Mutual Non-DDisclosure Agreement.
 ✅ You accept all terms, including confidentiality, liability limitations, and dispute resolution.
 ✅ You understand that NexaTalent reserves the right to enforce this Agreement, including through legal means if necessary.
"""
        st.text_area("User Agreement", value=user_agreement_text, height=200, disabled=True)
        st.write('Please enter a valid email. This is used for communicating updates and providing support.')

        # Email input field.
        email = st.text_input("Enter your email address:")
        
        # Button is disabled until an email is entered.
        if st.button("I understand and accept", disabled=(not email.strip())):
            if log_consent(email) is not None:
                st.session_state.consent = True
                consent_container.empty()
    
    if not st.session_state.consent:
        st.stop()

###############################################################################
# Updated Logging Function with New WebApp URL (Main Logger)
###############################################################################
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxOcjcozSKkD-39s1LGd8U2iKsDUEQNyl1wg7GNWjdqsSBY3Y4NTIv7q-Gfrqw7WWPd/exec"

def log_to_google_sheets(
    tool_selection,
    user_input,
    initial_output,
    evaluator_feedback,
    evaluator_score,
    refined_output,
    feedback=None,
    prompt_tokens=None,
    completion_tokens=None,
    total_tokens=None,
    user_summary=None,
    model_comparison=None,
    model_judgement=None
):
    """
    Sends log data including initial output, evaluator feedback, evaluator score,
    refined output, and additional evaluation details (user_summary, model_comparison, model_judgement),
    along with the original fields, to the specified Google Sheet via the provided webhook.
    """
    timestamp = get_current_timestamp()
    data = {
        "timestamp": timestamp,
        "tool_selection": tool_selection,
        "user_input": user_input,
        "initial_output": initial_output,
        "evaluator_feedback": evaluator_feedback,
        "evaluator_score": evaluator_score,
        "refined_output": refined_output,
        "feedback": feedback if feedback is not None else "",
        "prompt_tokens": prompt_tokens if prompt_tokens is not None else "",
        "completion_tokens": completion_tokens if completion_tokens is not None else "",
        "total_tokens": total_tokens if total_tokens is not None else "",
        "user_summary": user_summary if user_summary is not None else "",
        "model_comparison": model_comparison if model_comparison is not None else "",
        "model_judgement": model_judgement if model_judgement is not None else ""
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.text
    except Exception as e:
        return f"Logging error: {e}"

###############################################################################
# Evaluator Function
###############################################################################

def evaluate_content(generated_output, rubric_context):
    """
    Sends the generated output and rubric context to the evaluator model (Gemini)
    and returns the evaluation feedback and score.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY and hasattr(st.secrets, "GOOGLE_API_KEY"):
        GOOGLE_API_KEY = st.secrets.GOOGLE_API_KEY
        
    if not GOOGLE_API_KEY:
        print("Google API key not found.")  # Log to console
        return None, ""
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }
    
    evaluator_prompt = (
        "Using the following rubric, evaluate the generated content below. "
        "Return a numerical score (0-5) and provide detailed feedback for improvements.\n\n"
        f"Rubric Context:\n{rubric_context}\n\n"
        f"Generated Content:\n{generated_output}\n\n"
        "Evaluator Response (Score and Feedback):"
    )
    
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            generation_config=generation_config
        )
        
        response = model.generate_content(evaluator_prompt)
        
        if not response.text:
            print("Empty response from Gemini API")  # Log to console
            return None, ""
            
        evaluator_text = response.text.strip()
        score_match = re.search(r"Score[:\s]*(\d)", evaluator_text)
        score = int(score_match.group(1)) if score_match else None
        
        if score is None:
            print("Could not extract score from evaluator response")  # Log to console
            
        return score, evaluator_text
        
    except Exception as e:
        print(f"Evaluator error: {str(e)}")  # Log to console
        print("Full error details:", e)  # Log to console
        try:
            available_models = [m.name for m in genai.list_models()]
            print("Available models:", available_models)  # Log to console
        except Exception as list_error:
            print(f"Error listing models: {str(list_error)}")  # Log to console
        return None, ""

###############################################################################
# Extract Model 
###############################################################################

def extract_evaluation_parts(text):
    """
    Extracts user_summary, model_comparison, and model_judgement from the given text.
    Assumes that the text contains lines like:
      >>User Summary: <content>
      >>Model Comparison: <content>
      >>Model Judgement: <content>
    """
    user_summary_match = re.search(r">>User Summary:\s*(.*)", text)
    model_comparison_match = re.search(r">>Model Comparison:\s*(.*)", text)
    model_judgement_match = re.search(r">>Model Judgement:\s*(.*)", text)
    
    user_summary = user_summary_match.group(1).strip() if user_summary_match else ""
    model_comparison = model_comparison_match.group(1).strip() if model_comparison_match else ""
    model_judgement = model_judgement_match.group(1).strip() if model_judgement_match else ""
    
    return user_summary, model_comparison, model_judgement

###############################################################################
# Mappings and Helper Texts
###############################################################################
ASSISTANT_IDS = {
    "Write a job description": "asst_1TJ2x5bhc1n4mS9YhOVcOFaJ",
    "Build Interview Questions": "asst_6jdd2oSBhocieeiDvQxnUNJ4",
    "Create response guides": "asst_B5g1JWvRl0Mr0Bl9lHKcQums",
    "Evaluate candidate responses": "asst_JI8Xr4zWgmsh6h2F5XF3aBkZ"
}

SPINNER_TEXTS = {
    "Write a job description": "Drafting your job description...",
    "Build Interview Questions": "Building your interview questions...",
    "Create response guides": "Creating your response guides...",
    "Evaluate candidate responses": "Evaluating your candidate's responses..."
}

TASK_LOOK_FORS = {
    "Write a job description": (
        "Users may submit information about job details, such as job title, responsibilities, qualifications, location, pay range, "
        "and details about the company. Look for specific job requirements or preferences that need to be incorporated."
    ),
    "Build Interview Questions": (
        "Users may submit a job description, competencies, or specific areas they want interview questions to focus on. "
        "They might also ask for questions related to specific skills or experiences relevant to the role."
    ),
    "Create response guides": (
        "Users may submit a question or set of questions for which they need example responses. "
        "They might also ask for help understanding how to evaluate responses using the NexaTalent rubric."
    ),
    "Evaluate candidate responses": (
        "Users may submit responses from candidates or summaries of candidate answers. "
        "Look for specific examples of candidate behavior or statements that need to be evaluated."
    )
}

TASK_OVERVIEWS = {
    "Write a job description": (
        "This task involves crafting a detailed job description that includes sections like 'About Us', 'Job Summary', "
        "'Key Responsibilities', 'Requirements', 'Qualifications', and more. The goal is to attract qualified candidates "
        "by clearly defining the role, responsibilities, and expectations."
    ),
    "Build Interview Questions": (
        "This task focuses on creating a set of unique situational interview questions tailored to the job's competencies "
        "and requirements. These questions are designed to assess a candidate's suitability for the role, using follow-up "
        "questions to explore their experience and problem-solving skills."
    ),
    "Create response guides": (
        "This task requires generating sample responses for the interview questions using the NexaTalent rubric. "
        "Each response corresponds to proficiency levels (e.g., Concern, Mixed, Strength) and helps interviewers "
        "evaluate candidates' answers effectively."
    ),
    "Evaluate candidate responses": (
        "This task involves analyzing and scoring candidates' responses to interview questions using a 1-5 scale. "
        "Justifications for the scores are provided, citing examples from the responses and linking them to the NexaTalent rubric."
    )
}

MASTER_INSTRUCTIONS = """
# CONTEXT #
You are a highly skilled assistant specializing in creating high-quality hiring materials. All of your outputs must adhere to the NexaTalent Pillars of Excellence and be evaluated against the rubric provided in the context above. Use the rubric as the standard for quality and for grading your output.

# OBJECTIVE #
When a user submits content, do the following:
1. Review the user's submission along with the rubric context provided.
2. Identify all relevant details from the submission (e.g., job details, required competencies, or candidate responses) as outlined in [TASK_LOOK_FORS].
   **If any of these are present, add 2 to the numeric value of {model_judgement}.
3. Generate a concise summary of what the user is asking for. == {user_summary}
4. Analyze your specific task ([TASK_OVERVIEW]) and summarize what your output should accomplish. == {model_summary}
5. Compare {user_summary} and {model_summary} to determine task similarity. Provide a comparison summary == {model_comparison}.
6. Based on the comparison, output a similarity score between 0 and 5 (0 means entirely different; 5 means identical). This numeric score should be set as {model_judgement}.
   ***Ensure you consider synonyms and varied phrasing for the task.
7. If {model_judgement} is less than or equal to 2, output the confidentiality message below.
8. If {model_judgement} is greater than 2, incorporate the rubric context in evaluating your draft and generate an initial draft for the final output.
9. Using the provided rubric, evaluate your draft output and write a brief summary explaining your score.
10. Revise your draft as needed to meet the quality standards of the rubric.
    
# STYLE #
Your language should be clear, concise, and educational. Avoid jargon and ensure your output is structured, using headings and bullet points where appropriate.

# TONE #
Maintain an informative and professional tone throughout your output.

# AUDIENCE #
Hiring team members and hiring managers.

# RESPONSE #
>>User Summary: <Insert user summary here>
>>Model Comparison: <Insert model comparison here>
>>Model Judgement: <Insert model judgement here>
[task_format]
"""

TASK_FORMAT_DEFINITIONS = {
    "Write a job description": """
Output should contain the following headings: "About Us, Job Summary, Key Responsibilities, Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment". 
Each section should build upon the previous ones to create a cohesive narrative. Use bullet points for Responsibilities, Requirements, and Benefits sections. 
Keep the About Us section under 150 words. Ensure all requirements listed are truly mandatory, including location and citizenship requirements when applicable. 
Always verify salary ranges comply with local pay transparency laws and reference specific technologies/tools rather than general terms whenever possible.
Ensure that your final output is evaluated against the quality standards provided in the rubric context above.
Follow the initial example below for the formatting of each section:

EXAMPLE:
**About Us**
At Intuitive Safety Solutions, we are dedicated to providing top-tier safety consulting services, helping our clients create safer workplaces across industries. Our commitment to excellence, innovation in safety solutions, and a workplace culture that values diversity, equity, and inclusion are at the heart of everything we do.

**Job Summary**
We are seeking a local Senior Safety Manager to join us as an Owner's Representative on a project in the Folsom, California area. The project will encompass the construction of a new lab and improvements to existing tenant spaces. This pivotal role will steer our on-site safety initiatives, ensuring a safe and compliant work environment for all project participants.

**Key Responsibilities**
- Lead the implementation of comprehensive safety protocols for the construction project.
- Conduct regular safety inspections and audits to identify and mitigate risks.
- Act as a key liaison between the project team, contractors, and stakeholders on matters related to safety.
- Develop and deliver safety training sessions to project staff and contractors.
- Manage incident investigation processes, including reporting and follow-up actions to prevent recurrence.
- Continuously update safety documentation and compliance records in alignment with local, state, and federal regulations.

>>>Continue this formatting for the Requirements, Qualifications, Key Skills, Benefits, Salary, and Work Environment sections following the instructions above.
""",
    "Build Interview Questions": """
Output should contain a set of unique situational interview questions with follow-up questions based on provided interview competencies, information provided, and NexaTalent Pillars of Excellence. 
Ensure that each question reflects the quality and evaluation standards outlined in the rubric provided in the context.
Each question should be formatted as follows:

EXAMPLE:
>>User Summary: The user is seeking to create interview questions for a mid-level Nurse position at Care Partners in Omaha, NE. They have provided detailed information about the organization, job summary, key responsibilities, requirements, qualifications, key skills, benefits, salary, and work environment to guide the development of relevant interview questions that align with the competencies needed for the role.
>>Model Summary: The task of building interview questions involves creating a set of situational questions that assess candidates' competencies, experiences, and qualifications relevant to the mid-level Nurse position. These questions should be tailored to reflect the responsibilities and skills outlined in the job description and should help interviewers evaluate the suitability of candidates for the role.
>>Model Judgement: The tasks of the user and the model are highly similar, as both involve the creation of interview questions specifically designed for the Nurse position. The focus is on assessing the candidates' abilities and experiences related to the provided job details. Thus, I would score this a 5.
 
**Experience with Club Channel Sales**
Main Question: Can you describe a successful initiative you've led in the Club Channel space that delivered significant business growth? What was your role, and how did you measure success?
- Follow-up 1: How did you address challenges during this initiative, especially regarding broker partner management?
- Follow-up 2: What strategies did you use to ensure alignment across cross-functional teams?
""",
    "Create response guides": """
Objective: Generate a cohesive set of sample responses based on the NexaTalent rubric, ensuring each response reflects the corresponding level of proficiency.
Structure: For each main question, write five sample responses that align with levels 1 through 5 of the NexaTalent rubric. Label each response clearly as follows: Concern, Mild Concern, Mixed, Mild Strength, Strength.
Integration: Generate one unified set of samples for each question, incorporating responses to any follow-up questions as part of the final output.
Summary: After providing the sample responses, condense the overall summaries for each proficiency level into a format that is easily digestible, clearly differentiating the levels while maintaining the core insights about candidate competencies.
Clarity and Conciseness: Ensure that each response and summary is concise, avoids unnecessary jargon, and is written in an educational tone to facilitate understanding among hiring team members.
Ensure that your final set of responses adheres to the quality standards outlined in the rubric provided in the context.
    
Example Output:

**Question Set**
Describe a time when you identified and capitalized on a growth opportunity within a Club account, leading to mutual satisfaction and business expansion. How did you approach the partnership? 
- Follow-up 1: How did you align your strategies with the retailer's objectives to foster a cooperative relationship? 
- Follow-up 2: Can you share an example of how you handled a disagreement or challenge with a Club partner and turned it into a positive outcome? 

**Concern** 
- The candidate exhibits minimal understanding of growth opportunities and partnership dynamics, with vague and unclear responses. They avoid complexities and lack engagement with essential business concepts. They may be suitable for entry-level roles under close supervision and would require significant development to progress in more strategic positions.
**Mild Concern**
- This candidate reflects a limited understanding of key concepts related to growth and partnerships, often providing vague responses. They may recognize opportunities in theory but lack clear strategies for implementation. They would be suited for routine-oriented positions with considerable support and training needed to enhance their competencies.
**Mixed** 
- The candidate shows a basic grasp of growth opportunities, but their responses indicate reliance on routine practices and occasional gaps in strategic thinking. While they acknowledge challenges, they may struggle to align strategies with partner objectives. They could fit roles that allow for development while performing functional tasks but would benefit from additional coaching.
**Mild Strength** 
- This candidate demonstrates a solid understanding of growth opportunities and relationship-building, though they may not consistently leverage these effectively. They are capable and reliable but might lack the depth of analysis and proactive engagement found in higher proficiency levels. They would excel in supportive roles within account management with structured guidance.
**Strength** 
- The candidate is a proactive and results-oriented professional who seeks growth opportunities through thorough analysis and collaboration. They excel in building strong partnerships and effectively resolving challenges through constructive dialogue. Their ability to deliver measurable outcomes makes them an asset in business development and client management roles.
""",
    "Evaluate candidate responses": """
Output should be a numerical score between 1-5 grading the candidate's overall performance. This should be followed by a justification paragraph. 
There will also be a score of 1-5 for each individual question with justifications for the scoring.
For scoring, use the NexaTalent Rubric for Candidate Evaluation to assess and grade responses.
For justification paragraphs, cite examples from the candidate's response and connect them to the NexaTalent rubric as appropriate.
Ensure that your evaluation is strictly aligned with the quality standards outlined in the rubric provided in the context.
"""
}

###############################################################################
# Streamlit UI and Integration
###############################################################################
st.title("NexaTalent AI")
st.subheader("Your assistant for generating high-quality hiring content.")

# Task selection and input method
task = st.selectbox("Select a task:", list(ASSISTANT_IDS.keys()))
input_method = st.radio("How would you like to provide additional notes or information?", ("Paste text", "Upload file"))

user_notes = ""
if input_method == "Paste text":
    user_notes = st.text_area("Enter additional notes or information:")
else:
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "md", "rtf", "docx", "pdf"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
            user_notes = string_data.read()
        else:
            st.error("Currently, only plain text files are supported. Please upload a .txt file.")

@st.cache_data
def load_rubric(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return None

if st.button("Generate"):
    if not user_notes.strip():
        st.warning("Please provide text or upload a file with valid content.")
    else:
        assistant_id = ASSISTANT_IDS[task]
        spinner_text = SPINNER_TEXTS[task]
        
        with st.spinner(spinner_text):
            chosen_task_format = TASK_FORMAT_DEFINITIONS[task]
            chosen_task_overview = TASK_OVERVIEWS[task]
            chosen_task_look_fors = TASK_LOOK_FORS[task]

            rubric_mapping = {
                "Write a job description": "NexaTalent Rubric for Job Description Evaluation.txt",
                "Build Interview Questions": "NexaTalent Rubric for Interview Question Generation.txt",
                "Create response guides": "NexaTalent Rubric for Candidate Responses.txt",
                "Evaluate candidate responses": "NexaTalent Rubric for Candidate Responses.txt"
            }
            rubric_file_path = os.path.join("reference_materials", rubric_mapping.get(task, ""))
            rubric_context = load_rubric(rubric_file_path)
            if rubric_context is None:
                st.warning(f"Rubric file not found for task: {task}")
                rubric_context = ""
            
            final_instructions = (
                "Rubric Context:\n" + rubric_context + "\n\n" +
                MASTER_INSTRUCTIONS
                .replace("[TASK_OVERVIEW]", chosen_task_overview)
                .replace("[TASK_LOOK_FORS]", chosen_task_look_fors)
                .replace("[task_format]", chosen_task_format.strip())
                .replace("[confidentiality_message]", "It looks like you may be trying to complete a task that this tool hasn't yet been fine-tuned to handle. At NexaTalent, we are committed to delivering tools that meet or exceed our rigorous quality standards. This commitment drives our mission to improve the quality of organizations through technology and data-driven insights.\n\nIf you have questions about how our app works or the types of tasks it specializes in, please feel free to reach out to us at info@nexatalent.com.")
                + "\n\n"
                "# ADDITIONAL NOTE #\n"
                "Only provide the final output per the #RESPONSE# section. Do not include any chain-of-thought, steps, or internal reasoning."
            )
            
            try:
                # Step 1: Generate initial content.
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": f"USER NOTES:\n{user_notes}"}
                    ],
                    temperature=0.7
                )
                
                initial_output = response.choices[0].message.content.strip()
                
                usage = getattr(response, "usage", None)
                if usage is not None:
                    prompt_tokens = usage.prompt_tokens
                    completion_tokens = usage.completion_tokens
                    total_tokens = usage.total_tokens
                else:
                    prompt_tokens = completion_tokens = total_tokens = ""
                
                # Extract evaluation parts
                user_summary, model_comparison, model_judgement = extract_evaluation_parts(initial_output)
                
                # Step 2: Evaluate the initial output using Gemini.
                score, evaluator_feedback = evaluate_content(initial_output, rubric_context)
                
                # Step 3: Refine the content using evaluator feedback.
                refinement_instructions = (
                    f"The following content was generated:\n{initial_output}\n\n"
                    f"The evaluator provided the following feedback:\n{evaluator_feedback}\n\n"
                    "Please refine the content based on the feedback."
                )
                refined_response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": refinement_instructions}
                    ],
                    temperature=0.7
                )
                refined_output = refined_response.choices[0].message.content.strip()
                
                # Move the logging here, after all data is available
                log_to_google_sheets(
                    tool_selection=task,
                    user_input=user_notes,
                    initial_output=initial_output,
                    evaluator_feedback=evaluator_feedback,
                    evaluator_score=score,
                    refined_output=refined_output,
                    feedback=f"Refinement based on evaluator score: {score}",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    user_summary=user_summary,
                    model_comparison=model_comparison,
                    model_judgement=model_judgement
                )

                # Step 4: Check the refined output for model judgement value.
                model_judgement_value = None
                judgement_match = re.search(r"\{model_judgement\}[:\s]*([0-5])", refined_output)
                if judgement_match:
                    model_judgement_value = int(judgement_match.group(1))
                
                if model_judgement_value is not None and model_judgement_value <= 2:
                    st.warning(
                        "It looks like you may be trying to complete a task that this tool hasn't yet been fine-tuned to handle. "
                        "At NexaTalent, we are committed to delivering tools that meet or exceed our rigorous quality standards. "
                        "This commitment drives our mission to improve the quality of organizations through technology and data-driven insights.\n\n"
                        "If you have questions about how our app works or the types of tasks it specializes in, please feel free to reach out to us at info@nexatalent.com."
                    )
                else:
                    # Clean the output by removing evaluation content
                    clean_output = refined_output
                    
                    # Remove evaluation summary section
                    if "### Evaluation Summary" in clean_output:
                        clean_output = clean_output.split("### Evaluation Summary")[0]
                    
                    # Remove any trailing evaluation content
                    if "---" in clean_output:
                        clean_output = clean_output.split("---")[0]
                    
                    # Remove any trailing whitespace and newlines
                    clean_output = clean_output.strip()
                    
                    # Display the cleaned output
                    st.text_area("Generated Content", value=clean_output, height=400)

            except Exception as e:
                st.error(f"An error occurred: {e}")

def verify_model_availability():
    """Verify that the required model is available"""
    try:
        available_models = [m.name for m in genai.list_models()]
        required_model = 'gemini-2.0-flash'
        
        if required_model not in available_models:
            # Log error to console instead of showing to user
            print(f"Required model '{required_model}' is not available. Using default model 'gemini-pro' instead.")
            return 'gemini-pro'
        return required_model
    except Exception as e:
        print(f"Error verifying model availability: {str(e)}")  # Log to console
        return 'gemini-pro'

# Remove the test button from UI
# if st.button("Test Consent Webhook"):
#     test_consent_webhook()

# Remove model verification from UI display
model_to_use = verify_model_availability()