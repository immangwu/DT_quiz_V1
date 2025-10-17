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
QUIZ_TITLE = "Manufacturing Processes Quiz"
COURSE_NAME = "Manufacturing Processes"
QUESTIONS_PER_QUIZ = 20
SUBMISSIONS_FILE = "submissions.json"
MALPRACTICE_LOG_FILE = "malpractice.json"
ADMIN_PASSWORD = "admin" # Replace with a more secure password in a real environment

# --- Question Database ---
QUESTION_BANK = [
    {"id": 1, "question": "What is the primary motion in a shaper machine?", "options": ["Rotary motion of the workpiece", "Reciprocating motion of the cutting tool", "Continuous rotation of the cutting tool", "Oscillating motion of the workpiece"], "correct": 1},
    {"id": 2, "question": "Which mechanism is commonly used for quick return in shapers?", "options": ["Gear train mechanism", "Belt and pulley system", "Crank and slotted link mechanism", "Hydraulic system"], "correct": 2},
    {"id": 3, "question": "What is the function of the clapper box in a shaper?", "options": ["To hold the workpiece firmly", "To provide cutting fluid", "To allow tool lifting during return stroke", "To control cutting speed"], "correct": 2},
    {"id": 4, "question": "In shaper operations, cutting occurs during:", "options": ["Both forward and return strokes", "Only the return stroke", "Only the forward stroke", "Neither stroke"], "correct": 2},
    {"id": 5, "question": "What type of cutting tool is used in shaper machines?", "options": ["Multi-point cutting tool", "Single-point cutting tool", "Abrasive wheel", "Milling cutter"], "correct": 1},
    {"id": 6, "question": "The stroke length in a shaper is determined by:", "options": ["Workpiece material", "Cutting tool material", "Position of the connecting rod", "Spindle speed"], "correct": 2},
    {"id": 7, "question": "Which surface can be machined using a shaper?", "options": ["Cylindrical surfaces only", "Flat surfaces only", "Flat, angular, and grooved surfaces", "Threaded surfaces only"], "correct": 2},
    {"id": 8, "question": "The cutting speed in shaper is measured in:", "options": ["RPM (revolutions per minute)", "m/min (meters per minute)", "Strokes per minute", "mm/tooth"], "correct": 1},
    {"id": 9, "question": "What is the main disadvantage of shaper machines?", "options": ["High initial cost", "Low production rate", "Complex operation", "High power consumption"], "correct": 1},
    {"id": 10, "question": "Which type of work is NOT suitable for shaper operations?", "options": ["Keyway cutting", "Surface finishing", "Deep hole drilling", "Angular surface machining"], "correct": 2},
    {"id": 11, "question": "What is the included angle of a standard twist drill?", "options": ["90°", "118°", "135°", "150°"], "correct": 1},
    {"id": 12, "question": "Which drilling operation is used to enlarge an existing hole?", "options": ["Drilling", "Reaming", "Boring", "Tapping"], "correct": 2},
    {"id": 13, "question": "What is the purpose of reaming?", "options": ["To create new holes", "To finish holes to precise dimensions", "To create threads", "To remove burrs only"], "correct": 1},
    {"id": 14, "question": "In tapping operations, what is cut into the hole?", "options": ["Keyways", "Internal threads", "External threads", "Splines"], "correct": 1},
    {"id": 15, "question": "What is the typical reaming allowance?", "options": ["5-10% of hole diameter", "0.1-0.4 mm", "1-2 mm", "10-15% of hole diameter"], "correct": 1},
    {"id": 16, "question": "Which tool is used for tapping operations?", "options": ["Twist drill", "Reamer", "Tap", "Boring bar"], "correct": 2},
    {"id": 17, "question": "What causes drill wandering?", "options": ["Too high cutting speed", "Improper point grinding", "Insufficient coolant", "Wrong drill material"], "correct": 1},
    {"id": 18, "question": "Core drilling is used for:", "options": ["Small diameter holes", "Large diameter holes", "Thread cutting", "Hole finishing"], "correct": 1},
    {"id": 19, "question": "What is the purpose of the chisel edge in a twist drill?", "options": ["To provide cutting action", "To guide the drill", "To clear chips", "To center the drill initially"], "correct": 3},
    {"id": 20, "question": "Boring operations are typically performed on:", "options": ["Drill press only", "Lathe machine", "Shaper machine", "Grinding machine"], "correct": 1},
    {"id": 21, "question": "What is the primary motion in milling operations?", "options": ["Reciprocating motion of cutter", "Linear motion of workpiece", "Rotary motion of cutter", "Oscillating motion of workpiece"], "correct": 2},
    {"id": 22, "question": "Which type of milling cutter is used for cutting slots?", "options": ["Face milling cutter", "End milling cutter", "Angle milling cutter", "Form milling cutter"], "correct": 1},
    {"id": 23, "question": "In up milling, the cutter rotates:", "options": ["In the same direction as workpiece feed", "Opposite to workpiece feed direction", "Perpendicular to workpiece feed", "At an angle to workpiece feed"], "correct": 1},
    {"id": 24, "question": "Face milling cutters are mounted on:", "options": ["Arbor", "Machine spindle directly", "Chuck", "Tailstock"], "correct": 1},
    {"id": 25, "question": "What is the advantage of down milling over up milling?", "options": ["Lower cutting forces", "Better surface finish", "Longer tool life", "All of the above"], "correct": 3},
    {"id": 26, "question": "Which milling cutter is used for machining T-slots?", "options": ["Plain milling cutter", "T-slot milling cutter", "Angular milling cutter", "Form milling cutter"], "correct": 1},
    {"id": 27, "question": "The cutting speed in milling is determined by:", "options": ["Feed rate only", "Spindle RPM and cutter diameter", "Depth of cut only", "Number of teeth only"], "correct": 1},
    {"id": 28, "question": "Which parameter is measured in mm/tooth in milling?", "options": ["Cutting speed", "Feed rate", "Depth of cut", "Spindle speed"], "correct": 1},
    {"id": 29, "question": "Form milling cutters are used to machine:", "options": ["Flat surfaces", "Specific contoured surfaces", "Angular surfaces only", "Cylindrical surfaces"], "correct": 1},
    {"id": 30, "question": "What is gang milling?", "options": ["Using multiple workpieces", "Using multiple cutters simultaneously", "Using high-speed cutting", "Using flood cooling"], "correct": 1},
    {"id": 31, "question": "Side milling cutters are primarily used for:", "options": ["Face milling operations", "Slot milling and side cutting", "Thread milling", "Gear cutting only"], "correct": 1},
    {"id": 32, "question": "The insert type milling cutters use:", "options": ["Brazed carbide tips", "Replaceable cutting inserts", "HSS cutting edges", "Diamond cutting edges"], "correct": 1},
    {"id": 33, "question": "Staggered tooth milling cutters are designed for:", "options": ["Heavy roughing cuts", "Finishing operations", "Gear cutting", "Thread milling"], "correct": 0},
    {"id": 34, "question": "What is the main advantage of carbide milling cutters?", "options": ["Lower cost", "Easy resharpening", "Higher cutting speeds", "Better vibration damping"], "correct": 2},
    {"id": 35, "question": "Shell end mills are mounted on:", "options": ["Direct spindle attachment", "Stub arbors", "Long arbors", "Collet chucks only"], "correct": 1},
    {"id": 36, "question": "What are the two main principles of gear cutting?", "options": ["Hobbing and shaping", "Forming and generation", "Milling and grinding", "Turning and boring"], "correct": 1},
    {"id": 37, "question": "In gear forming process, the cutter profile:", "options": ["Matches the gear tooth space", "Is different from tooth space", "Is constantly changing", "Requires multiple passes"], "correct": 0},
    {"id": 38, "question": "Which gear cutting method uses the generation principle?", "options": ["Form milling", "Broaching", "Hobbing", "Punching"], "correct": 2},
    {"id": 39, "question": "A gear hob is essentially a:", "options": ["Milling cutter", "Threading tool", "Worm with cutting edges", "Broaching tool"], "correct": 2},
    {"id": 40, "question": "In gear hobbing, the hob and gear blank rotate in a ratio of:", "options": ["1:1 always", "Based on hob threads and gear teeth", "2:1 always", "Based on module only"], "correct": 1},
    {"id": 41, "question": "Gear shaping process uses:", "options": ["Rotary cutting motion", "Reciprocating cutting motion", "Linear cutting motion", "Oscillating cutting motion"], "correct": 1},
    {"id": 42, "question": "The gear shaping cutter resembles:", "options": ["A hob", "A milling cutter", "A gear itself", "A broach"], "correct": 2},
    {"id": 43, "question": "What is the main advantage of gear shaping over hobbing?", "options": ["Higher production rate", "Can cut internal gears", "Better surface finish", "Lower cost"], "correct": 1},
    {"id": 44, "question": "Gear finishing operations include:", "options": ["Shaving only", "Grinding only", "Shaving, grinding, and lapping", "Honing only"], "correct": 2},
    {"id": 45, "question": "Gear shaving is performed:", "options": ["Before heat treatment", "After heat treatment", "During heat treatment", "Without regard to heat treatment"], "correct": 1},
    {"id": 46, "question": "In gear grinding, the grinding wheel:", "options": ["Has random abrasive arrangement", "Is dressed to match tooth profile", "Rotates slowly", "Uses flood cooling only"], "correct": 1},
    {"id": 47, "question": "What is the purpose of gear lapping?", "options": ["Rough cutting of teeth", "Final finishing for smooth operation", "Heat treatment process", "Tooth profile correction"], "correct": 1},
    {"id": 48, "question": "Form milling of gears requires:", "options": ["One cutter for all gears", "Different cutter for each gear", "Eight cutters for each module", "Sixteen cutters for each module"], "correct": 2},
    {"id": 49, "question": "The indexing operation in gear cutting:", "options": ["Is done manually always", "Positions the blank for each tooth", "Is not required in hobbing", "Both b and c"], "correct": 3},
    {"id": 50, "question": "Gear burnishing is a:", "options": ["Cutting operation", "Heat treatment process", "Cold finishing process", "Grinding operation"], "correct": 2}
]

# --- Helper Functions for Data Handling ---

def load_json_data(filepath):
    """Loads data from a JSON file."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json_data(filepath, data):
    """Saves data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def save_submission(submission_data):
    """Saves a single submission."""
    submissions = load_json_data(SUBMISSIONS_FILE)
    submissions.append(submission_data)
    save_json_data(SUBMISSIONS_FILE, submissions)

def save_malpractice_log(log_data):
    """Saves a single malpractice log."""
    logs = load_json_data(MALPRACTICE_LOG_FILE)
    logs.append(log_data)
    save_json_data(MALPRACTICE_LOG_FILE, logs)

# --- PDF Generation ---

def create_results_pdf(session_data):
    """Generates a PDF report for a completed quiz session and returns it as bytes."""
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


# --- Streamlit UI Components ---

def trigger_server_side_malpractice():
    """Flags malpractice on the server, logs it, and sets the session state."""
    if not st.session_state.get('malpractice_detected', False):
        st.session_state.malpractice_detected = True
        log_data = {
            "student_name": st.session_state.student_name,
            "register_number": st.session_state.register_number,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "User switched tabs or minimized the browser."
        }
        save_malpractice_log(log_data)
        # Clear sensitive quiz data
        st.session_state.pop('questions', None)
        st.session_state.pop('answers', None)

def render_start_page():
    """Displays the initial page for student information."""
    st.set_page_config(page_title=QUIZ_TITLE, layout="centered")
    st.title(f"🎓 {QUIZ_TITLE}")
    st.markdown(f"**Course:** {COURSE_NAME}")
    st.warning("⚠️ **Important:** Do not switch tabs or minimize the browser during the quiz. Doing so will automatically terminate your session.")
    st.markdown("---")
    
    with st.form("student_info_form"):
        student_name = st.text_input("Enter your Full Name", key="student_name_input")
        register_number = st.text_input("Enter your Register Number", key="register_number_input")
        submitted = st.form_submit_button(f"Start Quiz ({QUESTIONS_PER_QUIZ} Questions)")

        if submitted:
            if not student_name or not register_number:
                st.error("Please fill in both your name and register number.")
            else:
                st.session_state.student_name = student_name
                st.session_state.register_number = register_number
                st.session_state.quiz_started = True
                st.session_state.questions = random.sample(QUESTION_BANK, QUESTIONS_PER_QUIZ)
                st.session_state.answers = [None] * QUESTIONS_PER_QUIZ
                st.session_state.current_question_index = 0
                st.rerun()

def render_quiz_page():
    """Displays the quiz questions and navigation with malpractice detection."""
    # --- Malpractice Detection ---
    # This JS code will replace the page content if the user switches tabs
    malpractice_js = """
    <script>
    const handleVisibilityChange = () => {
        if (document.hidden) {
            // Set a flag in session storage so the server can verify on next interaction
            window.sessionStorage.setItem('malpractice', 'true');
            // Immediately terminate the quiz on the client-side for instant feedback
            document.body.innerHTML = `<div style='text-align: center; padding: 40px; color: red;'>
                <h1>Malpractice Detected</h1>
                <p>Your quiz has been terminated because you switched tabs or minimized the window.</p>
                <p>Please refresh the page.</p>
            </div>`;
        }
    };
    // Add the event listener. 'once: true' ensures it only fires once.
    window.addEventListener('visibilitychange', handleVisibilityChange, { once: true });
    </script>
    """
    st.components.v1.html(malpractice_js, height=0)

    # This component checks the session storage flag and reports it back to Python
    malpractice_flag = streamlit_js_eval(js_expressions="window.sessionStorage.getItem('malpractice')", key='malpractice_check')
    
    if malpractice_flag == 'true':
        trigger_server_side_malpractice()
        st.rerun() # Rerun to lock the user into the malpractice page
        return
        
    # --- Regular Quiz UI ---
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
    """Displays the final score and download options."""
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
        file_name=f"{st.session_state.register_number}_Quiz_Report.pdf",
        mime="application/pdf"
    )

    if st.button("↩️ Take Another Quiz"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

def render_malpractice_page():
    """Displays a screen indicating the quiz was terminated due to malpractice."""
    st.set_page_config(page_title="Quiz Terminated", layout="centered")
    st.title("🚨 Quiz Terminated 🚨")
    st.error(
        "Your quiz session has been terminated due to malpractice (switching tabs or minimizing the browser). "
        "This incident has been logged. Please contact your administrator."
    )
    st.warning(f"**Student:** {st.session_state.get('student_name', 'N/A')}")
    st.warning(f"**Register Number:** {st.session_state.get('register_number', 'N/A')}")

def render_admin_panel():
    """Displays the admin view in the sidebar."""
    st.sidebar.title("🔐 Admin Panel")
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
                display_df = df[['timestamp', 'student_name', 'register_number', 'score']].copy()
                display_df['Score'] = display_df['score'].astype(str) + f" / {QUESTIONS_PER_QUIZ}"
                st.dataframe(display_df[['timestamp', 'student_name', 'register_number', 'Score']], use_container_width=True)
                
                # Prepare detailed data for CSV
                csv_data = []
                for sub in submissions:
                    base_info = {
                        "Timestamp": sub.get('timestamp', 'N/A'),
                        "Student Name": sub['student_name'],
                        "Register Number": sub['register_number'],
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
                    file_name="complete_quiz_scores.csv",
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
            for i, q in enumerate(QUESTION_BANK):
                with st.expander(f"**{i+1}. {q['question']}**"):
                    st.markdown(f"**Correct Answer:** {q['options'][q['correct']]}")

    elif password:
        st.sidebar.error("Incorrect Password.")

# --- Main App Logic ---
def main():
    if 'quiz_started' not in st.session_state: st.session_state.quiz_started = False
    if 'quiz_submitted' not in st.session_state: st.session_state.quiz_submitted = False
    if 'malpractice_detected' not in st.session_state: st.session_state.malpractice_detected = False

    # Check for admin mode first
    if 'admin_password' in st.session_state and st.session_state.admin_password == ADMIN_PASSWORD:
         render_admin_panel()
    else:
        # Routing for student view
        if st.session_state.malpractice_detected:
            render_malpractice_page()
        elif st.session_state.quiz_submitted:
            render_results_page()
        elif st.session_state.quiz_started:
            render_quiz_page()
        else:
            render_start_page()
        # Always allow admin login attempt
        st.sidebar.empty() # Clear sidebar if not in admin mode
        render_admin_panel()


if __name__ == "__main__":
    main()

