# app.py

import streamlit as st
import json
import random
import datetime
import pandas as pd
from io import BytesIO
import time

# --- Third-party libraries ---
import gspread
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

# --- PDF Generation Libraries ---
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# =====================================================================================
# --- 📝 CONFIGURATION & CONSTANTS ---
# =====================================================================================
APP_TITLE = "Manufacturing Technology Quiz System"
COURSE_NAME = "Manufacturing Technology"
QUESTIONS_PER_QUIZ = 20
QUIZ_DURATION_MINUTES = 7
QUIZ_DURATION_SECONDS = QUIZ_DURATION_MINUTES * 60
ADMIN_USERNAME = "immangwu"
ADMIN_PASSWORD = "jesus"

# =====================================================================================
# --- 🧠 QUESTION BANKS ---
# =====================================================================================

# Quiz 1: Design Thinking
QUIZ_1_BANK = [
    {"id": 1, "question": "What is the primary goal of the 'Empathize' phase in Design Thinking?", "options": ["Brainstorming solutions", "Understanding user needs and perspectives", "Creating a final product", "Testing prototypes"], "correct": 1},
    {"id": 2, "question": "The '5 Whys' technique is primarily used for what purpose?", "options": ["Generating ideas", "Creating user personas", "Identifying the root cause of a problem", "Prototyping"], "correct": 2},
    {"id": 3, "question": "What is a 'prototype' in the context of Design Thinking?", "options": ["The final, polished product", "A detailed business plan", "A simple, low-cost model to test ideas", "A marketing strategy"], "correct": 2},
    {"id": 4, "question": "Which of the following best describes 'synthesis'?", "options": ["Breaking down complex data", "Organizing research findings into meaningful patterns and insights", "Ignoring user feedback", "Focusing only on quantitative data"], "correct": 1},
    {"id": 5, "question": "A good 'How Might We' (HMW) question should be:", "options": ["So narrow it suggests a specific solution", "Too broad to be actionable", "Generative and allow for multiple possible solutions", "Focused on business metrics only"], "correct": 2},
    {"id": 6, "question": "What is a key principle of the 'Ideate' phase?", "options": ["Focus on quality over quantity", "Defer judgment and encourage wild ideas", "Immediately discard unfeasible ideas", "Only one person should contribute ideas"], "correct": 1},
    {"id": 7, "question": "What is an 'Affinity Diagram' used for?", "options": ["Calculating project costs", "Grouping large amounts of data into themes", "Writing code", "Final user testing"], "correct": 1},
    {"id": 8, "question": "The 'Test' phase is for:", "options": ["Selling the product to customers", "Getting feedback on prototypes from real users", "Finalizing the product design without changes", "Arguing with users about their feedback"], "correct": 1},
    {"id": 9, "question": "A 'Point of View' (POV) statement is composed of:", "options": ["User, Need, and Insight", "Problem, Solution, and Business Goal", "Feature, Advantage, and Benefit", "Idea, Prototype, and Test"], "correct": 0},
    {"id": 10, "question": "What does it mean for a problem statement to be 'human-centered'?", "options": ["It focuses on technical limitations", "It focuses on the needs and goals of the people you are designing for", "It is written by a robot", "It prioritizes the company's profit above all else"], "correct": 1},
    {"id": 11, "question": "Which of these is NOT a brainstorming rule?", "options": ["One conversation at a time", "Go for quantity", "Criticize every idea", "Build on the ideas of others"], "correct": 2},
    {"id": 12, "question": "A user 'persona' is a:", "options": ["Real user hired for testing", "Detailed legal document", "Fictional character representing a target user group", "Software for creating user interfaces"], "correct": 2},
    {"id": 13, "question": "What is the main benefit of creating low-fidelity prototypes first?", "options": ["They look more professional", "They are expensive and show commitment", "They are quick and cheap, allowing for fast iteration", "They are fully functional"], "correct": 2},
    {"id": 14, "question": "Design Thinking is best described as a:", "options": ["Linear, rigid process", "Problem-solving approach focused on users", "Marketing framework", "Software development methodology"], "correct": 1},
    {"id": 15, "question": "In the 'Define' phase, the goal is to:", "options": ["Create a clear and actionable problem statement", "Come up with as many ideas as possible", "Build the final product", "Observe users in their environment"], "correct": 0},
    {"id": 16, "question": "An 'Empathy Map' helps the team to:", "options": ["Plan the project timeline", "Gain a deeper understanding of a user's experience", "Write the code for the app", "Secure funding from investors"], "correct": 1},
    {"id": 17, "question": "'Fail fast, fail often' is a mantra that encourages:", "options": ["Giving up easily", "Learning quickly from low-cost experiments", "Delivering a poor-quality product", "Ignoring failures"], "correct": 1},
    {"id": 18, "question": "What is a 'user journey map'?", "options": ["A map to the user's house", "A visualization of a user's interactions with a product or service", "A list of software bugs", "A financial forecast"], "correct": 1},
    {"id": 19, "question": "The double diamond model represents which two phases of thinking?", "options": ["Fast and Slow", "Good and Bad", "Simple and Complex", "Divergent and Convergent"], "correct": 3},
    {"id": 20, "question": "The ultimate goal of Design Thinking is to:", "options": ["Create innovative solutions that meet user needs", "Make as much money as possible", "Use the latest technology", "Follow a process without deviation"], "correct": 0}
]

# Quiz 2: Shaper Machine (Placeholder - Add actual questions)
QUIZ_2_BANK = [
    {"id": 1, "question": "What is the primary motion in a shaper machine?", "options": ["Rotary motion", "Reciprocating motion", "Circular motion", "Helical motion"], "correct": 1},
    {"id": 2, "question": "The cutting stroke in a shaper is:", "options": ["Forward stroke", "Return stroke", "Both strokes", "Neither stroke"], "correct": 0},
    {"id": 3, "question": "Which mechanism is commonly used in shapers for return stroke?", "options": ["Quick return mechanism", "Slow return mechanism", "Uniform speed mechanism", "Variable speed mechanism"], "correct": 0},
    {"id": 4, "question": "The tool head of a shaper can be:", "options": ["Only vertical", "Only horizontal", "Swiveled at an angle", "Fixed permanently"], "correct": 2},
    {"id": 5, "question": "Feed in a shaper machine is provided during:", "options": ["Cutting stroke", "Return stroke", "Both strokes", "Manually only"], "correct": 1},
    {"id": 6, "question": "Crank and slotted link mechanism is used in shapers for:", "options": ["Feeding", "Quick return motion", "Clamping workpiece", "Tool changing"], "correct": 1},
    {"id": 7, "question": "The maximum length of stroke in a shaper depends on:", "options": ["Ram length", "Table size", "Motor power", "Tool size"], "correct": 0},
    {"id": 8, "question": "Which type of shaper has the ram positioned horizontally?", "options": ["Vertical shaper", "Horizontal shaper", "Universal shaper", "Special purpose shaper"], "correct": 1},
    {"id": 9, "question": "The stroke length in a shaper can be adjusted by:", "options": ["Changing motor speed", "Adjusting crank pin position", "Replacing the ram", "Changing the tool"], "correct": 1},
    {"id": 10, "question": "Shaper machines are primarily used for:", "options": ["Cylindrical surfaces", "Flat surfaces", "Spherical surfaces", "Threaded surfaces"], "correct": 1},
    {"id": 11, "question": "The table of a shaper can move in how many directions?", "options": ["One direction", "Two directions (cross and vertical)", "Three directions", "Cannot move"], "correct": 1},
    {"id": 12, "question": "Which operation CANNOT be performed on a shaper?", "options": ["Planing flat surfaces", "Cutting keyways", "Turning cylindrical parts", "Cutting grooves"], "correct": 2},
    {"id": 13, "question": "The vice on a shaper table is used for:", "options": ["Holding the cutting tool", "Clamping the workpiece", "Adjusting stroke length", "Controlling speed"], "correct": 1},
    {"id": 14, "question": "Compared to a planer, a shaper is more suitable for:", "options": ["Large workpieces", "Small workpieces", "Heavy workpieces", "Long workpieces"], "correct": 1},
    {"id": 15, "question": "The cutting tool in a shaper is generally made of:", "options": ["Mild steel", "High speed steel or carbide", "Aluminum", "Copper"], "correct": 1},
    {"id": 16, "question": "In a shaper, the ram carries:", "options": ["The workpiece", "The tool head", "The table", "The motor"], "correct": 1},
    {"id": 17, "question": "A vertical shaper is also known as a:", "options": ["Planer", "Slotter", "Broaching machine", "Boring machine"], "correct": 1},
    {"id": 18, "question": "The speed of cutting stroke is generally:", "options": ["Faster than return stroke", "Slower than return stroke", "Same as return stroke", "Variable and uncontrolled"], "correct": 1},
    {"id": 19, "question": "Angular cuts can be made on a shaper by:", "options": ["Tilting the workpiece", "Swiveling the tool head", "Both a and b", "Cannot make angular cuts"], "correct": 2},
    {"id": 20, "question": "The stroke per minute in a shaper determines:", "options": ["Feed rate", "Production rate", "Surface finish", "Tool life"], "correct": 1}
]

# Quiz 3: Abrasive Processes and Broaching
QUIZ_3_BANK = [
    {"id": 1, "question": "What does the first letter in grinding wheel specification indicate?", "options": ["Grain size", "Abrasive type", "Bond type", "Wheel hardness"], "correct": 1},
    {"id": 2, "question": "Which abrasive is most commonly used for grinding steel?", "options": ["Silicon carbide (C)", "Aluminum oxide (A)", "Diamond (D)", "Cubic boron nitride (B)"], "correct": 1},
    {"id": 3, "question": "What does a grain size number of 60 indicate?", "options": ["Very coarse grain", "Medium grain", "Fine grain", "Very fine grain"], "correct": 1},
    {"id": 4, "question": "Which grinding wheel grade indicates a hard wheel?", "options": ["F, G, H", "I, J, K", "L, M, N", "S, T, U"], "correct": 3},
    {"id": 5, "question": "What does the structure number in wheel specification represent?", "options": ["Hardness of the wheel", "Spacing between abrasive grains", "Type of bond used", "Manufacturing process"], "correct": 1},
    {"id": 6, "question": "Vitrified bond is represented by which letter?", "options": ["R", "B", "V", "E"], "correct": 2},
    {"id": 7, "question": "For grinding soft materials, which type of wheel should be selected?", "options": ["Soft wheel with coarse grain", "Hard wheel with fine grain", "Hard wheel with coarse grain", "Soft wheel with fine grain"], "correct": 2},
    {"id": 8, "question": "Silicon carbide abrasive is best suited for grinding:", "options": ["High carbon steel", "Cast iron and non-ferrous metals", "Tool steel", "Stainless steel"], "correct": 1},
    {"id": 9, "question": "What happens when a grinding wheel is too soft for the application?", "options": ["Poor surface finish", "Excessive wheel wear", "Both a and b", "Wheel cracking"], "correct": 2},
    {"id": 10, "question": "Resinoid bond wheels are typically used for:", "options": ["Precision grinding", "Heavy stock removal", "Surface grinding only", "Internal grinding only"], "correct": 1},
    {"id": 11, "question": "What does CBN stand for in grinding wheel specifications?", "options": ["Carbon Boron Nitride", "Cubic Boron Nitride", "Ceramic Bond Nitride", "Coated Boron Nitride"], "correct": 1},
    {"id": 12, "question": "For grinding carbide tools, which abrasive is most suitable?", "options": ["Aluminum oxide", "Silicon carbide", "Diamond", "Emery"], "correct": 2},
    {"id": 13, "question": "In cylindrical grinding, the workpiece is held between:", "options": ["Chuck and tailstock", "Centers", "Collet and chuck", "Both a and b are possible"], "correct": 3},
    {"id": 14, "question": "What is the main advantage of centerless grinding?", "options": ["Higher accuracy", "No need for centers or chucks", "Better surface finish", "Lower cost setup"], "correct": 1},
    {"id": 15, "question": "In centerless grinding, the workpiece is supported by:", "options": ["Centers", "Chuck", "Work rest blade", "Magnetic chuck"], "correct": 2},
    {"id": 16, "question": "Surface grinding is primarily used for machining:", "options": ["Cylindrical surfaces", "Flat surfaces", "Internal surfaces", "Threaded surfaces"], "correct": 1},
    {"id": 17, "question": "In broaching, cutting is achieved by:", "options": ["Rotary motion of the tool", "Linear motion of a multi-tooth tool", "Reciprocating motion", "Oscillating motion"], "correct": 1},
    {"id": 18, "question": "What is the main advantage of broaching?", "options": ["Low tooling cost", "High production rate and accuracy", "Versatility", "Simple setup"], "correct": 1},
    {"id": 19, "question": "In broach construction, each successive tooth is:", "options": ["Identical to the previous tooth", "Slightly larger than the previous tooth", "Smaller than the previous tooth", "Randomly sized"], "correct": 1},
    {"id": 20, "question": "Push broaching is suitable for:", "options": ["Long workpieces", "Short workpieces with simple shapes", "Internal surfaces only", "External surfaces only"], "correct": 1}
]

# Quiz 4: Numerical Control and CNC
QUIZ_4_BANK = [
    {"id": 1, "question": "What does NC stand for in machine tools?", "options": ["New Control", "Numerical Control", "Network Control", "Normal Control"], "correct": 1},
    {"id": 2, "question": "The main difference between NC and CNC is:", "options": ["NC uses computers, CNC doesn't", "CNC uses computers, NC uses hardwired logic", "No difference between them", "NC is newer than CNC"], "correct": 1},
    {"id": 3, "question": "Which type of CNC system allows program editing at the machine?", "options": ["Point-to-point system", "Straight cut system", "Conversational programming system", "CAM system only"], "correct": 2},
    {"id": 4, "question": "In a CNC system, the MCU stands for:", "options": ["Machine Control Unit", "Memory Control Unit", "Motor Control Unit", "Manual Control Unit"], "correct": 0},
    {"id": 5, "question": "What type of control system is used in modern CNC machines?", "options": ["Open loop control only", "Closed loop control only", "Both open and closed loop", "Manual control only"], "correct": 2},
    {"id": 6, "question": "Point-to-point NC systems are suitable for:", "options": ["Contouring operations", "Drilling and boring operations", "Complex curve machining", "Surface milling"], "correct": 1},
    {"id": 7, "question": "Continuous path NC systems are used for:", "options": ["Drilling operations only", "Point drilling", "Contouring and profiling", "Simple positioning"], "correct": 2},
    {"id": 8, "question": "The resolution of a CNC system refers to:", "options": ["Screen display quality", "Smallest programmable increment", "Maximum feed rate", "Spindle speed range"], "correct": 1},
    {"id": 9, "question": "Which feedback device is commonly used in CNC machines?", "options": ["Potentiometer", "Encoder", "Tachometer", "All of the above"], "correct": 3},
    {"id": 10, "question": "DNC stands for:", "options": ["Direct Numerical Control", "Distributed Numerical Control", "Dynamic Numerical Control", "Both a and b"], "correct": 3},
    {"id": 11, "question": "The typical resolution of modern CNC systems is:", "options": ["0.1 mm", "0.01 mm", "0.001 mm", "0.0001 mm"], "correct": 2},
    {"id": 12, "question": "Which of the following is NOT a type of CNC interpolation?", "options": ["Linear interpolation", "Circular interpolation", "Parabolic interpolation", "Helical interpolation"], "correct": 2},
    {"id": 13, "question": "G00 in CNC programming represents:", "options": ["Linear interpolation", "Rapid positioning", "Circular interpolation clockwise", "Dwell command"], "correct": 1},
    {"id": 14, "question": "G01 in CNC programming represents:", "options": ["Rapid positioning", "Linear interpolation at feed rate", "Circular interpolation", "Return to home position"], "correct": 1},
    {"id": 15, "question": "M06 code is used for:", "options": ["Spindle start", "Tool change", "Coolant on", "Program stop"], "correct": 1},
    {"id": 16, "question": "VMC stands for:", "options": ["Variable Machining Center", "Vertical Machining Center", "Virtual Machining Center", "Versatile Machining Center"], "correct": 1},
    {"id": 17, "question": "The ATC in machining centers refers to:", "options": ["Automatic Temperature Control", "Automatic Tool Changer", "Advanced Turning Center", "Automatic Threading Cycle"], "correct": 1},
    {"id": 18, "question": "A 5-axis machining center can machine:", "options": ["Simple flat surfaces only", "Complex 3D surfaces in single setup", "Only cylindrical parts", "Two surfaces simultaneously"], "correct": 1},
    {"id": 19, "question": "In CNC programming, the F word specifies:", "options": ["Feed rate", "Spindle speed", "Tool number", "Coordinate position"], "correct": 0},
    {"id": 20, "question": "The S word in CNC programming specifies:", "options": ["Feed rate", "Spindle speed", "Sequence number", "Safety position"], "correct": 1}
]

QUIZ_BANKS = {
    "Quiz 1: Design Thinking": QUIZ_1_BANK,
    "Quiz 2: Shaper Machine": QUIZ_2_BANK,
    "Quiz 3: Abrasive Processes & Broaching": QUIZ_3_BANK,
    "Quiz 4: CNC & Numerical Control": QUIZ_4_BANK
}

# =====================================================================================
# --- ☁️ GOOGLE SHEETS HELPER FUNCTIONS ---
# =====================================================================================

def get_gspread_client():
    """Connects to Google Sheets using credentials from Streamlit secrets."""
    try:
        return gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {e}")
        return None

def initialize_spreadsheet():
    """Initializes the spreadsheet with required sheets and headers."""
    try:
        client = get_gspread_client()
        if not client:
            return False
        
        spreadsheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet_url"])
        
        # Define required sheets and their headers
        sheets_config = {
            "Quiz1": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "Quiz2": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "Quiz3": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "Quiz4": ["timestamp", "student_name", "register_number", "score", "total_questions", "answers_json", "questions_json"],
            "MalpracticeLogs": ["timestamp", "student_name", "register_number", "quiz_name", "event"]
        }
        
        existing_sheets = [ws.title for ws in spreadsheet.worksheets()]
        
        for sheet_name, headers in sheets_config.items():
            if sheet_name not in existing_sheets:
                # Create new sheet
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                worksheet.append_row(headers)
            else:
                # Check if headers exist
                worksheet = spreadsheet.worksheet(sheet_name)
                existing_headers = worksheet.row_values(1)
                if not existing_headers or existing_headers != headers:
                    worksheet.clear()
                    worksheet.append_row(headers)
        
        return True
    except Exception as e:
        st.error(f"❌ Error initializing spreadsheet: {e}")
        return False

def save_to_gsheet(sheet_name, data_dict):
    """Saves a dictionary of data as a new row in the specified Google Sheet."""
    try:
        client = get_gspread_client()
        if not client:
            return False
        
        spreadsheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet_url"])
        ws = spreadsheet.worksheet(sheet_name)
        header = ws.row_values(1)
        row_to_insert = [data_dict.get(key, "N/A") for key in header]
        ws.append_row(row_to_insert, value_input_option='USER_ENTERED')
        return True
    except Exception as e:
        st.error(f"❌ Could not write to Google Sheets: {e}")
        return False

def get_sheet_data(sheet_name):
    """Retrieves all data from a specified sheet."""
    try:
        client = get_gspread_client()
        if not client:
            return None
        
        spreadsheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet_url"])
        ws = spreadsheet.worksheet(sheet_name)
        return pd.DataFrame(ws.get_all_records())
    except Exception as e:
        st.error(f"❌ Error reading from sheet {sheet_name}: {e}")
        return None

# =====================================================================================
# --- 📄 PDF GENERATION FUNCTIONS ---
# =====================================================================================

def create_results_pdf(session_data):
    """Generates a detailed PDF report for a single student."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['h1'], alignment=TA_CENTER, fontSize=18, textColor=colors.HexColor('#1f4788'))
    story.append(Paragraph(COURSE_NAME, title_style))
    story.append(Paragraph(f"{session_data.get('quiz_name', 'Quiz')} - Performance Report", styles['h2']))
    story.append(Spacer(1, 0.25 * inch))
    
    # Student Information
    student_info = [
        ['Student Name:', session_data.get('student_name', 'N/A')],
        ['Register Number:', session_data.get('register_number', 'N/A')],
        ['Quiz:', session_data.get('quiz_name', 'N/A')],
        ['Date & Time:', session_data.get('timestamp', 'N/A')],
        ['Score:', f"<b>{session_data.get('score', '0')} / {session_data.get('total_questions', 20)}</b>"],
        ['Percentage:', f"<b>{(session_data.get('score', 0) / session_data.get('total_questions', 20) * 100):.2f}%</b>"]
    ]
    
    info_table = Table(student_info, colWidths=[1.5 * inch, 4.5 * inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4 * inch))
    
    # Detailed Answer Sheet
    story.append(Paragraph("Detailed Answer Sheet", styles['h3']))
    story.append(Spacer(1, 0.2 * inch))
    
    results_data = [['Q#', 'Your Answer', 'Correct Answer', 'Result']]
    questions = session_data.get('questions', [])
    answers = session_data.get('answers', [])
    
    for i, q in enumerate(questions):
        user_answer_idx = answers[i]
        user_answer_text = q['options'][user_answer_idx] if user_answer_idx is not None else "Not Answered"
        correct_answer_text = q['options'][q['correct']]
        result = "✓ Correct" if user_answer_idx == q['correct'] else "✗ Wrong"
        
        results_data.append([
            str(i + 1),
            Paragraph(user_answer_text, styles['Normal']),
            Paragraph(correct_answer_text, styles['Normal']),
            result
        ])
    
    results_table = Table(results_data, colWidths=[0.4*inch, 2.4*inch, 2.4*inch, 0.8*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    # Color coding rows
    for i, row in enumerate(results_data[1:], start=1):
        if row[-1] == "✓ Correct":
            results_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightgreen)]))
        else:
            results_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.lightpink)]))
    
    story.append(results_table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def create_question_bank_pdf(quiz_name, question_bank):
    """Generates a PDF of the question bank for a specific quiz."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['h1'], alignment=TA_CENTER, fontSize=18)
    story.append(Paragraph(f"{quiz_name} - Question Bank", title_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Questions
    for idx, q in enumerate(question_bank, 1):
        # Question
        q_text = f"<b>Q{idx}. {q['question']}</b>"
        story.append(Paragraph(q_text, styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        # Options
        for opt_idx, option in enumerate(q['options']):
            opt_letter = chr(97 + opt_idx)  # a, b, c, d
            opt_text = f"{opt_letter}) {option}"
            if opt_idx == q['correct']:
                opt_text = f"<b><font color='green'>{opt_text} ✓</font></b>"
            story.append(Paragraph(opt_text, styles['Normal']))
        
        story.append(Spacer(1, 0.2 * inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =====================================================================================
# --- 🖥️ UI RENDERING FUNCTIONS ---
# =====================================================================================

def render_quiz_selection_page():
    """Displays quiz selection interface."""
    st.set_page_config(page_title=APP_TITLE, layout="centered", page_icon="📚")
    
    # Check spreadsheet connection
    with st.spinner("🔄 Connecting to database..."):
        connection_status = initialize_spreadsheet()
    
    if connection_status:
        st.success("✅ Connected to database successfully!", icon="✅")
    else:
        st.error("❌ Failed to connect to database. Please check your configuration.", icon="🚨")
        st.stop()
    
    st.title(f"📚 {APP_TITLE}")
    st.markdown(f"**Course:** {COURSE_NAME}")
    st.markdown("---")
    
    st.subheader("🎯 Select Your Quiz")
    
    quiz_options = list(QUIZ_BANKS.keys())
    selected_quiz = st.selectbox("Choose a quiz to attempt:", [""] + quiz_options)
    
    if selected_quiz:
        st.info(f"**Duration:** {QUIZ_DURATION_MINUTES} minutes | **Questions:** {QUESTIONS_PER_QUIZ}")
        st.warning("⚠️ **Important:** Do not switch tabs or minimize the browser during the quiz. This will automatically terminate your session.", icon="🚨")
        
        if st.button("Proceed to Quiz", type="primary", use_container_width=True):
            st.session_state.selected_quiz = selected_quiz
            st.session_state.page = "student_info"
            st.rerun()

def render_student_info_page():
    """Displays student information form."""
    st.set_page_config(page_title="Student Information", layout="centered", page_icon="📝")
    
    st.title("📝 Student Information")
    st.markdown(f"**Quiz:** {st.session_state.selected_quiz}")
    st.markdown("---")
    
    with st.form("student_info_form"):
        st.subheader("Enter Your Details")
        student_name = st.text_input("Full Name *", placeholder="Enter your full name")
        register_number = st.text_input("Register Number *", placeholder="Enter your register number")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Start Quiz", type="primary", use_container_width=True)
        with col2:
            back = st.form_submit_button("← Back", use_container_width=True)
        
        if back:
            st.session_state.page = "quiz_selection"
            st.rerun()
        
        if submitted:
            if not all([student_name.strip(), register_number.strip()]):
                st.error("❌ Please fill in all required fields marked with *")
            else:
                st.session_state.student_name = student_name.strip()
                st.session_state.register_number = register_number.strip()
                st.session_state.quiz_started = True
                st.session_state.start_time = time.time()
                
                # Select random questions from the bank
                quiz_bank = QUIZ_BANKS[st.session_state.selected_quiz]
                st.session_state.questions = random.sample(quiz_bank, min(QUESTIONS_PER_QUIZ, len(quiz_bank)))
                st.session_state.answers = [None] * len(st.session_state.questions)
                st.session_state.current_question_index = 0
                st.session_state.page = "quiz"
                st.rerun()

def render_quiz_page():
    """Displays the main quiz interface with timer and questions."""
    st.set_page_config(page_title="Quiz in Progress", layout="centered", page_icon="✍️")
    
    # Malpractice detection script
    malpractice_js = """
    <script>
    const handleVisibilityChange = () => {
        if (document.hidden) {
            window.sessionStorage.setItem('malpractice', 'true');
            document.body.innerHTML = `<div style='text-align: center; padding: 40px; color: red;'><h1>🚨 Quiz Terminated</h1><p>Malpractice detected. Your session has been terminated.</p></div>`;
        }
    };
    window.addEventListener('visibilitychange', handleVisibilityChange, { once: true });
    </script>
    """
    st.components.v1.html(malpractice_js, height=0)

    # Check for malpractice
    if streamlit_js_eval(js_expressions="window.sessionStorage.getItem('malpractice')", key='malpractice_check') == 'true':
        if not st.session_state.get('malpractice_detected', False):
            st.session_state.malpractice_detected = True
            
            # Log malpractice
            log_data = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "student_name": st.session_state.student_name,
                "register_number": st.session_state.register_number,
                "quiz_name": st.session_state.selected_quiz,
                "event": "Tab switch/Browser minimized"
            }
            save_to_gsheet("MalpracticeLogs", log_data)
            st.session_state.page = "malpractice"
        st.rerun()
        return

    # Timer with auto-refresh
    st_autorefresh(interval=1000, limit=None, key="quiz_timer")
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = QUIZ_DURATION_SECONDS - elapsed_time
    
    if remaining_time <= 0:
        st.toast("⏳ Time's up! Auto-submitting your quiz...", icon="⏰")
        time.sleep(2)
        st.session_state.quiz_submitted = True
        st.session_state.page = "results"
        st.rerun()
        return

    # Header with timer
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(st.session_state.selected_quiz)
    with col2:
        mins, secs = divmod(int(remaining_time), 60)
        timer_color = "🟢" if remaining_time > 120 else "🟡" if remaining_time > 60 else "🔴"
        st.metric(f"{timer_color} Time Left", f"{mins:02d}:{secs:02d}")

    # Progress bar
    progress = (st.session_state.current_question_index + 1) / len(st.session_state.questions)
    st.progress(progress)
    
    # Question display
    q_index = st.session_state.current_question_index
    question_data = st.session_state.questions[q_index]
    
    st.markdown(f"### Question {q_index + 1} of {len(st.session_state.questions)}")
    st.markdown(f"**{question_data['question']}**")
    st.markdown("")
    
    # Answer options - Fix for the None error
    saved_answer_index = st.session_state.answers[q_index]
    
    # Create radio button with proper index handling
    if saved_answer_index is not None:
        default_index = saved_answer_index
    else:
        default_index = 0
        # Don't save the default selection until user interacts
    
    user_choice_label = st.radio(
        "Select your answer:",
        options=question_data['options'],
        index=default_index,
        key=f"q_{q_index}_{st.session_state.start_time}"  # Unique key
    )
    
    # Save the selected answer
    st.session_state.answers[q_index] = question_data['options'].index(user_choice_label)
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=(q_index == 0)):
            st.session_state.current_question_index -= 1
            st.rerun()
    
    with col2:
        # Question navigator
        st.markdown(f"<center>Question {q_index + 1}/{len(st.session_state.questions)}</center>", unsafe_allow_html=True)
    
    with col3:
        if q_index < len(st.session_state.questions) - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                st.session_state.quiz_submitted = True
                st.session_state.page = "results"
                st.rerun()
    
    # Question overview
    st.markdown("---")
    st.markdown("**Question Overview:**")
    answered = sum(1 for ans in st.session_state.answers if ans is not None)
    st.info(f"Answered: {answered} / {len(st.session_state.questions)}")

def render_results_page():
    """Displays final results and allows PDF download."""
    st.set_page_config(page_title="Quiz Results", layout="centered", page_icon="🎉")
    
    # Calculate score
    score = sum(1 for i, q in enumerate(st.session_state.questions) 
                if st.session_state.answers[i] is not None and st.session_state.answers[i] == q['correct'])
    
    total_questions = len(st.session_state.questions)
    percentage = (score / total_questions) * 100
    
    # Display results
    st.balloons()
    st.title("🎉 Quiz Submitted Successfully!")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total_questions}")
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    with col3:
        grade = "Excellent" if percentage >= 80 else "Good" if percentage >= 60 else "Pass" if percentage >= 40 else "Needs Improvement"
        st.metric("Grade", grade)
    
    # Save to Google Sheets
    if not st.session_state.get('submission_saved', False):
        quiz_number = st.session_state.selected_quiz.split(":")[0].replace("Quiz ", "").strip()
        sheet_name = f"Quiz{quiz_number}"
        
        submission_data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student_name": st.session_state.student_name,
            "register_number": st.session_state.register_number,
            "score": score,
            "total_questions": total_questions,
            "answers_json": json.dumps(st.session_state.answers),
            "questions_json": json.dumps([{"question": q["question"], "options": q["options"], "correct": q["correct"]} for q in st.session_state.questions])
        }
        
        if save_to_gsheet(sheet_name, submission_data):
            st.success("✅ Your results have been saved successfully!", icon="💾")
            st.session_state.submission_saved = True
        else:
            st.warning("⚠️ Could not save results to database. Please contact administrator.")
    
    # Generate and offer PDF download
    st.markdown("---")
    st.subheader("📄 Download Your Report")
    
    pdf_data = {
        'quiz_name': st.session_state.selected_quiz,
        'student_name': st.session_state.student_name,
        'register_number': st.session_state.register_number,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'score': score,
        'total_questions': total_questions,
        'questions': st.session_state.questions,
        'answers': st.session_state.answers
    }
    
    pdf_bytes = create_results_pdf(pdf_data)
    st.download_button(
        label="📥 Download Performance Report (PDF)",
        data=pdf_bytes,
        file_name=f"{st.session_state.register_number}_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    st.markdown("---")
    if st.button("🔄 Take Another Quiz", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_malpractice_page():
    """Displays malpractice termination screen."""
    st.set_page_config(page_title="Quiz Terminated", layout="centered", page_icon="🚫")
    
    st.title("🚨 Quiz Terminated")
    st.error("Your quiz session has been terminated due to malpractice detection (tab switching or browser minimization).", icon="🚫")
    
    st.markdown("---")
    st.markdown("### Incident Details")
    st.info(f"""
    **Student Name:** {st.session_state.get('student_name', 'N/A')}  
    **Register Number:** {st.session_state.get('register_number', 'N/A')}  
    **Quiz:** {st.session_state.get('selected_quiz', 'N/A')}  
    **Time:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """)
    
    st.warning("This incident has been logged and reported to the administrator.")
    
    if st.button("Return to Home", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def render_admin_panel():
    """Displays admin panel in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.title("🔐 Admin Access")
    
    with st.sidebar.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")
    
    if login:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.session_state.page = "admin_dashboard"
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid credentials")

def render_admin_dashboard():
    """Displays the full admin dashboard."""
    st.set_page_config(page_title="Admin Dashboard", layout="wide", page_icon="👨‍💼")
    
    st.title("👨‍💼 Admin Dashboard")
    st.markdown("---")
    
    # Logout button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.page = "quiz_selection"
            st.rerun()
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Quiz Results", "🚨 Malpractice Logs", "📚 Question Banks"])
    
    with tab1:
        st.subheader("Quiz Results")
        
        # Quiz selection
        quiz_selector = st.selectbox("Select Quiz:", ["Quiz1", "Quiz2", "Quiz3", "Quiz4"])
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
        
        # Fetch data
        with st.spinner("Loading data..."):
            df = get_sheet_data(quiz_selector)
        
        if df is not None and not df.empty:
            st.metric("Total Submissions", len(df))
            
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_score = df['score'].mean()
                st.metric("Average Score", f"{avg_score:.2f}")
            with col2:
                max_score = df['score'].max()
                st.metric("Highest Score", f"{max_score}")
            with col3:
                min_score = df['score'].min()
                st.metric("Lowest Score", f"{min_score}")
            
            # Display data table
            st.markdown("### Recent Submissions")
            display_df = df[['timestamp', 'student_name', 'register_number', 'score', 'total_questions']].copy()
            display_df['percentage'] = (display_df['score'] / display_df['total_questions'] * 100).round(2)
            st.dataframe(display_df, use_container_width=True)
            
            # Download all results
            csv_bytes = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download All Results (CSV)",
                data=csv_bytes,
                file_name=f"{quiz_selector}_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Individual student report download
            st.markdown("### Individual Student Reports")
            student_names = df['student_name'].tolist()
            selected_student = st.selectbox("Select Student:", student_names)
            
            if st.button("📄 Download Student Report (PDF)"):
                # Find student record
                student_record = df[df['student_name'] == selected_student].iloc[0]
                
                # Reconstruct data for PDF
                pdf_data = {
                    'quiz_name': quiz_selector.replace("Quiz", "Quiz "),
                    'student_name': student_record['student_name'],
                    'register_number': student_record['register_number'],
                    'timestamp': student_record['timestamp'],
                    'score': student_record['score'],
                    'total_questions': student_record['total_questions'],
                    'questions': json.loads(student_record['questions_json']),
                    'answers': json.loads(student_record['answers_json'])
                }
                
                pdf_bytes = create_results_pdf(pdf_data)
                st.download_button(
                    label=f"📥 Download {selected_student}'s Report",
                    data=pdf_bytes,
                    file_name=f"{student_record['register_number']}_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("No submissions found for this quiz.")
    
    with tab2:
        st.subheader("Malpractice Incidents")
        
        with st.spinner("Loading malpractice logs..."):
            log_df = get_sheet_data("MalpracticeLogs")
        
        if log_df is not None and not log_df.empty:
            st.error(f"⚠️ {len(log_df)} malpractice incidents detected", icon="🚨")
            st.dataframe(log_df, use_container_width=True)
            
            # Download logs
            csv_bytes = log_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Malpractice Logs (CSV)",
                data=csv_bytes,
                file_name="malpractice_logs.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ No malpractice incidents recorded", icon="✅")
    
    with tab3:
        st.subheader("Question Banks")
        
        quiz_bank_selector = st.selectbox("Select Quiz Bank:", list(QUIZ_BANKS.keys()))
        
        if quiz_bank_selector:
            selected_bank = QUIZ_BANKS[quiz_bank_selector]
            st.info(f"Total Questions: {len(selected_bank)}")
            
            # Display questions
            with st.expander("View Questions"):
                for idx, q in enumerate(selected_bank, 1):
                    st.markdown(f"**Q{idx}. {q['question']}**")
                    for opt_idx, option in enumerate(q['options']):
                        marker = "✅" if opt_idx == q['correct'] else ""
                        st.markdown(f"   {chr(97 + opt_idx)}) {option} {marker}")
                    st.markdown("---")
            
            # Download question bank as PDF
            if st.button("📥 Download Question Bank (PDF)"):
                pdf_bytes = create_question_bank_pdf(quiz_bank_selector, selected_bank)
                st.download_button(
                    label=f"Download {quiz_bank_selector} Questions",
                    data=pdf_bytes,
                    file_name=f"{quiz_bank_selector.replace(':', '').replace(' ', '_')}_QuestionBank.pdf",
                    mime="application/pdf"
                )

# =====================================================================================
# --- 🚀 MAIN APPLICATION ROUTER ---
# =====================================================================================

def main():
    """Main function to control the app's page flow."""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "quiz_selection"
    
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    # Route to appropriate page
    if st.session_state.admin_authenticated and st.session_state.page == "admin_dashboard":
        render_admin_dashboard()
    elif st.session_state.get('malpractice_detected', False):
        render_malpractice_page()
    elif st.session_state.page == "quiz_selection":
        render_quiz_selection_page()
        if not st.session_state.admin_authenticated:
            render_admin_panel()
    elif st.session_state.page == "student_info":
        render_student_info_page()
    elif st.session_state.page == "quiz":
        render_quiz_page()
    elif st.session_state.page == "results":
        render_results_page()
    else:
        st.session_state.page = "quiz_selection"
        st.rerun()

if __name__ == "__main__":
    main()