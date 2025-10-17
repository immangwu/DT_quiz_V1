#!/usr/bin/env python3
"""
Manufacturing Processes II Quiz Server
Serves random quiz questions and monitors screen focus
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
import random

app = Flask(__name__)

# Complete question bank from Theory of Metal Cutting
QUESTION_BANK = [
    {
        "id": 1,
        "question": "The primary deformation zone in metal cutting is located:",
        "options": ["At the tool tip", "Ahead of the cutting edge", "Behind the cutting edge", "In the workpiece material"],
        "correct": 1
    },
    {
        "id": 2,
        "question": "The secondary deformation zone occurs:",
        "options": ["In the workpiece", "Between chip and tool face", "In the tool material", "At the cutting edge"],
        "correct": 1
    },
    {
        "id": 3,
        "question": "The shear angle in metal cutting is defined as:",
        "options": ["Angle between shear plane and cutting direction", "Angle between tool face and horizontal", "Angle between shear plane and tool face", "Angle between cutting edge and workpiece"],
        "correct": 0
    },
    {
        "id": 4,
        "question": "According to Merchant's theory, the shear angle is related to:",
        "options": ["Rake angle only", "Friction angle only", "Both rake angle and friction angle", "Cutting speed only"],
        "correct": 2
    },
    {
        "id": 5,
        "question": "The built-up edge (BUE) formation is favored by:",
        "options": ["High cutting speeds", "Low cutting speeds", "High rake angles", "Brittle workpiece materials"],
        "correct": 1
    },
    {
        "id": 6,
        "question": "The velocity of chip flow is:",
        "options": ["Always equal to cutting speed", "Always less than cutting speed", "Always greater than cutting speed", "Independent of cutting speed"],
        "correct": 1
    },
    {
        "id": 7,
        "question": "The chip thickness ratio is defined as:",
        "options": ["Cut chip thickness / Uncut chip thickness", "Uncut chip thickness / Cut chip thickness", "Chip width / Cut width", "Chip length / Cut length"],
        "correct": 0
    },
    {
        "id": 8,
        "question": "Ernst and Merchant's equation relates shear angle to:",
        "options": ["Tool geometry only", "Friction coefficient only", "Tool geometry and friction", "Cutting conditions only"],
        "correct": 2
    },
    {
        "id": 9,
        "question": "The strain in the primary deformation zone is:",
        "options": ["Uniform throughout", "Maximum at the tool tip", "Maximum at the shear plane", "Zero everywhere"],
        "correct": 2
    },
    {
        "id": 10,
        "question": "Plastic deformation in metal cutting occurs primarily due to:",
        "options": ["Thermal effects", "Shear stress exceeding yield strength", "Tool vibration", "Chemical reactions"],
        "correct": 1
    },
    {
        "id": 11,
        "question": "The chip compression ratio is the reciprocal of:",
        "options": ["Cutting ratio", "Shear strain", "Friction coefficient", "Shear angle"],
        "correct": 0
    },
    {
        "id": 12,
        "question": "In ideal orthogonal cutting, the cutting edge is:",
        "options": ["Parallel to the direction of cutting", "Perpendicular to the direction of cutting", "At 45° to the direction of cutting", "Inclined at rake angle to cutting direction"],
        "correct": 1
    },
    {
        "id": 13,
        "question": "The material ahead of the tool experiences:",
        "options": ["Tensile stress only", "Compressive stress only", "Both tensile and compressive stress", "No stress"],
        "correct": 2
    },
    {
        "id": 14,
        "question": "Stabler's rule states that in oblique cutting:",
        "options": ["Chip flow angle equals inclination angle", "Shear angle remains constant", "Cutting forces are minimized", "Tool life is maximized"],
        "correct": 0
    },
    {
        "id": 15,
        "question": "The effective rake angle in oblique cutting is:",
        "options": ["Greater than normal rake angle", "Less than normal rake angle", "Equal to normal rake angle", "Independent of inclination angle"],
        "correct": 1
    },
    {
        "id": 16,
        "question": "The rake angle of a cutting tool is measured between:",
        "options": ["Tool face and cutting edge", "Tool face and reference plane", "Flank face and cutting edge", "Flank face and reference plane"],
        "correct": 1
    },
    {
        "id": 17,
        "question": "A positive rake angle:",
        "options": ["Increases cutting forces", "Decreases cutting forces", "Has no effect on cutting forces", "Doubles cutting forces"],
        "correct": 1
    },
    {
        "id": 18,
        "question": "The clearance angle is provided to:",
        "options": ["Improve surface finish", "Reduce tool wear", "Prevent rubbing of flank face", "Increase tool strength"],
        "correct": 2
    },
    {
        "id": 19,
        "question": "The nose radius of a cutting tool affects:",
        "options": ["Surface finish only", "Tool strength only", "Both surface finish and tool strength", "Cutting speed only"],
        "correct": 2
    },
    {
        "id": 20,
        "question": "The cutting edge angle (lead angle) affects:",
        "options": ["Chip thickness", "Tool life", "Heat generation", "All of the above"],
        "correct": 3
    },
    {
        "id": 21,
        "question": "Back rake angle is measured in:",
        "options": ["Longitudinal plane", "Transverse plane", "Axial plane", "Reference plane"],
        "correct": 0
    },
    {
        "id": 22,
        "question": "Side rake angle is measured in:",
        "options": ["Longitudinal plane", "Transverse plane", "Axial plane", "Reference plane"],
        "correct": 1
    },
    {
        "id": 23,
        "question": "The included angle of a cutting tool is:",
        "options": ["Sum of rake and clearance angles", "Difference between rake and clearance angles", "Complement of rake angle", "Supplement of clearance angle"],
        "correct": 0
    },
    {
        "id": 24,
        "question": "A sharp cutting edge has:",
        "options": ["Large nose radius", "Small nose radius", "Zero nose radius", "Variable nose radius"],
        "correct": 2
    },
    {
        "id": 25,
        "question": "The side cutting edge angle determines:",
        "options": ["Chip flow direction", "Surface finish", "Tool entry angle", "All of the above"],
        "correct": 3
    },
    {
        "id": 26,
        "question": "Chip breakers are used to:",
        "options": ["Increase cutting speed", "Control chip formation", "Reduce cutting forces", "Improve tool life"],
        "correct": 1
    },
    {
        "id": 27,
        "question": "The wedge angle of a cutting tool is:",
        "options": ["Always 90°", "Sum of rake and clearance angles", "Difference between 90° and sum of rake and clearance angles", "Independent of rake and clearance angles"],
        "correct": 2
    },
    {
        "id": 28,
        "question": "In ASA (American Standards Association) system, angles are measured from:",
        "options": ["Tool shank", "Base of tool", "Cutting edge", "Tool face"],
        "correct": 1
    },
    {
        "id": 29,
        "question": "The approach angle affects:",
        "options": ["Heat dissipation", "Tool life", "Surface finish", "All of the above"],
        "correct": 3
    },
    {
        "id": 30,
        "question": "A negative rake angle is used for:",
        "options": ["Soft materials", "Brittle materials", "High-speed cutting", "Finishing operations"],
        "correct": 1
    },
    {
        "id": 31,
        "question": "The three components of cutting force are:",
        "options": ["Tangential, radial, and axial", "Primary, secondary, and tertiary", "Cutting, thrust, and feed", "Horizontal, vertical, and lateral"],
        "correct": 0
    },
    {
        "id": 32,
        "question": "The main cutting force acts:",
        "options": ["Parallel to cutting velocity", "Perpendicular to cutting velocity", "At 45° to cutting velocity", "Opposite to cutting velocity"],
        "correct": 0
    },
    {
        "id": 33,
        "question": "The thrust force in turning acts:",
        "options": ["Along the feed direction", "Radially inward", "Tangentially", "Axially"],
        "correct": 1
    },
    {
        "id": 34,
        "question": "Continuous chips are formed when:",
        "options": ["Material is brittle", "Material is ductile with high cutting speed", "Material is hard", "Cutting speed is very low"],
        "correct": 1
    },
    {
        "id": 35,
        "question": "Discontinuous chips are characterized by:",
        "options": ["Smooth surface", "Segmented appearance", "Continuous flow", "Uniform thickness"],
        "correct": 1
    },
    {
        "id": 36,
        "question": "Built-up edge chips occur due to:",
        "options": ["High temperature", "High pressure and low speed", "Material brittleness", "Tool sharpness"],
        "correct": 1
    },
    {
        "id": 37,
        "question": "The power required for machining is given by:",
        "options": ["Force × velocity", "Force × displacement", "Force × time", "Force / velocity"],
        "correct": 0
    },
    {
        "id": 38,
        "question": "Merchant's circle diagram is used to determine:",
        "options": ["Tool geometry", "Cutting forces", "Relationship between forces and angles", "Material properties"],
        "correct": 2
    },
    {
        "id": 39,
        "question": "The coefficient of friction on rake face is:",
        "options": ["Always less than 1", "Always greater than 1", "Can be greater than 1", "Always equal to 1"],
        "correct": 2
    },
    {
        "id": 40,
        "question": "Serrated chips are formed in:",
        "options": ["Ductile materials at low speeds", "Brittle materials", "Hard materials at high speeds", "Soft materials"],
        "correct": 2
    },
    {
        "id": 41,
        "question": "The specific cutting energy is:",
        "options": ["Power per unit volume removal rate", "Force per unit area", "Energy per unit volume of material removed", "Energy per unit time"],
        "correct": 2
    },
    {
        "id": 42,
        "question": "Cutting force increases with:",
        "options": ["Increased feed rate", "Increased depth of cut", "Decreased rake angle", "All of the above"],
        "correct": 3
    },
    {
        "id": 43,
        "question": "The feed force component is:",
        "options": ["Largest among all forces", "Smallest among all forces", "Equal to cutting force", "Independent of feed rate"],
        "correct": 1
    },
    {
        "id": 44,
        "question": "Dynamometer is used to measure:",
        "options": ["Cutting temperature", "Cutting forces", "Tool wear", "Surface roughness"],
        "correct": 1
    },
    {
        "id": 45,
        "question": "The ideal chip type for good surface finish is:",
        "options": ["Continuous chip", "Discontinuous chip", "Built-up edge chip", "Serrated chip"],
        "correct": 0
    },
    {
        "id": 46,
        "question": "The maximum temperature in metal cutting occurs:",
        "options": ["At the tool tip", "On the rake face near cutting edge", "In the chip", "In the workpiece"],
        "correct": 1
    },
    {
        "id": 47,
        "question": "Heat generation in metal cutting is primarily due to:",
        "options": ["Plastic deformation", "Friction", "Both plastic deformation and friction", "Tool vibration"],
        "correct": 2
    },
    {
        "id": 48,
        "question": "The percentage of heat conducted into the tool is approximately:",
        "options": ["5-10%", "10-20%", "20-40%", "40-60%"],
        "correct": 0
    },
    {
        "id": 49,
        "question": "High Speed Steel (HSS) can withstand temperatures up to:",
        "options": ["200°C", "400°C", "600°C", "800°C"],
        "correct": 2
    },
    {
        "id": 50,
        "question": "Carbide tools can operate at temperatures up to:",
        "options": ["600°C", "800°C", "1000°C", "1200°C"],
        "correct": 2
    },
    {
        "id": 51,
        "question": "Ceramic tools are suitable for:",
        "options": ["Low-speed operations", "High-speed operations", "Interrupted cuts", "Soft materials"],
        "correct": 1
    },
    {
        "id": 52,
        "question": "Diamond tools are used for machining:",
        "options": ["Ferrous materials", "Non-ferrous materials", "All materials", "Only ceramics"],
        "correct": 1
    },
    {
        "id": 53,
        "question": "Cubic Boron Nitride (CBN) is used for:",
        "options": ["Soft materials", "Hardened steels", "Aluminum alloys", "Plastics"],
        "correct": 1
    },
    {
        "id": 54,
        "question": "The hardness of cutting tool material should be:",
        "options": ["Equal to workpiece hardness", "Less than workpiece hardness", "Greater than workpiece hardness", "Independent of workpiece hardness"],
        "correct": 2
    },
    {
        "id": 55,
        "question": "Coated carbide tools have:",
        "options": ["Better wear resistance", "Higher cutting speeds", "Improved tool life", "All of the above"],
        "correct": 3
    },
    {
        "id": 56,
        "question": "TiN coating provides:",
        "options": ["Increased hardness", "Reduced friction", "Chemical stability", "All of the above"],
        "correct": 3
    },
    {
        "id": 57,
        "question": "The thermal conductivity of cutting tool should be:",
        "options": ["High", "Low", "Medium", "Variable"],
        "correct": 0
    },
    {
        "id": 58,
        "question": "Cermets are:",
        "options": ["Pure ceramics", "Pure metals", "Ceramic-metal composites", "Carbon-based materials"],
        "correct": 2
    },
    {
        "id": 59,
        "question": "The cutting speed for HSS tools is typically:",
        "options": ["10-50 m/min", "50-150 m/min", "150-300 m/min", "300-500 m/min"],
        "correct": 1
    },
    {
        "id": 60,
        "question": "Stellite is a:",
        "options": ["Carbide material", "Ceramic material", "Cobalt-based alloy", "Diamond material"],
        "correct": 2
    },
    {
        "id": 61,
        "question": "The most common type of tool wear is:",
        "options": ["Crater wear", "Flank wear", "Nose wear", "Edge chipping"],
        "correct": 1
    },
    {
        "id": 62,
        "question": "Taylor's tool life equation is:",
        "options": ["VT = C", "VT^n = C", "V^n T = C", "VT^n + C = 0"],
        "correct": 1
    },
    {
        "id": 63,
        "question": "The value of 'n' in Taylor's equation is typically:",
        "options": ["0.1-0.2", "0.2-0.5", "0.5-0.8", "0.8-1.0"],
        "correct": 0
    },
    {
        "id": 64,
        "question": "Crater wear occurs on:",
        "options": ["Flank face", "Rake face", "Cutting edge", "Tool shank"],
        "correct": 1
    },
    {
        "id": 65,
        "question": "Built-up edge causes:",
        "options": ["Better surface finish", "Poor surface finish", "No change in surface finish", "Variable surface finish"],
        "correct": 1
    },
    {
        "id": 66,
        "question": "Surface roughness is primarily affected by:",
        "options": ["Feed rate", "Cutting speed", "Depth of cut", "Tool material"],
        "correct": 0
    },
    {
        "id": 67,
        "question": "The theoretical surface roughness in turning is proportional to:",
        "options": ["Feed rate", "Square of feed rate", "Square root of feed rate", "Cube of feed rate"],
        "correct": 1
    },
    {
        "id": 68,
        "question": "Cutting fluids serve to:",
        "options": ["Cool the cutting zone", "Lubricate the interfaces", "Flush away chips", "All of the above"],
        "correct": 3
    },
    {
        "id": 69,
        "question": "Machinability index is based on:",
        "options": ["Tool life", "Surface finish", "Cutting forces", "All of the above"],
        "correct": 3
    },
    {
        "id": 70,
        "question": "Free-cutting steels have:",
        "options": ["High carbon content", "Sulfur or lead additions", "High alloy content", "Fine grain structure"],
        "correct": 1
    },
    {
        "id": 71,
        "question": "The most machinable material among the following is:",
        "options": ["Stainless steel", "Cast iron", "Free-cutting steel", "Titanium alloy"],
        "correct": 2
    },
    {
        "id": 72,
        "question": "Minimum quantity lubrication (MQL) uses:",
        "options": ["Flood cooling", "Mist cooling", "Dry cutting", "Cryogenic cooling"],
        "correct": 1
    },
    {
        "id": 73,
        "question": "Surface integrity includes:",
        "options": ["Surface finish", "Residual stresses", "Microstructural changes", "All of the above"],
        "correct": 3
    },
    {
        "id": 74,
        "question": "The recommended tool life for roughing operations is:",
        "options": ["5-15 minutes", "15-45 minutes", "45-90 minutes", "90-180 minutes"],
        "correct": 1
    },
    {
        "id": 75,
        "question": "Work hardening during machining affects:",
        "options": ["Tool life", "Surface finish", "Cutting forces", "All of the above"],
        "correct": 3
    }
]

# Store active quiz sessions
quiz_sessions = {}

def get_random_questions(num_questions=20):
    """Get random questions from the question bank"""
    return random.sample(QUESTION_BANK, min(num_questions, len(QUESTION_BANK)))

# HTML Template with enhanced security features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>20ME002 - MANUFACTURING PROCESSES II - Quiz</title>
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

        .warning-banner {
            background: #ff6b6b;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .malpractice-screen {
            background: #ff4757;
            color: white;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 9999;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }

        .malpractice-screen h1 {
            font-size: 3em;
            margin-bottom: 20px;
        }

        .malpractice-screen p {
            font-size: 1.5em;
            margin-bottom: 10px;
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

        .focus-warning {
            background: #ff9f43;
            color: white;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
            display: none;
        }
    </style>
</head>
<body>
    <!-- Malpractice Detection Screen -->
    <div class="malpractice-screen" id="malpracticeScreen">
        <h1>⚠️ MALPRACTICE DETECTED</h1>
        <p>You have switched away from the quiz window!</p>
        <p>The quiz has been automatically terminated.</p>
        <p style="font-size: 1.2em; margin-top: 30px;">Contact your instructor for further assistance.</p>
    </div>

    <div class="container">
        <div class="header">
            <h1>DEPARTMENT OF MECHANICAL ENGINEERING</h1>
            <div class="course-info">20ME002 - MANUFACTURING PROCESSES II</div>
            <div class="course-info">THEORY OF METAL CUTTING</div>
            <div class="quiz-details">Duration: 30 Minutes | Questions: 20 | Marks: 20</div>
        </div>

        <div class="warning-banner">
            ⚠️ WARNING: Do not switch windows or tabs during the quiz. Any attempt to leave this page will result in automatic quiz termination!
        </div>

        <div class="network-info">
            <h3>🌐 Quiz Server Information</h3>
            <p><strong>Server URL:</strong> <span id="serverUrl">Loading...</span></p>
            <p><strong>Status:</strong> <span style="color: #4CAF50;">● Online</span></p>
            <p><strong>Random Questions:</strong> 20 questions randomly selected from 75-question bank</p>
            <p>Share this URL with students on your network!</p>
        </div>

        <div class="content">
            <!-- Focus Warning -->
            <div class="focus-warning" id="focusWarning">
                ⚠️ Focus detected lost! Return to quiz immediately or it will be terminated!
            </div>

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
                    <li>Answer ALL questions - each question carries 1 mark</li>
                    <li>You will get 20 random questions from the question bank</li>
                    <li>Select the most appropriate answer for each question</li>
                    <li>No negative marking</li>
                    <li><strong>DO NOT switch windows, tabs, or minimize the browser</strong></li>
                    <li><strong>Any attempt to leave this page will terminate the quiz</strong></li>
                    <li>You have 30 minutes to complete the quiz</li>
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
                    Question <span id="currentQuestionNum">1</span> of 20
                </div>
            </div>

            <!-- Quiz Questions -->
            <div id="quizContainer" class="hidden">
                <!-- Questions will be dynamically loaded here -->
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
                <div class="score" id="finalScore">0/20</div>
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
        let quizQuestions = [];
        let sessionId = '';
        let focusLostCount = 0;
        let maxFocusLoss = 2;
        let isQuizActive = false;

        // Initialize
        window.onload = function() {
            document.getElementById('serverUrl').textContent = window.location.href;
            setupFocusDetection();
        };

        // Focus detection and malpractice prevention
        function setupFocusDetection() {
            let warningTimeout;

            // Detect when window loses focus
            window.addEventListener('blur', function() {
                if (!isQuizActive) return;
                
                focusLostCount++;
                console.log('Focus lost! Count:', focusLostCount);
                
                if (focusLostCount <= maxFocusLoss) {
                    showFocusWarning();
                    warningTimeout = setTimeout(() => {
                        triggerMalpractice('Window focus lost for too long');
                    }, 5000); // 5 seconds grace period
                } else {
                    triggerMalpractice('Multiple attempts to leave quiz detected');
                }
            });

            // Detect when window regains focus
            window.addEventListener('focus', function() {
                if (!isQuizActive) return;
                
                clearTimeout(warningTimeout);
                hideFocusWarning();
            });

            // Prevent right-click context menu
            document.addEventListener('contextmenu', function(e) {
                if (isQuizActive) {
                    e.preventDefault();
                    return false;
                }
            });

            // Prevent common keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (!isQuizActive) return;
                
                // Prevent F12 (DevTools)
                if (e.key === 'F12') {
                    e.preventDefault();
                    triggerMalpractice('Attempt to open developer tools');
                    return false;
                }
                
                // Prevent Ctrl+Shift+I (DevTools)
                if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                    e.preventDefault();
                    triggerMalpractice('Attempt to open developer tools');
                    return false;
                }
                
                // Prevent Ctrl+U (View Source)
                if (e.ctrlKey && e.key === 'u') {
                    e.preventDefault();
                    triggerMalpractice('Attempt to view page source');
                    return false;
                }
                
                // Prevent Alt+Tab (Switch windows)
                if (e.altKey && e.key === 'Tab') {
                    e.preventDefault();
                    triggerMalpractice('Attempt to switch windows');
                    return false;
                }
            });

            // Detect page visibility change (tab switching)
            document.addEventListener('visibilitychange', function() {
                if (!isQuizActive) return;
                
                if (document.hidden) {
                    focusLostCount++;
                    if (focusLostCount > maxFocusLoss) {
                        triggerMalpractice('Tab switching detected');
                    } else {
                        showFocusWarning();
                    }
                } else {
                    hideFocusWarning();
                }
            });
        }

        function showFocusWarning() {
            document.getElementById('focusWarning').style.display = 'block';
        }

        function hideFocusWarning() {
            document.getElementById('focusWarning').style.display = 'none';
        }

        function triggerMalpractice(reason) {
            console.log('Malpractice triggered:', reason);
            isQuizActive = false;
            clearInterval(timerInterval);
            
            // Send malpractice report to server
            fetch('/report_malpractice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    studentName: studentName,
                    registerNumber: registerNumber,
                    reason: reason,
                    timestamp: new Date().toISOString(),
                    sessionId: sessionId
                })
            });
            
            // Show malpractice screen
            document.getElementById('malpracticeScreen').style.display = 'flex';
        }

        async function startQuiz() {
            const name = document.getElementById('studentName').value.trim();
            const regNum = document.getElementById('registerNumber').value.trim();
            
            if (!name || !regNum) {
                alert('Please enter both name and register number!');
                return;
            }
            
            studentName = name;
            registerNumber = regNum;
            
            // Get random questions from server
            try {
                const response = await fetch('/get_random_questions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        studentName: studentName,
                        registerNumber: registerNumber
                    })
                });
                
                const data = await response.json();
                quizQuestions = data.questions;
                sessionId = data.sessionId;
                
                document.getElementById('studentForm').classList.add('hidden');
                document.getElementById('instructions').classList.remove('hidden');
            } catch (error) {
                alert('Error loading quiz questions. Please try again.');
                console.error('Error:', error);
            }
        }

        function beginQuiz() {
            isQuizActive = true;
            document.getElementById('instructions').classList.add('hidden');
            document.getElementById('timer').classList.remove('hidden');
            document.getElementById('progressContainer').classList.remove('hidden');
            document.getElementById('quizContainer').classList.remove('hidden');
            
            loadQuizQuestions();
            showQuestion(0);
            startTimer();
        }

        function loadQuizQuestions() {
            const container = document.getElementById('quizContainer');
            const navigation = container.querySelector('.navigation');
            
            quizQuestions.forEach((question, index) => {
                const questionDiv = document.createElement('div');
                questionDiv.className = 'question-container question';
                questionDiv.id = `question${index + 1}`;
                questionDiv.style.display = 'none';
                
                questionDiv.innerHTML = `
                    <div class="question-header">
                        <div class="question-number">Q${index + 1}</div>
                    </div>
                    <div class="question-text">${question.question}</div>
                    <div class="options">
                        ${question.options.map((option, optIndex) => `
                            <div class="option" onclick="selectOption(${index + 1}, ${optIndex})">
                                <input type="radio" name="q${index + 1}" value="${optIndex}" id="q${index + 1}_${optIndex}">
                                <label for="q${index + 1}_${optIndex}">${option}</label>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                container.insertBefore(questionDiv, navigation);
            });
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
            const progress = ((index + 1) / 20) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('currentQuestionNum').textContent = index + 1;
            
            // Update navigation buttons
            document.getElementById('prevBtn').disabled = index === 0;
            
            if (index === 19) {
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
            if (currentQuestion < 19) {
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
            if (Object.keys(answers).length < 20) {
                if (!confirm('You have not answered all questions. Are you sure you want to submit?')) {
                    return;
                }
            }
            
            isQuizActive = false;
            clearInterval(timerInterval);
            
            // Calculate score
            let score = 0;
            for (let i = 1; i <= 20; i++) {
                if (answers[i] === quizQuestions[i-1].correct) {
                    score++;
                }
            }
            
            // Show results
            document.getElementById('timer').classList.add('hidden');
            document.getElementById('progressContainer').classList.add('hidden');
            document.getElementById('quizContainer').classList.add('hidden');
            document.getElementById('resultsContainer').classList.remove('hidden');
            
            document.getElementById('finalScore').textContent = score + '/20';
            
            const percentage = (score / 20) * 100;
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
                    totalQuestions: 20,
                    timeTaken: (30 * 60) - timeRemaining,
                    sessionId: sessionId,
                    questions: quizQuestions
                })
            });
        }

        function downloadPDF() {
            window.open('/download_pdf/' + encodeURIComponent(studentName) + '/' + encodeURIComponent(registerNumber), '_blank');
        }

        // Prevent page unload during active quiz
        window.addEventListener('beforeunload', function(e) {
            if (isQuizActive) {
                e.preventDefault();
                e.returnValue = 'Are you sure you want to leave? This will terminate your quiz!';
                return 'Are you sure you want to leave? This will terminate your quiz!';
            }
        });
    </script>
</body>
</html>
"""

def get_local_ip():
    """Get the local IP address"""
    try:
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
        alignment=1
    )
    
    story.append(Paragraph("DEPARTMENT OF MECHANICAL ENGINEERING", title_style))
    story.append(Paragraph("20ME002 - MANUFACTURING PROCESSES II", styles['Heading2']))
    story.append(Paragraph("THEORY OF METAL CUTTING - QUIZ", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Student Information
    student_info = [
        ['Student Name:', student_data['studentName']],
        ['Register Number:', student_data['registerNumber']],
        ['Date:', datetime.datetime.now().strftime("%Y-%m-%d")],
        ['Time:', datetime.datetime.now().strftime("%H:%M:%S")],
        ['Duration:', f"{student_data['timeTaken']//60}:{student_data['timeTaken']%60:02d} minutes"],
        ['Questions:', f"20 (Random selection from 75-question bank)"],
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
    
    for i, question in enumerate(student_data['questions'], 1):
        user_answer_idx = student_data['answers'].get(str(i), -1)
        correct_answer_idx = question['correct']
        
        user_answer = question['options'][user_answer_idx] if user_answer_idx >= 0 else "Not Answered"
        correct_answer = question['options'][correct_answer_idx]
        status = "✓ Correct" if user_answer_idx == correct_answer_idx else "✗ Wrong"
        
        results_data.append([str(i), user_answer[:30] + "..." if len(user_answer) > 30 else user_answer, 
                           correct_answer[:30] + "..." if len(correct_answer) > 30 else correct_answer, status])
    
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
    
    story.append(Paragraph("This is an auto-generated report from random question selection.", footer_style))
    story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    
    # Build PDF
    doc.build(story)
    return filepath

@app.route('/')
def index():
    """Serve the quiz homepage"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_random_questions', methods=['POST'])
def get_random_questions_route():
    """Get 20 random questions for a student"""
    try:
        data = request.json
        student_name = data['studentName']
        register_number = data['registerNumber']
        
        # Generate random questions
        random_questions = get_random_questions(20)
        
        # Create session ID
        session_id = f"{register_number}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store session
        quiz_sessions[session_id] = {
            'studentName': student_name,
            'registerNumber': register_number,
            'questions': random_questions,
            'startTime': datetime.datetime.now().isoformat()
        }
        
        return jsonify({
            'questions': random_questions,
            'sessionId': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating questions: {str(e)}'
        }), 500

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
            'sessionId': data['sessionId'],
            'questions': data['questions'],
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

@app.route('/report_malpractice', methods=['POST'])
def report_malpractice():
    """Handle malpractice reports"""
    try:
        data = request.json
        
        # Log malpractice
        malpractice_log = {
            'studentName': data['studentName'],
            'registerNumber': data['registerNumber'],
            'reason': data['reason'],
            'timestamp': data['timestamp'],
            'sessionId': data['sessionId']
        }
        
        # Save to malpractice log file
        os.makedirs("malpractice_logs", exist_ok=True)
        log_filename = f"malpractice_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        log_filepath = os.path.join("malpractice_logs", log_filename)
        
        # Read existing logs
        logs = []
        if os.path.exists(log_filepath):
            with open(log_filepath, 'r') as f:
                logs = json.load(f)
        
        # Add new log
        logs.append(malpractice_log)
        
        # Write back
        with open(log_filepath, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return jsonify({'status': 'logged'})
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error logging malpractice: {str(e)}'
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
    """Enhanced admin panel"""
    try:
        results_dir = "quiz_results"
        malpractice_dir = "malpractice_logs"
        
        # Get quiz submissions
        pdf_files = []
        if os.path.exists(results_dir):
            files = os.listdir(results_dir)
            pdf_files = [f for f in files if f.endswith('.pdf')]
        
        # Get malpractice logs
        malpractice_count = 0
        if os.path.exists(malpractice_dir):
            for log_file in os.listdir(malpractice_dir):
                if log_file.endswith('.json'):
                    with open(os.path.join(malpractice_dir, log_file), 'r') as f:
                        logs = json.load(f)
                        malpractice_count += len(logs)
        
        html = f"""
        <html>
        <head>
            <title>Manufacturing Processes II - Quiz Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                .file-list {{ list-style: none; padding: 0; }}
                .file-item {{ background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .download-link {{ color: #007bff; text-decoration: none; font-weight: bold; }}
                .download-link:hover {{ text-decoration: underline; }}
                .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Manufacturing Processes II - Quiz Administration</h1>
                <p>20ME002 - Theory of Metal Cutting</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(pdf_files)}</div>
                    <div>Total Submissions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{malpractice_count}</div>
                    <div>Malpractice Cases</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">75</div>
                    <div>Question Bank Size</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{get_local_ip()}</div>
                    <div>Server IP</div>
                </div>
            </div>
        """
        
        if malpractice_count > 0:
            html += f'''
            <div class="warning">
                <strong>⚠️ Warning:</strong> {malpractice_count} malpractice case(s) detected! 
                <a href="/malpractice_logs" style="color: #d63031;">View Details</a>
            </div>
            '''
        
        html += '''
            <div class="section">
                <h3>Quiz Information</h3>
                <ul>
                    <li><strong>Course:</strong> 20ME002 - Manufacturing Processes II</li>
                    <li><strong>Topic:</strong> Theory of Metal Cutting</li>
                    <li><strong>Question Bank:</strong> 75 questions covering all topics</li>
                    <li><strong>Quiz Format:</strong> 20 random questions per student</li>
                    <li><strong>Duration:</strong> 30 minutes</li>
                    <li><strong>Security Features:</strong> Focus detection, tab switching prevention</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>Recent Quiz Submissions</h3>
        '''
        
        if pdf_files:
            html += '<ul class="file-list">'
            for pdf_file in sorted(pdf_files, reverse=True)[:10]:  # Show last 10
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
            
            if len(pdf_files) > 10:
                html += f'<p><em>Showing 10 most recent submissions. Total: {len(pdf_files)}</em></p>'
        else:
            html += '<p>No submissions yet.</p>'
        
        html += '''
            </div>
            
            <div class="section">
                <h3>Quick Actions</h3>
                <p><a href="/">&larr; Back to Quiz</a></p>
                <p><a href="/question_bank">View Question Bank</a></p>
                <p><a href="/malpractice_logs">View Malpractice Logs</a></p>
            </div>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f"Error loading admin panel: {str(e)}"

@app.route('/malpractice_logs')
def malpractice_logs():
    """View malpractice logs"""
    try:
        malpractice_dir = "malpractice_logs"
        all_logs = []
        
        if os.path.exists(malpractice_dir):
            for log_file in os.listdir(malpractice_dir):
                if log_file.endswith('.json'):
                    with open(os.path.join(malpractice_dir, log_file), 'r') as f:
                        logs = json.load(f)
                        all_logs.extend(logs)
        
        html = '''
        <html>
        <head>
            <title>Malpractice Logs</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .header { background: #e74c3c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
                .log-item { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c; }
                .timestamp { color: #666; font-size: 0.9em; }
                .reason { font-weight: bold; color: #e74c3c; }
                table { width: 100%; border-collapse: collapse; background: white; }
                th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
                th { background: #e74c3c; color: white; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 Malpractice Detection Logs</h1>
                <p>Security violations detected during quiz sessions</p>
            </div>
        '''
        
        if all_logs:
            html += '''
            <table>
                <tr>
                    <th>Student Name</th>
                    <th>Register Number</th>
                    <th>Violation</th>
                    <th>Timestamp</th>
                    <th>Session ID</th>
                </tr>
            '''
            
            for log in sorted(all_logs, key=lambda x: x['timestamp'], reverse=True):
                timestamp = datetime.datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                html += f'''
                <tr>
                    <td>{log['studentName']}</td>
                    <td>{log['registerNumber']}</td>
                    <td class="reason">{log['reason']}</td>
                    <td class="timestamp">{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    <td>{log['sessionId']}</td>
                </tr>
                '''
            
            html += '</table>'
        else:
            html += '<p>No malpractice cases detected. ✅</p>'
        
        html += '''
            <br>
            <p><a href="/admin">&larr; Back to Admin Panel</a></p>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f"Error loading malpractice logs: {str(e)}"

@app.route('/question_bank')
def question_bank():
    """View the complete question bank"""
    try:
        html = '''
        <html>
        <head>
            <title>Question Bank</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .header { background: #3498db; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
                .question { background: white; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
                .question-text { font-weight: bold; margin-bottom: 10px; }
                .options { margin-left: 20px; }
                .correct { color: #27ae60; font-weight: bold; }
                .option { margin: 5px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📚 Complete Question Bank</h1>
                <p>20ME002 - Manufacturing Processes II - Theory of Metal Cutting</p>
                <p>Total Questions: 75</p>
            </div>
        '''
        
        for i, question in enumerate(QUESTION_BANK, 1):
            html += f'''
            <div class="question">
                <div class="question-text">{i}. {question['question']}</div>
                <div class="options">
            '''
            
            for j, option in enumerate(question['options']):
                if j == question['correct']:
                    html += f'<div class="option correct">✓ {chr(97+j)}) {option}</div>'
                else:
                    html += f'<div class="option">{chr(97+j)}) {option}</div>'
            
            html += '</div></div>'
        
        html += '''
            <br>
            <p><a href="/admin">&larr; Back to Admin Panel</a></p>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f"Error loading question bank: {str(e)}"

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
    print("\n" + "="*70)
    print("🎓 MANUFACTURING PROCESSES II - QUIZ SERVER")
    print("="*70)
    print(f"📡 Server IP Address: {ip}")
    print(f"🌐 Quiz URL: http://{ip}:5000")
    print(f"⚙️  Admin Panel: http://{ip}:5000/admin")
    print(f"📁 Results Directory: {os.path.abspath('quiz_results')}")
    print(f"🚨 Malpractice Logs: {os.path.abspath('malpractice_logs')}")
    print("="*70)
    print("📋 Course Details:")
    print("   • Course Code: 20ME002")
    print("   • Course Name: Manufacturing Processes II")
    print("   • Topic: Theory of Metal Cutting")
    print("   • Question Bank: 75 questions")
    print("   • Quiz Format: 20 random questions per student")
    print("   • Duration: 30 minutes")
    print("="*70)
    print("🔒 Security Features:")
    print("   • Focus detection and monitoring")
    print("   • Tab switching prevention")
    print("   • Window blur detection")
    print("   • Keyboard shortcut blocking")
    print("   • Automatic malpractice logging")
    print("   • Quiz termination on violations")
    print("="*70)
    print("🚀 Instructions:")
    print("   1. Share the Quiz URL with students on your WiFi network")
    print("   2. Students enter their name and register number")
    print("   3. Each student gets 20 random questions from 75-question bank")
    print("   4. Quiz monitors for malpractice and terminates if detected")
    print("   5. Results are automatically saved as PDFs")
    print("   6. Use Admin Panel to view submissions and malpractice logs")
    print("   7. Press Ctrl+C to stop the server")
    print("="*70)
    print("✅ Server is running... Waiting for students!")
    print("⚠️  Security monitoring is ACTIVE!")
    print()

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs("quiz_results", exist_ok=True)
    os.makedirs("malpractice_logs", exist_ok=True)
    
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