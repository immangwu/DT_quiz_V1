#!/usr/bin/env python3
"""
Unconventional Machining Process Quiz Server
Serves quiz on local network and generates PDF results
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import socket
import os
import datetime
import json

app = Flask(__name__)

# Quiz questions from the PDF
QUIZ_DATA = {
    "title": "UNCONVENTIONAL MACHINING PROCESS - QUIZ 1",
    "course": "20MEP11 - UNCONVENTIONAL MACHINING PROCESS",
    "unit": "UNIT I: INTRODUCTION",
    "duration": "45 Minutes",
    "max_marks": 20,
    "instructions": [
        "Answer ALL questions",
        "Each question carries 1 mark", 
        "Select the most appropriate answer",
        "No negative marking"
    ],
    "questions": [
        {
            "id": 1,
            "question": "Non-traditional machining is recommended when we need which of the following features?",
            "options": ["Complex shapes", "High surface quality", "Low-rigidity structures", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 2,
            "question": "Non-traditional machining can also be called as:",
            "options": ["Contact machining", "Non-contact machining", "Partial contact machining", "Half contact machining"],
            "correct": 1
        },
        {
            "id": 3,
            "question": "In which industries do Non-traditional machining methods play an important role?",
            "options": ["Automobile", "Aerospace", "Medical", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 4,
            "question": "Different classifications of Non-traditional machining based on source of energy are:",
            "options": ["Mechanical", "Thermal", "Chemical and electro-chemical", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 5,
            "question": "In mechanical machining, material is removed by:",
            "options": ["Erosion", "Corrosion", "Abrasion", "Vaporization"],
            "correct": 2
        },
        {
            "id": 6,
            "question": "Material in thermal machining is removed by which means?",
            "options": ["Vaporization", "Melting", "Electro-plating", "All of the mentioned"],
            "correct": 0
        },
        {
            "id": 7,
            "question": "Which process comes under mechanical machining?",
            "options": ["USM", "EDM", "LBM", "PAM"],
            "correct": 0
        },
        {
            "id": 8,
            "question": "Surface defects that may occur during thermal machining are:",
            "options": ["Micro cracking", "Heat affected zones", "Striations", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 9,
            "question": "Sources used in thermal machining are:",
            "options": ["Ions", "Plasma", "Electrons", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 10,
            "question": "Vacuum is the machining medium for:",
            "options": ["LBM", "WJM", "EBM", "None of the mentioned"],
            "correct": 2
        },
        {
            "id": 11,
            "question": "In chemical machining, material removal takes place by:",
            "options": ["Chemical reaction", "Erosion", "Electron removal", "None of the mentioned"],
            "correct": 0
        },
        {
            "id": 12,
            "question": "Which is an example of hybrid machining?",
            "options": ["Ultrasonic Machining", "Electron Beam Machining", "Ultrasonic assisted ECM", "Laser Beam Machining"],
            "correct": 2
        },
        {
            "id": 13,
            "question": "The main advantage of non-traditional machining over conventional machining is:",
            "options": ["Higher material removal rate", "Lower cost", "Ability to machine hard materials", "Simpler equipment"],
            "correct": 2
        },
        {
            "id": 14,
            "question": "Which energy source is NOT used in non-traditional machining?",
            "options": ["Electrical energy", "Chemical energy", "Gravitational energy", "Thermal energy"],
            "correct": 2
        },
        {
            "id": 15,
            "question": "The selection of non-traditional machining process depends on:",
            "options": ["Material properties", "Required accuracy", "Production rate", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 16,
            "question": "Non-traditional machining processes are particularly suitable for:",
            "options": ["Mass production", "Hard and brittle materials", "Large components", "Simple geometries"],
            "correct": 1
        },
        {
            "id": 17,
            "question": "The main limitation of non-traditional machining is:",
            "options": ["Poor surface finish", "High tooling cost", "Low material removal rate", "Limited material range"],
            "correct": 2
        },
        {
            "id": 18,
            "question": "Which factor is most important in process selection?",
            "options": ["Initial cost", "Material hardness", "Operator skill", "Factory location"],
            "correct": 1
        },
        {
            "id": 19,
            "question": "Environmental considerations in non-traditional machining include:",
            "options": ["Waste disposal", "Energy consumption", "Emissions control", "All of the mentioned"],
            "correct": 3
        },
        {
            "id": 20,
            "question": "The future trend in non-traditional machining is towards:",
            "options": ["Hybrid processes", "Automation", "Miniaturization", "All of the mentioned"],
            "correct": 3
        }
    ]
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ quiz.title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 1.8em;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header .course-info {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .header .quiz-details {
            font-size: 0.9em;
            opacity: 0.8;
        }

        .network-info {
            background: #e8f4fd;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
            border-left: 4px solid #2196F3;
        }

        .network-info h3 {
            color: #1976D2;
            margin-bottom: 10px;
        }

        .content {
            padding: 30px;
        }

        .student-form {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            border-left: 4px solid #28a745;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }

        .instructions {
            background: #fff3cd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #ffc107;
        }

        .instructions h3 {
            color: #856404;
            margin-bottom: 15px;
        }

        .instructions ul {
            color: #856404;
            padding-left: 20px;
        }

        .instructions li {
            margin-bottom: 5px;
        }

        .question-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .question-number {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px 15px;
            border-radius: 50px;
            font-weight: bold;
        }

        .question-text {
            font-size: 1.1em;
            color: #333;
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .options {
            display: grid;
            gap: 12px;
        }

        .option {
            background: white;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
        }

        .option:hover {
            border-color: #667eea;
            background: #f0f4ff;
        }

        .option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .option input[type="radio"] {
            margin-right: 12px;
            transform: scale(1.2);
        }

        .progress-bar {
            background: #e1e5e9;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }

        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .btn-success {
            background: linear-gradient(135deg, #28a745, #20c997);
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        }

        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
        }

        .navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }

        .results-screen {
            text-align: center;
            padding: 40px;
        }

        .score {
            font-size: 4em;
            color: #667eea;
            font-weight: bold;
            margin: 30px 0;
        }

        .score-message {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 30px;
        }

        .hidden {
            display: none;
        }

        .quiz-completed {
            background: #d4edda;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
            text-align: center;
        }

        .quiz-completed h3 {
            color: #155724;
            margin-bottom: 10px;
        }

        .timer {
            background: #f8d7da;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #dc3545;
            text-align: center;
        }

        .timer-text {
            color: #721c24;
            font-weight: bold;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DEPARTMENT OF MECHANICAL ENGINEERING</h1>
            <div class="course-info">{{ quiz.course }}</div>
            <div class="course-info">{{ quiz.unit }}</div>
            <div class="quiz-details">Duration: {{ quiz.duration }} | Maximum Marks: {{ quiz.max_marks }}</div>
        </div>

        <div class="network-info">
            <h3>🌐 Quiz Server Information</h3>
            <p><strong>Server URL:</strong> <span id="serverUrl">Loading...</span></p>
            <p><strong>Status:</strong> <span style="color: #4CAF50;">● Online</span></p>
            <p>Share this URL with students on your network!</p>
        </div>

        <div class="content">
            <!-- Student Information Form -->
            <div id="studentForm" class="student-form">
                <h3>Student Information</h3>
                <div class="form-group">
                    <label for="studentName">Student Name *</label>
                    <input type="text" id="studentName" placeholder="Enter your full name" required>
                </div>
                <div class="form-group">
                    <label for="registerNumber">Register Number *</label>
                    <input type="text" id="registerNumber" placeholder="Enter your register number" required>
                </div>
                <button class="btn btn-success" onclick="startQuiz()">Start Quiz</button>
            </div>

            <!-- Instructions -->
            <div id="instructions" class="instructions hidden">
                <h3>📋 Instructions</h3>
                <ul>
                    {% for instruction in quiz.instructions %}
                    <li>{{ instruction }}</li>
                    {% endfor %}
                </ul>
                <div style="margin-top: 20px;">
                    <button class="btn" onclick="beginQuiz()">Begin Quiz</button>
                </div>
            </div>

            <!-- Timer -->
            <div id="timer" class="timer hidden">
                <div class="timer-text">Time Remaining: <span id="timeDisplay">10:00</span></div>
            </div>

            <!-- Progress Bar -->
            <div id="progressContainer" class="hidden">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div style="text-align: center; margin-bottom: 20px;">
                    Question <span id="currentQuestionNum">1</span> of {{ quiz.questions|length }}
                </div>
            </div>

            <!-- Quiz Questions -->
            <div id="quizContainer" class="hidden">
                {% for question in quiz.questions %}
                <div class="question-container question" id="question{{ question.id }}" style="display: none;">
                    <div class="question-header">
                        <div class="question-number">Q{{ question.id }}</div>
                    </div>
                    <div class="question-text">{{ question.question }}</div>
                    <div class="options">
                        {% for option in question.options %}
                        <div class="option" onclick="selectOption({{ question.id }}, {{ loop.index0 }})">
                            <input type="radio" name="q{{ question.id }}" value="{{ loop.index0 }}" id="q{{ question.id }}_{{ loop.index0 }}">
                            <label for="q{{ question.id }}_{{ loop.index0 }}">{{ option }}</label>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}

                <div class="navigation">
                    <button class="btn" onclick="previousQuestion()" id="prevBtn" disabled>Previous</button>
                    <button class="btn" onclick="nextQuestion()" id="nextBtn">Next</button>
                    <button class="btn btn-success hidden" onclick="submitQuiz()" id="submitBtn">Submit Quiz</button>
                </div>
            </div>

            <!-- Results -->
            <div id="resultsContainer" class="results-screen hidden">
                <div class="quiz-completed">
                    <h3>🎉 Quiz Completed Successfully!</h3>
                    <p>Your answers have been recorded and your result PDF has been generated.</p>
                </div>
                <div class="score" id="finalScore">0/{{ quiz.questions|length }}</div>
                <div class="score-message" id="scoreMessage">Great job!</div>
                <button class="btn btn-success" onclick="downloadPDF()" id="downloadBtn">Download Result PDF</button>
            </div>
        </div>
    </div>

    <script>
        let currentQuestion = 0;
        let answers = {};
        let studentName = '';
        let registerNumber = '';
        let timeRemaining = 10 * 60; // 10 minutes in seconds
        let timerInterval;

        // Initialize
        window.onload = function() {
            document.getElementById('serverUrl').textContent = window.location.href;
        };

        function startQuiz() {
            const name = document.getElementById('studentName').value.trim();
            const regNum = document.getElementById('registerNumber').value.trim();
            
            if (!name || !regNum) {
                alert('Please enter both name and register number!');
                return;
            }
            
            studentName = name;
            registerNumber = regNum;
            
            document.getElementById('studentForm').classList.add('hidden');
            document.getElementById('instructions').classList.remove('hidden');
        }

        function beginQuiz() {
            document.getElementById('instructions').classList.add('hidden');
            document.getElementById('timer').classList.remove('hidden');
            document.getElementById('progressContainer').classList.remove('hidden');
            document.getElementById('quizContainer').classList.remove('hidden');
            
            showQuestion(0);
            startTimer();
        }

        function startTimer() {
            timerInterval = setInterval(function() {
                timeRemaining--;
                updateTimeDisplay();
                
                if (timeRemaining <= 0) {
                    clearInterval(timerInterval);
                    alert('Time is up! Submitting quiz automatically.');
                    submitQuiz();
                }
            }, 1000);
        }

        function updateTimeDisplay() {
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            document.getElementById('timeDisplay').textContent = 
                minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
        }

        function showQuestion(index) {
            // Hide all questions
            document.querySelectorAll('.question').forEach(q => q.style.display = 'none');
            
            // Show current question
            document.getElementById('question' + (index + 1)).style.display = 'block';
            
            // Update progress
            const progress = ((index + 1) / {{ quiz.questions|length }}) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('currentQuestionNum').textContent = index + 1;
            
            // Update navigation buttons
            document.getElementById('prevBtn').disabled = index === 0;
            
            if (index === {{ quiz.questions|length }} - 1) {
                document.getElementById('nextBtn').classList.add('hidden');
                document.getElementById('submitBtn').classList.remove('hidden');
            } else {
                document.getElementById('nextBtn').classList.remove('hidden');
                document.getElementById('submitBtn').classList.add('hidden');
            }
        }

        function selectOption(questionId, optionIndex) {
            answers[questionId] = optionIndex;
            
            // Update UI
            const questionElement = document.getElementById('question' + questionId);
            questionElement.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
            questionElement.querySelectorAll('.option')[optionIndex].classList.add('selected');
            questionElement.querySelector(`input[value="${optionIndex}"]`).checked = true;
        }

        function nextQuestion() {
            if (currentQuestion < {{ quiz.questions|length }} - 1) {
                currentQuestion++;
                showQuestion(currentQuestion);
            }
        }

        function previousQuestion() {
            if (currentQuestion > 0) {
                currentQuestion--;
                showQuestion(currentQuestion);
            }
        }

        function submitQuiz() {
            if (Object.keys(answers).length < {{ quiz.questions|length }}) {
                if (!confirm('You have not answered all questions. Are you sure you want to submit?')) {
                    return;
                }
            }
            
            clearInterval(timerInterval);
            
            // Calculate score
            let score = 0;
            const correctAnswers = {{ quiz.questions|map(attribute='correct')|list }};
            
            for (let i = 1; i <= {{ quiz.questions|length }}; i++) {
                if (answers[i] === correctAnswers[i-1]) {
                    score++;
                }
            }
            
            // Show results
            document.getElementById('timer').classList.add('hidden');
            document.getElementById('progressContainer').classList.add('hidden');
            document.getElementById('quizContainer').classList.add('hidden');
            document.getElementById('resultsContainer').classList.remove('hidden');
            
            document.getElementById('finalScore').textContent = score + '/{{ quiz.questions|length }}';
            
            const percentage = (score / {{ quiz.questions|length }}) * 100;
            let message = '';
            if (percentage >= 90) message = 'Excellent! Outstanding performance! 🌟';
            else if (percentage >= 80) message = 'Very Good! Well done! 👏';
            else if (percentage >= 70) message = 'Good! Keep it up! 👍';
            else if (percentage >= 60) message = 'Satisfactory! You can do better! 💪';
            else message = 'Needs improvement! Keep studying! 📚';
            
            document.getElementById('scoreMessage').textContent = message;
            
            // Send results to server
            fetch('/submit_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    studentName: studentName,
                    registerNumber: registerNumber,
                    answers: answers,
                    score: score,
                    totalQuestions: {{ quiz.questions|length }},
                    timeTaken: (10 * 60) - timeRemaining
                })
            });
        }

        function downloadPDF() {
            window.open('/download_pdf/' + encodeURIComponent(studentName) + '/' + encodeURIComponent(registerNumber), '_blank');
        }
    </script>
</body>
</html>
"""

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def create_results_pdf(student_data):
    """Generate PDF with quiz results"""
    filename = f"{student_data['studentName']}_{student_data['registerNumber']}.pdf"
    filepath = os.path.join("quiz_results", filename)
    
    # Create directory if it doesn't exist
    os.makedirs("quiz_results", exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    story.append(Paragraph("DEPARTMENT OF MECHANICAL ENGINEERING", title_style))
    story.append(Paragraph("20MEP11 - UNCONVENTIONAL MACHINING PROCESS", styles['Heading2']))
    story.append(Paragraph("QUIZ 1 - UNIT I: INTRODUCTION", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Student Information
    student_info = [
        ['Student Name:', student_data['studentName']],
        ['Register Number:', student_data['registerNumber']],
        ['Date:', datetime.datetime.now().strftime("%Y-%m-%d")],
        ['Time:', datetime.datetime.now().strftime("%H:%M:%S")],
        ['Duration:', f"{student_data['timeTaken']//60}:{student_data['timeTaken']%60:02d} minutes"],
    ]
    
    student_table = Table(student_info, colWidths=[2*inch, 3*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 20))
    
    # Score Summary
    score_style = ParagraphStyle(
        'ScoreStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        spaceAfter=20
    )
    
    percentage = (student_data['score'] / student_data['totalQuestions']) * 100
    story.append(Paragraph(f"<b>SCORE: {student_data['score']}/{student_data['totalQuestions']} ({percentage:.1f}%)</b>", score_style))
    
    # Grade calculation
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    else:
        grade = "F"
    
    story.append(Paragraph(f"<b>GRADE: {grade}</b>", score_style))
    story.append(Spacer(1, 20))
    
    # Detailed Results
    story.append(Paragraph("DETAILED RESULTS", styles['Heading3']))
    story.append(Spacer(1, 10))
    
    # Answer details
    results_data = [['Q.No', 'Your Answer', 'Correct Answer', 'Status']]
    
    for i, question in enumerate(QUIZ_DATA['questions'], 1):
        user_answer_idx = student_data['answers'].get(str(i), -1)
        correct_answer_idx = question['correct']
        
        user_answer = question['options'][user_answer_idx] if user_answer_idx >= 0 else "Not Answered"
        correct_answer = question['options'][correct_answer_idx]
        status = "✓ Correct" if user_answer_idx == correct_answer_idx else "✗ Wrong"
        
        results_data.append([str(i), user_answer, correct_answer, status])
    
    results_table = Table(results_data, colWidths=[0.7*inch, 2.2*inch, 2.2*inch, 1*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Color code the status column
    for i in range(1, len(results_data)):
        if "✓ Correct" in results_data[i][3]:
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (3, i), (3, i), colors.lightgreen),
            ]))
        else:
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (3, i), (3, i), colors.lightpink),
            ]))
    
    story.append(results_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )
    
    story.append(Paragraph("This is an auto-generated report.", footer_style))
    story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    
    # Build PDF
    doc.build(story)
    return filepath

@app.route('/')
def index():
    """Serve the quiz homepage"""
    return render_template_string(HTML_TEMPLATE, quiz=QUIZ_DATA)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Handle quiz submission and generate PDF"""
    try:
        data = request.json
        
        # Store submission data
        submission_data = {
            'studentName': data['studentName'],
            'registerNumber': data['registerNumber'],
            'answers': data['answers'],
            'score': data['score'],
            'totalQuestions': data['totalQuestions'],
            'timeTaken': data['timeTaken'],
            'submissionTime': datetime.datetime.now().isoformat()
        }
        
        # Generate PDF
        pdf_path = create_results_pdf(submission_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Quiz submitted successfully',
            'pdf_generated': True,
            'filename': os.path.basename(pdf_path)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing submission: {str(e)}'
        }), 500

@app.route('/download_pdf/<student_name>/<register_number>')
def download_pdf(student_name, register_number):
    """Download the generated PDF"""
    try:
        filename = f"{student_name}_{register_number}.pdf"
        filepath = os.path.join("quiz_results", filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return "PDF not found", 404
            
    except Exception as e:
        return f"Error downloading PDF: {str(e)}", 500

@app.route('/admin')
def admin_panel():
    """Simple admin panel to view submissions"""
    try:
        results_dir = "quiz_results"
        if not os.path.exists(results_dir):
            return "No submissions yet."
        
        files = os.listdir(results_dir)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        
        html = f"""
        <html>
        <head>
            <title>Quiz Admin Panel</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #343a40; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .file-list {{ list-style: none; padding: 0; }}
                .file-item {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
                .download-link {{ color: #007bff; text-decoration: none; font-weight: bold; }}
                .download-link:hover {{ text-decoration: underline; }}
                .stats {{ background: #e9ecef; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Quiz Administration Panel</h1>
                <p>Unconventional Machining Process - Quiz Results</p>
            </div>
            
            <div class="stats">
                <h3>Statistics</h3>
                <p><strong>Total Submissions:</strong> {len(pdf_files)}</p>
                <p><strong>Server IP:</strong> {get_local_ip()}</p>
                <p><strong>Results Directory:</strong> {os.path.abspath(results_dir)}</p>
            </div>
            
            <h3>Submitted Results:</h3>
        """
        
        if pdf_files:
            html += '<ul class="file-list">'
            for pdf_file in sorted(pdf_files):
                file_path = os.path.join(results_dir, pdf_file)
                file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                html += f'''
                <li class="file-item">
                    <strong>{pdf_file.replace('_', ' - ').replace('.pdf', '')}</strong><br>
                    <small>Submitted: {file_time.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                    <a href="/quiz_results/{pdf_file}" class="download-link" target="_blank">Download PDF</a>
                </li>
                '''
            html += '</ul>'
        else:
            html += '<p>No submissions yet.</p>'
        
        html += '''
            <br>
            <p><a href="/">&larr; Back to Quiz</a></p>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f"Error loading admin panel: {str(e)}"

@app.route('/quiz_results/<filename>')
def serve_pdf(filename):
    """Serve PDF files from results directory"""
    try:
        return send_file(os.path.join("quiz_results", filename))
    except Exception as e:
        return f"Error serving file: {str(e)}", 404

def print_server_info():
    """Print server startup information"""
    ip = get_local_ip()
    print("\n" + "="*60)
    print("🎓 UNCONVENTIONAL MACHINING PROCESS QUIZ SERVER")
    print("="*60)
    print(f"📡 Server IP Address: {ip}")
    print(f"🌐 Quiz URL: http://{ip}:5000")
    print(f"⚙️  Admin Panel: http://{ip}:5000/admin")
    print(f"📁 Results Directory: {os.path.abspath('quiz_results')}")
    print("="*60)
    print("📋 Quiz Details:")
    print(f"   • Course: {QUIZ_DATA['course']}")
    print(f"   • Unit: {QUIZ_DATA['unit']}")
    print(f"   • Duration: {QUIZ_DATA['duration']}")
    print(f"   • Questions: {len(QUIZ_DATA['questions'])}")
    print(f"   • Max Marks: {QUIZ_DATA['max_marks']}")
    print("="*60)
    print("🚀 Instructions:")
    print("   1. Share the Quiz URL with students on your WiFi network")
    print("   2. Students enter their name and register number")
    print("   3. Quiz results are automatically saved as PDFs")
    print("   4. Use Admin Panel to view all submissions")
    print("   5. Press Ctrl+C to stop the server")
    print("="*60)
    print("✅ Server is running... Waiting for students!")
    print()

if __name__ == '__main__':
    # Create results directory
    os.makedirs("quiz_results", exist_ok=True)
    
    # Print server information
    print_server_info()
    
    try:
        # Run the Flask server
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        print("👋 Goodbye!")