import streamlit as st
import json
import os
import random
import datetime
import pandas as pd
from io import BytesIO
from streamlit_js_eval import streamlit_js_eval
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# --- Configuration & Constants ---
QUIZ_TITLE = "Design Thinking - Analyse Phase Quiz"
COURSE_NAME = "Design Thinking (25HS204)"
QUESTIONS_PER_QUIZ = 20
SUBMISSIONS_FILE = "dt_analyse_submissions.json"
MALPRACTICE_LOG_FILE = "dt_analyse_malpractice.json"
ADMIN_PASSWORD = "admin123"

# --- Question Database ---
QUESTION_BANK = [
    # Data Synthesis & Pattern Recognition (10 questions)
    {"id": 1, "question": "What is the primary difference between analysis and synthesis in Design Thinking?", "options": ["Analysis breaks down, synthesis pieces together", "Analysis is qualitative, synthesis is quantitative", "Analysis is first, synthesis is last", "Analysis is creative, synthesis is logical"], "correct": 0},
    {"id": 2, "question": "What are the three stages of synthesis in the Analyse phase?", "options": ["Research, Design, Test", "Learnings, Themes, Insights", "Empathize, Define, Ideate", "Observe, Interpret, Ideate"], "correct": 1},
    {"id": 3, "question": "In the synthesis process, what is a 'Learning'?", "options": ["A final conclusion", "An initial observation or quote", "A problem statement", "A solution idea"], "correct": 1},
    {"id": 4, "question": "What is a 'Theme' in data synthesis?", "options": ["A single user quote", "A cluster of similar observations", "A final insight", "A problem statement"], "correct": 1},
    {"id": 5, "question": "How do insights typically emerge during synthesis?", "options": ["From single observations", "From contradictions in the data", "From stakeholder requests", "From technical constraints"], "correct": 1},
    {"id": 6, "question": "What is deductive thinking in synthesis?", "options": ["Specific to general reasoning", "General to specific reasoning", "Creative leaps to explanations", "Random pattern recognition"], "correct": 1},
    {"id": 7, "question": "What is inductive thinking in synthesis?", "options": ["General to specific reasoning", "Specific to general reasoning", "Testing hypotheses", "Creative guessing"], "correct": 1},
    {"id": 8, "question": "What is abductive thinking?", "options": ["Logical deduction", "Statistical analysis", "Creative leap to best explanation", "Linear reasoning"], "correct": 2},
    {"id": 9, "question": "What type of data is most important in the Analyse phase?", "options": ["Only quantitative data", "Only qualitative data", "Both qualitative and quantitative", "Neither, only assumptions"], "correct": 2},
    {"id": 10, "question": "Pattern recognition in synthesis helps to:", "options": ["Make data look organized", "Identify recurring themes across observations", "Create random groupings", "Avoid user feedback"], "correct": 1},
    
    # Root Cause Analysis & 5 Whys (10 questions)
    {"id": 11, "question": "What is the purpose of the 5 Whys technique?", "options": ["To annoy users", "To identify root causes, not symptoms", "To create more questions", "To delay the project"], "correct": 1},
    {"id": 12, "question": "Do you always ask exactly 5 'Why' questions in the 5 Whys technique?", "options": ["Yes, always exactly 5", "No, it depends on the problem complexity", "Yes, but sometimes 6", "No, always 3"], "correct": 1},
    {"id": 13, "question": "Who developed the 5 Whys technique?", "options": ["Steve Jobs", "Sakichi Toyoda", "Henry Ford", "Thomas Edison"], "correct": 1},
    {"id": 14, "question": "The 5 Whys technique was originally used in:", "options": ["Software development", "Healthcare", "Toyota Production System", "Education"], "correct": 2},
    {"id": 15, "question": "What is the difference between a symptom and a root cause?", "options": ["They are the same", "Symptom is observable, root cause is underlying", "Symptom is hidden, root cause is visible", "No difference"], "correct": 1},
    {"id": 16, "question": "When applying 5 Whys, you should stop asking when:", "options": ["You reach exactly 5", "You get tired", "No further logical 'Why' can be asked", "The user says stop"], "correct": 2},
    {"id": 17, "question": "The 5 Whys technique belongs to which category of analysis?", "options": ["Statistical analysis", "Logical analysis", "Creative analysis", "Random analysis"], "correct": 1},
    {"id": 18, "question": "What should each answer in 5 Whys be based on?", "options": ["Assumptions", "Guesses", "Facts and observations", "Opinions"], "correct": 2},
    {"id": 19, "question": "In the student tardiness case study, what was the root cause?", "options": ["Student is lazy", "Student wakes up late", "Student has too many courses", "Student doesn't care"], "correct": 2},
    {"id": 20, "question": "Why is treating symptoms instead of root causes problematic?", "options": ["It's faster", "Problems will recur", "It's cheaper", "It's easier"], "correct": 1},
    
    # Affinity Mapping (8 questions)
    {"id": 21, "question": "What is the primary purpose of affinity mapping?", "options": ["To make data look pretty", "To organize unstructured data into patterns", "To confuse the team", "To delay decisions"], "correct": 1},
    {"id": 22, "question": "Affinity mapping is also known as:", "options": ["The Toyota method", "The KJ method", "The Stanford method", "The Apple method"], "correct": 1},
    {"id": 23, "question": "What should be written on each affinity note?", "options": ["Multiple ideas", "One single observation or idea", "A full paragraph", "Nothing specific"], "correct": 1},
    {"id": 24, "question": "When is affinity mapping most useful?", "options": ["When you have structured data", "When you have large amounts of unstructured data", "When you have no data", "When the project is done"], "correct": 1},
    {"id": 25, "question": "What is the first step in affinity mapping?", "options": ["Create groups", "Label everything", "Capture individual observations", "Make conclusions"], "correct": 2},
    {"id": 26, "question": "How should affinity notes be grouped?", "options": ["Randomly", "By color", "Based on natural relationships", "Alphabetically"], "correct": 2},
    {"id": 27, "question": "Affinity mapping should be done:", "options": ["Alone for best results", "Collaboratively with the team", "Only by the designer", "Only by stakeholders"], "correct": 1},
    {"id": 28, "question": "What makes a good label for an affinity group?", "options": ["Very long and detailed", "Vague and general", "Clear and descriptive", "A single word"], "correct": 2},
    
    # Problem Statement Formulation (12 questions)
    {"id": 29, "question": "What are the three traits of a good problem statement?", "options": ["Long, detailed, technical", "Human-centered, broad enough, narrow enough", "Business-focused, technical, specific", "Short, vague, flexible"], "correct": 1},
    {"id": 30, "question": "A problem statement should be human-centered, meaning:", "options": ["It focuses on technology", "It focuses on users and their needs", "It focuses on business goals", "It focuses on competitors"], "correct": 1},
    {"id": 31, "question": "Why should problem statements be broad enough?", "options": ["To confuse people", "To allow creative freedom", "To avoid making decisions", "To delay the project"], "correct": 1},
    {"id": 32, "question": "Why should problem statements be narrow enough?", "options": ["To limit creativity", "To be manageable and solvable", "To make them easy", "To avoid work"], "correct": 1},
    {"id": 33, "question": "What is the POV statement formula?", "options": ["User + Problem + Solution", "[User] needs [Need] because [Insight]", "Problem + Answer + Test", "Question + Answer + Verify"], "correct": 1},
    {"id": 34, "question": "In a POV statement, the NEED should be expressed as:", "options": ["A noun (solution)", "An adjective", "A verb (action)", "A question"], "correct": 2},
    {"id": 35, "question": "In a POV statement, the INSIGHT reveals:", "options": ["The solution", "Why the need matters", "What to build", "When to start"], "correct": 1},
    {"id": 36, "question": "What does HMW stand for?", "options": ["How Many Ways", "How Might We", "How Must We", "How Maybe We"], "correct": 1},
    {"id": 37, "question": "Why is 'MIGHT' important in HMW questions?", "options": ["It shows uncertainty", "It allows exploration of possibilities", "It shows weakness", "It delays decisions"], "correct": 1},
    {"id": 38, "question": "HMW questions should:", "options": ["Include the solution", "Suggest one approach", "Inspire multiple solutions", "Be very technical"], "correct": 2},
    {"id": 39, "question": "A common pitfall in problem statements is:", "options": ["Making them user-focused", "Including solutions (solution bias)", "Making them clear", "Testing them"], "correct": 1},
    {"id": 40, "question": "Which is a bad problem statement?", "options": ["Users need quick meal solutions", "We need to build a mobile app", "Parents need confidence in decisions", "Students need accessible learning"], "correct": 1},
    
    # Conflict of Interest (8 questions)
    {"id": 41, "question": "What is a conflict of interest in problem-solving?", "options": ["Team disagreements", "When satisfying one requirement makes another difficult", "Budget issues", "Time pressure"], "correct": 1},
    {"id": 42, "question": "How should conflicts be handled in the Define phase?", "options": ["Ignore them", "Make them explicit and creative challenges", "Choose one side", "Delay decisions"], "correct": 1},
    {"id": 43, "question": "In the Porthos case study, what was the conflict?", "options": ["Price vs quality", "Perfect fit vs no touch by tailor", "Speed vs accuracy", "Cost vs time"], "correct": 1},
    {"id": 44, "question": "The goal when facing conflicts is to:", "options": ["Choose one requirement", "Compromise on both", "Satisfy both requirements simultaneously", "Avoid the problem"], "correct": 2},
    {"id": 45, "question": "A user vs. business conflict example:", "options": ["Two users disagree", "Users want free service, business needs revenue", "Two businesses compete", "User wants speed and accuracy"], "correct": 1},
    {"id": 46, "question": "Why make conflicts explicit rather than hiding them?", "options": ["To create problems", "So they can be creatively resolved", "To delay the project", "To confuse stakeholders"], "correct": 1},
    {"id": 47, "question": "In conflict resolution, Either/Or thinking:", "options": ["Is the best approach", "Fails to find creative solutions", "Always works", "Is required"], "correct": 1},
    {"id": 48, "question": "Both/And thinking in conflict resolution:", "options": ["Is impossible", "Seeks to satisfy both requirements", "Chooses one side", "Avoids decisions"], "correct": 1},
    
    # Problem Definition Canvas (6 questions)
    {"id": 49, "question": "The Problem Definition Canvas helps to:", "options": ["Build solutions", "Comprehensively define problems", "Test prototypes", "Manage teams"], "correct": 1},
    {"id": 50, "question": "In the Problem Definition Canvas, the customer type should be:", "options": ["Very general", "The average user", "Highly specific (the 10% extreme users)", "Anyone who might use it"], "correct": 2},
    {"id": 51, "question": "Why focus on extreme users in problem definition?", "options": ["They are easy to find", "Their needs reveal broader audience needs", "They complain more", "They pay more"], "correct": 1},
    {"id": 52, "question": "Emotional impact in the canvas:", "options": ["Should be ignored", "Links problem to motivation for solutions", "Is not important", "Only matters for children"], "correct": 1},
    {"id": 53, "question": "Quantifiable impact should be expressed in:", "options": ["Vague terms", "Legible currency (time, money, health, etc.)", "Technical jargon", "Future projections"], "correct": 1},
    {"id": 54, "question": "Alternative solutions in the canvas show:", "options": ["What we should build", "What users currently use (competitive landscape)", "Impossible options", "Future technology"], "correct": 1},
    
    # Case Studies Application (8 questions)
    {"id": 55, "question": "In the student tardiness case, the simplest solution was:", "options": ["Better alarm clock", "Longer sleep", "Take fewer courses", "Skip class"], "correct": 2},
    {"id": 56, "question": "In the auto workshop case, what was the key reframing?", "options": ["Workshop is too far → Distance customers travel is too far", "Customers are lazy → Workshop is bad", "Price is too high → Service is poor", "No reframing needed"], "correct": 0},
    {"id": 57, "question": "The auto workshop solution was:", "options": ["Move the workshop", "Lower prices", "Offer pick-up and drop-off service", "Advertise more"], "correct": 2},
    {"id": 58, "question": "What lesson does the Porthos case teach?", "options": ["Violence solves problems", "Creative thinking resolves paradoxes", "Avoid difficult clients", "Traditional methods always work"], "correct": 1},
    {"id": 59, "question": "One solution for Porthos was:", "options": ["Force him to cooperate", "Get him drunk (intoxication)", "Refuse service", "Charge more"], "correct": 1},
    {"id": 60, "question": "The best Porthos solution was:", "options": ["Intoxication", "Use old clothes", "Train a trusted companion to measure", "Use a long pole"], "correct": 2},
    {"id": 61, "question": "All three case studies demonstrate:", "options": ["Surface vs deep analysis", "Speed over quality", "Technology solutions", "Ignoring users"], "correct": 0},
    {"id": 62, "question": "The common pattern across all cases is:", "options": ["Business focus", "Quick solutions", "Looking beyond symptoms to root causes", "Avoiding conflict"], "correct": 2},
    
    # Integration & Best Practices (8 questions)
    {"id": 63, "question": "The Define phase connects:", "options": ["Empathize to Ideate", "Ideate to Prototype", "Prototype to Test", "Test to Empathize"], "correct": 0},
    {"id": 64, "question": "What transfers from Empathize to Define?", "options": ["Solutions", "Raw research data and empathy maps", "Prototypes", "Final products"], "correct": 1},
    {"id": 65, "question": "What transfers from Define to Ideate?", "options": ["Research notes", "Clear problem statements and HMW questions", "Prototypes", "Test results"], "correct": 1},
    {"id": 66, "question": "A best practice in the Define phase is:", "options": ["Work alone", "Rush to conclusions", "Embrace messiness and collaboration", "Ignore data"], "correct": 2},
    {"id": 67, "question": "Why should you look for contradictions in data?", "options": ["To create problems", "Most powerful insights come from contradictions", "To confuse the team", "To delay progress"], "correct": 1},
    {"id": 68, "question": "A common pitfall is:", "options": ["Too much research", "Jumping to solutions too quickly", "Too much collaboration", "Too much time on definition"], "correct": 1},
    {"id": 69, "question": "Analysis paralysis means:", "options": ["Analyzing too fast", "Over-analyzing without reaching conclusions", "Not analyzing enough", "Analyzing perfectly"], "correct": 1},
    {"id": 70, "question": "Before moving to Ideate, verify that:", "options": ["You have a solution", "Problem statement is clear and team aligned", "Prototype is ready", "Testing is complete"], "correct": 1},
]

# --- Helper Functions ---
def load_json_data(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def save_submission(submission_data):
    submissions = load_json_data(SUBMISSIONS_FILE)
    submissions.append(submission_data)
    save_json_data(SUBMISSIONS_FILE, submissions)

def save_malpractice_log(log_data):
    logs = load_json_data(MALPRACTICE_LOG_FILE)
    logs.append(log_data)
    save_json_data(MALPRACTICE_LOG_FILE, logs)

def create_results_pdf(session_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph(COURSE_NAME, styles['h1']))
    story.append(Paragraph(f"{QUIZ_TITLE} - Results", styles['h2']))
    story.append(Spacer(1, 0.25 * inch))
    
    student_info = [
        ['Student Name:', session_data['student_name']],
        ['Register Number:', session_data['register_number']],
        ['Year:', session_data.get('year', 'N/A')],
        ['Department:', session_data.get('department', 'N/A')],
        ['Venue:', session_data.get('venue', 'N/A')],
        ['Date & Time:', session_data['timestamp']],
        ['Score:', f"<b>{session_data['score']} / {len(session_data['questions'])}</b>"]
    ]
    info_table = Table(student_info, colWidths=[1.5 * inch, 4.5 * inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5 * inch))
    
    story.append(Paragraph("Detailed Answer Sheet", styles['h3']))
    results_data = [['Q#', 'Your Answer', 'Correct Answer', 'Result']]
    
    for i, q in enumerate(session_data['questions']):
        user_answer_idx = session_data['answers'][i]
        user_answer_text = q['options'][user_answer_idx] if user_answer_idx is not None else "Not Answered"
        correct_answer_text = q['options'][q['correct']]
        result = "Correct" if user_answer_idx == q['correct'] else "Wrong"
        
        p_user = Paragraph(user_answer_text, styles['Normal'])
        p_correct = Paragraph(correct_answer_text, styles['Normal'])
        results_data.append([i + 1, p_user, p_correct, result])
    
    results_table = Table(results_data, colWidths=[0.5 * inch, 2.5 * inch, 2.5 * inch, 0.7 * inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(0x005A9C)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
    ]))
    
    for i, row in enumerate(results_data[1:], start=1):
        if row[-1] == "Correct":
            results_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightgreen)]))
        else:
            results_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightpink)]))
            
    story.append(results_table)
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()

def trigger_server_side_malpractice():
    if not st.session_state.get('malpractice_detected', False):
        st.session_state.malpractice_detected = True
        log_data = {
            "student_name": st.session_state.student_name,
            "register_number": st.session_state.register_number,
            "year": st.session_state.get('year', 'N/A'),
            "department": st.session_state.get('department', 'N/A'),
            "venue": st.session_state.get('venue', 'N/A'),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "User switched tabs or minimized the browser."
        }
        save_malpractice_log(log_data)
        st.session_state.pop('questions', None)
        st.session_state.pop('answers', None)

# --- UI Functions ---
def render_start_page():
    st.set_page_config(page_title=QUIZ_TITLE, layout="centered")
    st.title(f"🎓 {QUIZ_TITLE}")
    st.markdown(f"**Course:** {COURSE_NAME}")
    st.markdown("**Topic:** Analyse Phase - Data Synthesis, Root Cause Analysis, Problem Statement Formulation")
    st.warning("⚠️ **Important:** Do not switch tabs or minimize the browser during the quiz. Doing so will automatically terminate your session.")
    st.markdown("---")
    
    with st.form("student_info_form"):
        student_name = st.text_input("Enter your Full Name *", key="student_name_input")
        register_number = st.text_input("Enter your Register Number *", key="register_number_input")
        year = st.selectbox("Select Year *", ["", "1st Year", "2nd Year", "3rd Year", "4th Year"], key="year_input")
        department = st.text_input("Enter your Department *", key="department_input", placeholder="e.g., Computer Science, Mechanical Engineering")
        venue = st.text_input("Enter Venue/Location *", key="venue_input", placeholder="e.g., Main Campus, Block A, Online")
        submitted = st.form_submit_button(f"Start Quiz ({QUESTIONS_PER_QUIZ} Questions)")

        if submitted:
            if not student_name or not register_number or not year or not department or not venue:
                st.error("Please fill in all required fields marked with *")
            else:
                st.session_state.student_name = student_name
                st.session_state.register_number = register_number
                st.session_state.year = year
                st.session_state.department = department
                st.session_state.venue = venue
                st.session_state.quiz_started = True
                st.session_state.questions = random.sample(QUESTION_BANK, QUESTIONS_PER_QUIZ)
                st.session_state.answers = [None] * QUESTIONS_PER_QUIZ
                st.session_state.current_question_index = 0
                st.rerun()

def render_quiz_page():
    malpractice_js = """
    <script>
    const handleVisibilityChange = () => {
        if (document.hidden) {
            window.sessionStorage.setItem('malpractice', 'true');
            document.body.innerHTML = `<div style='text-align: center; padding: 40px; color: red;'>
                <h1>Malpractice Detected</h1>
                <p>Your quiz has been terminated because you switched tabs or minimized the window.</p>
                <p>Please refresh the page.</p>
            </div>`;
        }
    };
    window.addEventListener('visibilitychange', handleVisibilityChange, { once: true });
    </script>
    """
    st.components.v1.html(malpractice_js, height=0)

    malpractice_flag = streamlit_js_eval(js_expressions="window.sessionStorage.getItem('malpractice')", key='malpractice_check')
    
    if malpractice_flag == 'true':
        trigger_server_side_malpractice()
        st.rerun()
        return
        
    st.title(QUIZ_TITLE)
    st.progress((st.session_state.current_question_index + 1) / QUESTIONS_PER_QUIZ)
    st.caption(f"Question {st.session_state.current_question_index + 1} of {QUESTIONS_PER_QUIZ}")

    question_data = st.session_state.questions[st.session_state.current_question_index]
    
    st.markdown(f"### {st.session_state.current_question_index + 1}. {question_data['question']}")
    
    current_answer_index = st.session_state.answers[st.session_state.current_question_index]
    if current_answer_index is None:
        current_answer_index = 0

    user_choice_label = st.radio(
        "Select your answer:",
        options=question_data['options'],
        index=current_answer_index,
        key=f"q_{st.session_state.current_question_index}"
    )
    
    st.session_state.answers[st.session_state.current_question_index] = question_data['options'].index(user_choice_label)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_question_index == 0):
            st.session_state.current_question_index -= 1
            st.rerun()
            
    with col3:
        if st.session_state.current_question_index < QUESTIONS_PER_QUIZ - 1:
            if st.button("Next ➡️"):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("Finish & Submit Quiz ✅", type="primary"):
                st.session_state.quiz_submitted = True
                st.rerun()

def render_results_page():
    score = 0
    for i, q in enumerate(st.session_state.questions):
        if st.session_state.answers[i] == q['correct']:
            score += 1
    st.session_state.score = score

    st.balloons()
    st.title("🎉 Quiz Submitted! 🎉")
    st.metric(label="Your Final Score", 
              value=f"{st.session_state.score} / {QUESTIONS_PER_QUIZ}",
              delta=f"{((st.session_state.score/QUESTIONS_PER_QUIZ)*100):.2f}%")
    st.markdown("---")
    
    submission_data = {
        "student_name": st.session_state.student_name,
        "register_number": st.session_state.register_number,
        "year": st.session_state.get('year', 'N/A'),
        "department": st.session_state.get('department', 'N/A'),
        "venue": st.session_state.get('venue', 'N/A'),
        "score": st.session_state.score,
        "answers": st.session_state.answers,
        "questions": st.session_state.questions,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if not st.session_state.get('submission_saved', False):
        save_submission(submission_data)
        st.session_state.submission_saved = True

    pdf_bytes = create_results_pdf(submission_data)
    st.download_button(
        label="📄 Download Detailed Report (PDF)",
        data=pdf_bytes,
        file_name=f"{st.session_state.register_number}_DT_Analyse_Quiz_Report.pdf",
        mime="application/pdf"
    )

    if st.button("↩️ Take Another Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_malpractice_page():
    st.set_page_config(page_title="Quiz Terminated", layout="centered")
    st.title("🚨 Quiz Terminated 🚨")
    st.error(
        "Your quiz session has been terminated due to malpractice (switching tabs or minimizing the browser). "
        "This incident has been logged. Please contact your administrator."
    )
    st.warning(f"**Student:** {st.session_state.get('student_name', 'N/A')}")
    st.warning(f"**Register Number:** {st.session_state.get('register_number', 'N/A')}")
    st.warning(f"**Year:** {st.session_state.get('year', 'N/A')}")
    st.warning(f"**Department:** {st.session_state.get('department', 'N/A')}")
    st.warning(f"**Venue:** {st.session_state.get('venue', 'N/A')}")

def render_admin_panel():
    st.sidebar.title("🔒 Admin Panel")
    password = st.sidebar.text_input("Enter Admin Password", type="password", key="admin_password")

    if password == ADMIN_PASSWORD:
        st.sidebar.success("Access Granted!")
        
        st.title("Admin Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["📊 Submissions", "🚨 Malpractice Logs", "📖 Question Bank"])

        with tab1:
            st.subheader("All Student Submissions")
            submissions = load_json_data(SUBMISSIONS_FILE)
            if not submissions:
                st.warning("No submissions have been recorded yet.")
            else:
                df = pd.DataFrame(submissions)
                st.metric("Total Submissions", len(df))
                display_df = df[['timestamp', 'student_name', 'register_number', 'year', 'department', 'venue', 'score']].copy()
                display_df['Score'] = display_df['score'].astype(str) + f" / {QUESTIONS_PER_QUIZ}"
                st.dataframe(display_df[['timestamp', 'student_name', 'register_number', 'year', 'department', 'venue', 'Score']], use_container_width=True)
                
                csv_data = []
                for sub in submissions:
                    base_info = {
                        "Timestamp": sub.get('timestamp', 'N/A'),
                        "Student Name": sub['student_name'],
                        "Register Number": sub['register_number'],
                        "Year": sub.get('year', 'N/A'),
                        "Department": sub.get('department', 'N/A'),
                        "Venue": sub.get('venue', 'N/A'),
                        "Final Score": sub['score'],
                    }
                    for i, q in enumerate(sub['questions']):
                        user_answer_idx = sub['answers'][i]
                        user_answer = q['options'][user_answer_idx] if user_answer_idx is not None else "Not Answered"
                        correct_answer = q['options'][q['correct']]
                        status = "Correct" if user_answer_idx == q['correct'] else "Wrong"
                        base_info[f"Q{i+1}"] = q['question']
                        base_info[f"Q{i+1}_Status"] = status
                        base_info[f"Q{i+1}_Your_Answer"] = user_answer
                        base_info[f"Q{i+1}_Correct_Answer"] = correct_answer
                    csv_data.append(base_info)
                
                csv_df = pd.DataFrame(csv_data)
                csv_bytes = csv_df.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="📊 Download Detailed Score Sheet (CSV)",
                    data=csv_bytes,
                    file_name="dt_analyse_quiz_scores.csv",
                    mime="text/csv",
                )
        
        with tab2:
            st.subheader("Malpractice Incidents")
            logs = load_json_data(MALPRACTICE_LOG_FILE)
            if not logs:
                st.info("No malpractice incidents have been logged. ✅")
            else:
                log_df = pd.DataFrame(logs)
                st.dataframe(log_df, use_container_width=True)

        with tab3:
            st.subheader("Full Question Bank")
            st.info(f"Total Questions: {len(QUESTION_BANK)}")
            
            # Show questions by topic
            topics = {
                "Data Synthesis & Pattern Recognition": list(range(0, 10)),
                "Root Cause Analysis & 5 Whys": list(range(10, 20)),
                "Affinity Mapping": list(range(20, 28)),
                "Problem Statement Formulation": list(range(28, 40)),
                "Conflict of Interest": list(range(40, 48)),
                "Problem Definition Canvas": list(range(48, 54)),
                "Case Studies Application": list(range(54, 62)),
                "Integration & Best Practices": list(range(62, 70))
            }
            
            for topic, indices in topics.items():
                with st.expander(f"**{topic}** ({len(indices)} questions)"):
                    for idx in indices:
                        q = QUESTION_BANK[idx]
                        st.markdown(f"**Q{q['id']}. {q['question']}**")
                        for i, opt in enumerate(q['options']):
                            if i == q['correct']:
                                st.markdown(f"   ✅ {opt}")
                            else:
                                st.markdown(f"   ⚪ {opt}")
                        st.markdown("---")

    elif password:
        st.sidebar.error("Incorrect Password.")

# --- Main App Logic ---
def main():
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'malpractice_detected' not in st.session_state:
        st.session_state.malpractice_detected = False

    if 'admin_password' in st.session_state and st.session_state.admin_password == ADMIN_PASSWORD:
        render_admin_panel()
    else:
        if st.session_state.malpractice_detected:
            render_malpractice_page()
        elif st.session_state.quiz_submitted:
            render_results_page()
        elif st.session_state.quiz_started:
            render_quiz_page()
        else:
            render_start_page()
        
        st.sidebar.empty()
        render_admin_panel()

if __name__ == "__main__":
    main()