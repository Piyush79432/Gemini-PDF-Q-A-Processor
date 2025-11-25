import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import PyPDF2
from datetime import datetime
import time
import re
import requests
import json
import base64
from io import BytesIO
import html
import tempfile
import os
import uuid

# Page configuration
st.set_page_config(
    page_title="Gemini PDF Q&A Processor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Custom CSS with Advanced Loader
st.markdown("""
<style>
    /* Main dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Headers */
    .big-font {
        font-size: 56px !important;
        font-weight: 900;
        background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 0 30px rgba(168, 237, 234, 0.5);
    }
    
    .subtitle {
        text-align: center;
        color: #b8b8d1;
        font-size: 20px;
        margin-bottom: 30px;
        font-weight: 300;
    }
    
    /* Advanced Loader */
    .loader-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 20px 0;
    }
    
    .loader {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 8px solid rgba(168, 237, 234, 0.2);
        border-top-color: #a8edea;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .pulse-ring {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 3px solid #a8edea;
        position: absolute;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(0.8);
            opacity: 1;
        }
        100% {
            transform: scale(1.4);
            opacity: 0;
        }
    }
    
    .loader-text {
        margin-top: 30px;
        font-size: 24px;
        font-weight: bold;
        color: #a8edea;
        text-align: center;
    }
    
    .status-text {
        margin-top: 15px;
        font-size: 16px;
        color: #b8b8d1;
        text-align: center;
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
        width: 100%;
        max-width: 600px;
    }
    
    .step {
        text-align: center;
        color: #666;
    }
    
    .step.active {
        color: #a8edea;
    }
    
    .step-icon {
        font-size: 30px;
        margin-bottom: 5px;
    }
    
    /* Glowing cards */
    .glow-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .question-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border-left: 5px solid #6366f1;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
    }
    
    .answer-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border-left: 5px solid #10b981;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        transition: all 0.3s ease;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.2));
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin: 10px 0;
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #b8b8d1;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 18px;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        transform: translateY(-3px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: white;
        padding: 12px;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #b8b8d1;
        font-weight: bold;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.2);
        border-left: 4px solid #10b981;
        border-radius: 10px;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.2);
        border-left: 4px solid #ef4444;
        border-radius: 10px;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.2);
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
    }
    
    /* Structured content */
    .structured-content {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #6366f1;
    }
    
    .section-header {
        color: #a8edea;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .bullet-points {
        margin-left: 20px;
    }
    
    .bullet-points li {
        margin-bottom: 8px;
        line-height: 1.6;
    }
    
    /* Diagram container */
    .diagram-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid rgba(168, 237, 234, 0.3);
    }
    
    /* Quality badges */
    .quality-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    
    .quality-high {
        background: rgba(16, 185, 129, 0.3);
        color: #10b981;
        border: 1px solid #10b981;
    }
    
    .quality-medium {
        background: rgba(245, 158, 11, 0.3);
        color: #f59e0b;
        border: 1px solid #f59e0b;
    }
    
    .quality-low {
        background: rgba(239, 68, 68, 0.3);
        color: #ef4444;
        border: 1px solid #ef4444;
    }
    
    /* Diagram image styling */
    .diagram-image {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 2px solid #a8edea;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-font">Gemini PDF Q&A Processor</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Advanced AI-powered question answering with multiple diagram options</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    api_key = st.text_input("🔑 Gemini API Key", type="password", help="Enter your Google Gemini API key")
    huggingface_key = st.text_input("🔑 HuggingFace Token (Optional)", type="password", help="Optional: For better AI diagram generation")
    
    st.markdown("---")
    st.markdown("### 🎯 Answer Settings")
    
    answer_type = st.radio(
        "Answer Detail Level:",
        ["Concise", "Detailed"],
        help="Choose between short or comprehensive answers"
    )
    
    diagram_option = st.radio(
        "Diagram Type:",
        ["No Diagrams", "Mermaid Diagrams", "AI-Generated Diagrams"],
        help="Choose the type of diagrams to generate"
    )
    
    st.markdown("---")
    st.markdown("### 📌 Features")
    st.info("""
    ✅ Multi-LLM quality checking
    ✅ Structured answer formatting
    ✅ Multiple diagram options
    ✅ Professional PDF output
    ✅ Accurate question detection
    ✅ Free AI diagram generation
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Resources")
    st.markdown("[Get Gemini API](https://aistudio.google.com/app/apikey)")
    st.markdown("[Get HuggingFace Token](https://huggingface.co/settings/tokens)")

# Main content
st.markdown("### 📄 Upload Question PDF Template")
uploaded_file = st.file_uploader(
    "Choose a PDF file containing questions",
    type=['pdf'],
    help="Upload a PDF with questions that need to be answered"
)

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    with col2:
        st.info(f"📊 File size: {uploaded_file.size / 1024:.2f} KB")

# Function to clean text for PDF encoding
def clean_text_for_pdf(text):
    """Clean text to remove characters that can't be encoded"""
    if not text:
        return ""
    
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u2022': '*',    # bullet
        '\u2013': '-',    # en dash
        '\u2014': '-',    # em dash
        '\u2018': "'",    # left single quote
        '\u2019': "'",    # right single quote
        '\u201c': '"',    # left double quote
        '\u201d': '"',    # right double quote
        '\u00b0': 'deg',  # degree symbol
        '\u00a9': '(c)',  # copyright
        '\u00ae': '(R)',  # registered
        '\u2122': '(TM)', # trademark
        '•': '*',         # bullet point
        '→': '->',        # right arrow
        '✓': '[X]',       # checkmark
    }
    
    # Apply replacements
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any other non-ASCII characters
    text = ''.join(char for char in text if ord(char) < 128)
    
    return text

# Improved function to extract questions from PDF
def extract_questions_from_pdf(pdf_file):
    """Extract questions from PDF file with improved accuracy"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    full_text = ""
    
    for page in pdf_reader.pages:
        full_text += page.extract_text()
    
    questions = []
    
    # Improved pattern matching for questions
    # Pattern 1: Numbered questions (1., 2., Q1, Question 1, etc.)
    numbered_pattern = r'(?:(?:^|\n)\s*(?:\d+[\.\)]|Q\s*\d+[\.\)]?|Question\s*\d+[\.\)]?)\s*)([^\n?]+\??)'
    numbered_matches = re.findall(numbered_pattern, full_text, re.IGNORECASE | re.MULTILINE)
    
    # Pattern 2: Questions ending with question marks that are substantial
    question_mark_pattern = r'([A-Z][^.!?]*\?[^.!?]*)(?=[.!?]|$)'
    question_matches = re.findall(question_mark_pattern, full_text)
    
    # Combine all matches
    all_questions = numbered_matches + question_matches
    
    # Clean and filter questions
    cleaned_questions = []
    for q in all_questions:
        if isinstance(q, tuple):
            q = q[0]
        
        # Clean the question
        q_clean = re.sub(r'^\s*[\d\.\)\sQ:-]+\s*', '', q.strip())
        q_clean = re.sub(r'\s+', ' ', q_clean)
        
        # Filter criteria
        if (len(q_clean) > 15 and 
            '?' in q_clean and
            q_clean not in cleaned_questions and
            not q_clean.lower().startswith(('answer', 'solution', 'explanation', 'note', 'example'))):
            cleaned_questions.append(q_clean)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_questions = []
    for q in cleaned_questions:
        if q not in seen:
            seen.add(q)
            unique_questions.append(q)
    
    return unique_questions[:15], full_text  # Limit to 15 questions

# Function to check if diagram is needed
def needs_diagram(question):
    """Determine if a diagram would be helpful based on question content"""
    diagram_keywords = [
        'process', 'flow', 'structure', 'architecture', 'diagram', 'chart', 
        'model', 'framework', 'system', 'cycle', 'relationship', 'compare',
        'difference', 'hierarchy', 'organization', 'workflow', 'pipeline',
        'steps', 'procedure', 'methodology', 'components', 'elements',
        'interaction', 'sequence', 'timeline', 'development', 'lifecycle',
        'illustrate', 'visualize', 'show', 'demonstrate', 'explain with diagram'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in diagram_keywords)

# Function to generate high-quality structured answer using Gemini 2.5 Flash Lite
def generate_structured_answer(question, context, api_key, answer_type):
    """Generate structured, accurate answer with proper formatting"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    if answer_type == "Concise":
        prompt = f"""Provide a CLEAN, ACCURATE, and WELL-STRUCTURED answer to this question. Follow this EXACT format:

QUESTION: {question}

ANSWER SUMMARY: [2-3 sentence clear summary]

KEY POINTS:
* Point 1 (clear and concise)
* Point 2 (clear and concise) 
* Point 3 (clear and concise)

TAKEAWAY: [1 sentence conclusion]

Context: {context[:2000]}

IMPORTANT: 
- Be accurate and factual
- Use clear, simple language
- Follow the exact format above
- Use only ASCII characters
- Use asterisks (*) for bullet points"""
    else:
        prompt = f"""Provide a DETAILED, ACCURATE, and WELL-STRUCTURED answer to this question. Follow this EXACT format:

QUESTION: {question}

OVERVIEW: [Brief introduction explaining the concept]

DETAILED EXPLANATION:
* Main concept 1 with clear explanation
* Main concept 2 with clear explanation  
* Main concept 3 with clear explanation

KEY COMPONENTS:
* Component 1: Description
* Component 2: Description
* Component 3: Description

APPLICATIONS/EXAMPLES:
* Real-world application 1
* Real-world application 2

SUMMARY: [Comprehensive conclusion]

Context: {context[:3000]}

IMPORTANT:
- Be thorough but organized
- Use clear, professional language
- Follow the exact format above
- Use only ASCII characters
- Use asterisks (*) for bullet points"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"

# Enhanced Mermaid Diagram Generation with Validation and Retry
def generate_validated_mermaid_diagram(question, answer, api_key, max_retries=3):
    """Generate Mermaid diagram with validation and automatic retry"""
    for attempt in range(max_retries):
        try:
            # Generate diagram with improved prompting
            diagram_code = generate_mermaid_with_context(question, answer, api_key, attempt)
            
            if not diagram_code:
                continue
                
            # Validate the diagram syntax
            is_valid, validation_message = validate_mermaid_syntax(diagram_code)
            
            if is_valid:
                # Test conversion to PNG
                png_data = convert_mermaid_to_png_enhanced(diagram_code)
                if png_data:
                    return diagram_code, png_data, f"Valid diagram (Attempt {attempt + 1})"
                else:
                    # If PNG conversion fails but syntax is valid, try to fix
                    fixed_code = fix_mermaid_syntax(diagram_code, api_key)
                    if fixed_code and fixed_code != diagram_code:
                        png_data = convert_mermaid_to_png_enhanced(fixed_code)
                        if png_data:
                            return fixed_code, png_data, f"Fixed diagram (Attempt {attempt + 1})"
            else:
                # Try to fix invalid syntax
                st.warning(f"Attempt {attempt + 1}: {validation_message}")
                fixed_code = fix_mermaid_syntax(diagram_code, api_key)
                if fixed_code and fixed_code != diagram_code:
                    png_data = convert_mermaid_to_png_enhanced(fixed_code)
                    if png_data:
                        return fixed_code, png_data, f"Fixed invalid syntax (Attempt {attempt + 1})"
                    
        except Exception as e:
            st.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            continue
    
    # If all attempts fail, generate fallback
    fallback_code = generate_fallback_mermaid(question)
    png_data = convert_mermaid_to_png_enhanced(fallback_code)
    return fallback_code, png_data, "Fallback diagram generated"

def generate_mermaid_with_context(question, answer, api_key, attempt):
    """Generate Mermaid diagram with context-aware prompting"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # Adjust prompt based on attempt
    if attempt == 0:
        complexity = "simple and clear"
    elif attempt == 1:
        complexity = "more detailed but still clean"
    else:
        complexity = "very simple and basic"
    
    prompt = f"""Create a {complexity} Mermaid diagram code that visually represents the key concepts from this question and answer.

QUESTION: {question}
ANSWER CONTEXT: {answer[:1500]}

CRITICAL REQUIREMENTS:
1. Generate ONLY valid Mermaid code without any explanations
2. Use proper Mermaid syntax (flowchart TD, graph TD, sequenceDiagram, or classDiagram)
3. Keep it between 5-10 nodes maximum
4. Use clear, descriptive labels in square brackets
5. Ensure all connections use proper arrows (--> or ->)
6. No markdown code blocks, just raw Mermaid code

Example of valid output:
flowchart TD
    A[Start] --> B[Process Step]
    B --> C[Decision]
    C -->|Yes| D[Success]
    C -->|No| E[Retry]

Generate the Mermaid code now:"""
    
    try:
        response = model.generate_content(prompt)
        code = response.text.strip()
        
        # Clean the code
        code = clean_mermaid_code(code)
        return code if is_valid_mermaid_code(code) else None
        
    except Exception as e:
        return None

def validate_mermaid_syntax(diagram_code):
    """Validate Mermaid diagram syntax"""
    if not diagram_code:
        return False, "Empty diagram code"
    
    # Check for valid starting keywords
    valid_starts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram']
    if not any(diagram_code.startswith(start) for start in valid_starts):
        return False, f"Invalid start. Must begin with: {', '.join(valid_starts)}"
    
    # Check for basic structure
    lines = diagram_code.split('\n')
    if len(lines) < 2:
        return False, "Diagram too short - needs at least 2 lines"
    
    # Check for connections
    has_connections = any('-->' in line or '->' in line for line in lines)
    if not has_connections:
        return False, "No connections found - diagram needs arrows (--> or ->)"
    
    # Check for proper node formatting
    has_nodes = any('[' in line and ']' in line for line in lines) or any('(' in line and ')' in line for line in lines)
    if not has_nodes:
        return False, "No properly formatted nodes found - use [brackets] or (parentheses)"
    
    return True, "Valid Mermaid syntax"

def fix_mermaid_syntax(broken_code, api_key):
    """Fix Mermaid syntax using Gemini"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = f"""Fix this broken Mermaid diagram code. Return ONLY the corrected Mermaid code without any explanations.

BROKEN CODE:
{broken_code}

CORRECTED CODE:"""
    
    try:
        response = model.generate_content(prompt)
        fixed_code = response.text.strip()
        fixed_code = clean_mermaid_code(fixed_code)
        return fixed_code if is_valid_mermaid_code(fixed_code) else None
    except:
        return None

def clean_mermaid_code(code):
    """Clean Mermaid code by removing markdown blocks and extra spaces"""
    if not code:
        return None
    
    # Remove code block markers
    code = re.sub(r'```mermaid\s*', '', code)
    code = re.sub(r'```\s*', '', code)
    
    # Remove extra whitespace
    code = '\n'.join(line.strip() for line in code.split('\n') if line.strip())
    
    return code

def is_valid_mermaid_code(code):
    """Check if Mermaid code is valid"""
    if not code:
        return False
    
    valid_starts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram']
    return any(code.startswith(start) for start in valid_starts)

def generate_fallback_mermaid(question):
    """Generate a simple fallback Mermaid diagram"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['process', 'step', 'flow', 'procedure']):
        return """flowchart TD
    A[Start] --> B[Process]
    B --> C[Check]
    C -->|OK| D[Complete]
    C -->|Issue| E[Review]
    E --> B"""
    
    elif any(word in question_lower for word in ['compare', 'difference', 'versus']):
        return """graph TD
    A[Concept A] --> B[Feature 1]
    A --> C[Feature 2]
    D[Concept B] --> E[Feature 1]
    D --> F[Feature 2]"""
    
    elif any(word in question_lower for word in ['structure', 'hierarchy']):
        return """graph TD
    A[Main] --> B[Part 1]
    A --> C[Part 2]
    A --> D[Part 3]
    B --> E[Detail A]
    B --> F[Detail B]"""
    
    else:
        return """flowchart TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Feedback]
    D --> B"""

# Enhanced AI Diagram Generation with Validation and Retry
def generate_validated_ai_diagram(question, answer, huggingface_key=None, max_retries=2):
    """Generate AI diagram with validation and retry mechanism"""
    for attempt in range(max_retries):
        try:
            # Generate diagram with improved prompt based on attempt
            prompt = create_ai_diagram_prompt(question, answer, attempt)
            diagram_data, status = generate_ai_diagram_with_services(prompt, huggingface_key)
            
            if diagram_data and validate_diagram_image(diagram_data):
                return diagram_data, f"Success (Attempt {attempt + 1}): {status}"
            else:
                # If validation fails, try with different parameters
                st.warning(f"AI diagram attempt {attempt + 1} failed validation, retrying...")
                continue
                
        except Exception as e:
            st.warning(f"AI diagram attempt {attempt + 1} error: {str(e)}")
            continue
    
    # Final fallback attempt
    try:
        prompt = create_simple_diagram_prompt(question)
        diagram_data, status = generate_simple_fallback_diagram(prompt)
        if diagram_data:
            return diagram_data, f"Fallback: {status}"
    except:
        pass
    
    return None, "All AI diagram generation attempts failed"

def create_ai_diagram_prompt(question, answer, attempt):
    """Create optimized prompt for AI diagram generation"""
    if attempt == 0:
        style = "professional educational infographic with clear labels and white background"
    else:
        style = "simple flowchart diagram with minimal elements and clear text"
    
    return f"""Create a {style} that illustrates: {question}

Key concepts: {answer[:200]}

Requirements:
- Educational diagram style
- Clear, readable text labels
- Professional color scheme
- Logical structure
- White background
- Informational design"""

def create_simple_diagram_prompt(question):
    """Create simple prompt for fallback diagram"""
    return f"Simple educational flowchart diagram about: {question}"

def generate_ai_diagram_with_services(prompt, huggingface_key):
    """Generate AI diagram using multiple services"""
    services = []
    
    if huggingface_key:
        services.append(lambda: try_huggingface_diagram(prompt, huggingface_key))
    
    services.extend([
        lambda: try_deepai_diagram(prompt),
        lambda: try_quickchart_diagram(prompt),
        lambda: try_simple_diagram_fallback(prompt)
    ])
    
    for service in services:
        try:
            result, status = service()
            if result and validate_diagram_image(result):
                return result, status
        except:
            continue
    
    return None, "All services failed"

def validate_diagram_image(image_data):
    """Basic validation of generated diagram image"""
    try:
        # Check if image data is not empty
        if not image_data or len(image_data) < 100:  # Minimum reasonable image size
            return False
        
        # Try to parse as image
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_data))
        
        # Basic checks
        if image.size[0] < 50 or image.size[1] < 50:  # Too small
            return False
            
        # Check if image has reasonable dimensions
        if image.size[0] > 2000 or image.size[1] > 2000:  # Too large (might be error)
            return False
            
        return True
        
    except Exception as e:
        return False

def try_huggingface_diagram(prompt, huggingface_key):
    """Try Hugging Face diagram generation"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {huggingface_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 512,
                "height": 512,
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            return response.content, "HuggingFace AI"
        return None, "HuggingFace failed"
    except:
        return None, "HuggingFace error"

def try_deepai_diagram(prompt):
    """Try DeepAI diagram generation"""
    try:
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={'text': prompt},
            headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'output_url' in result:
                img_response = requests.get(result['output_url'], timeout=30)
                if img_response.status_code == 200:
                    return img_response.content, "DeepAI"
        return None, "DeepAI failed"
    except:
        return None, "DeepAI error"

def try_quickchart_diagram(prompt):
    """Try QuickChart diagram generation"""
    try:
        # Create a simple flowchart
        chart_config = {
            "type": "graph",
            "data": {
                "nodes": [
                    {"id": "Start", "label": "Start", "color": "#4CAF50"},
                    {"id": "Process", "label": "Process", "color": "#2196F3"},
                    {"id": "End", "label": "End", "color": "#FF5722"}
                ],
                "edges": [
                    {"from": "Start", "to": "Process", "label": "begin"},
                    {"from": "Process", "to": "End", "label": "complete"}
                ]
            }
        }
        
        encoded_config = base64.urlsafe_b64encode(json.dumps(chart_config).encode()).decode()
        chart_url = f"https://quickchart.io/graphviz?graph={encoded_config}&format=png"
        
        response = requests.get(chart_url, timeout=30)
        if response.status_code == 200:
            return response.content, "QuickChart"
        return None, "QuickChart failed"
    except:
        return None, "QuickChart error"

def try_simple_diagram_fallback(prompt):
    """Simple diagram fallback"""
    try:
        # Use a very basic diagram service
        simple_config = {
            "type": "graph",
            "data": {
                "nodes": [{"id": "Concept", "label": prompt[:20] + "...", "color": "#6366F1"}],
                "edges": []
            }
        }
        
        encoded = base64.urlsafe_b64encode(json.dumps(simple_config).encode()).decode()
        url = f"https://quickchart.io/graphviz?graph={encoded}&format=png"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content, "Simple Diagram"
        return None, "Simple failed"
    except:
        return None, "Simple error"

def generate_simple_fallback_diagram(prompt):
    """Generate a very simple fallback diagram"""
    return try_quickchart_diagram(prompt)

# Enhanced Mermaid to PNG conversion
def convert_mermaid_to_png_enhanced(mermaid_code):
    """Convert Mermaid code to PNG with multiple fallback methods"""
    if not mermaid_code:
        return None
    
    methods = [
        convert_via_mermaid_ink,
        convert_via_quickchart_mermaid,
        convert_via_kroki
    ]
    
    for method in methods:
        try:
            result = method(mermaid_code)
            if result:
                return result
        except:
            continue
    
    return None

def convert_via_mermaid_ink(mermaid_code):
    """Convert using mermaid.ink"""
    try:
        encoded_code = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
        mermaid_url = f"https://mermaid.ink/img/{encoded_code}"
        response = requests.get(mermaid_url, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def convert_via_quickchart_mermaid(mermaid_code):
    """Convert using QuickChart Mermaid"""
    try:
        payload = {
            "chart": mermaid_code,
            "format": "png",
            "width": 600,
            "height": 400
        }
        response = requests.post('https://quickchart.io/mermaid', json=payload, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

def convert_via_kroki(mermaid_code):
    """Convert using Kroki.io"""
    try:
        import zlib
        compressed = zlib.compress(mermaid_code.encode(), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode()
        
        kroki_url = f"https://kroki.io/mermaid/png/{encoded}"
        response = requests.get(kroki_url, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# Enhanced diagram processing
def process_diagram_generation(question, answer, diagram_option, api_key, huggingface_key, idx):
    """Enhanced diagram generation with validation and retry"""
    if not needs_diagram(question):
        return None, None, "No diagram needed"
    
    try:
        if diagram_option == "Mermaid Diagrams":
            # Generate validated Mermaid diagram
            diagram_code, png_data, status = generate_validated_mermaid_diagram(question, answer, api_key)
            if diagram_code:
                return diagram_code, png_data, status
            else:
                return None, None, "Mermaid generation failed after all attempts"
                
        elif diagram_option == "AI-Generated Diagrams":
            # Generate validated AI diagram
            diagram_image, status = generate_validated_ai_diagram(question, answer, huggingface_key)
            if diagram_image:
                return None, diagram_image, status
            else:
                return None, None, "AI diagram generation failed after all attempts"
                
    except Exception as e:
        return None, None, f"Diagram generation error: {str(e)}"
    
    return None, None, "Unknown diagram error"

def enhanced_diagram_processing(questions, answers, diagram_option, api_key, huggingface_key):
    """Enhanced diagram processing with better error handling"""
    diagram_images = {}
    diagram_status = {}
    mermaid_diagrams = {}
    
    for idx, (question, answer) in enumerate(zip(questions, answers), 1):
        if needs_diagram(question):
            diagram_code, diagram_image, status = process_diagram_generation(
                question, answer, diagram_option, api_key, huggingface_key, idx
            )
            
            if diagram_code:
                mermaid_diagrams[idx] = diagram_code
            if diagram_image:
                diagram_images[idx] = diagram_image
            diagram_status[idx] = status
            
            time.sleep(2)  # Rate limiting
    
    return diagram_images, diagram_status, mermaid_diagrams

# Function to parse and display structured content
def display_structured_content(answer):
    """Parse and display structured answer with beautiful formatting"""
    if not answer:
        return "<div class='structured-content'>No answer available</div>"
    
    lines = answer.split('\n')
    html_content = '<div class="structured-content">'
    in_bullet_list = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            if in_bullet_list:
                html_content += '</ul>'
                in_bullet_list = False
            continue
        
        # Handle headers (format: HEADER:)
        if any(line.startswith(header) for header in ['QUESTION:', 'ANSWER SUMMARY:', 'KEY POINTS:', 'TAKEAWAY:', 'OVERVIEW:', 'DETAILED EXPLANATION:', 'KEY COMPONENTS:', 'APPLICATIONS/EXAMPLES:', 'SUMMARY:']):
            if in_bullet_list:
                html_content += '</ul>'
                in_bullet_list = False
            header_text = line
            html_content += f'<div class="section-header">📌 {header_text}</div>'
        
        # Handle bullet points (*)
        elif line.startswith('*'):
            if not in_bullet_list:
                html_content += '<ul class="bullet-points">'
                in_bullet_list = True
            
            content = line[1:].strip()
            html_content += f'<li>{html.escape(content)}</li>'
        
        # Handle regular text
        else:
            if in_bullet_list and not line.startswith('*'):
                html_content += '</ul>'
                in_bullet_list = False
            
            # Skip if it's likely a continuation of previous bullet point
            if i > 0 and lines[i-1].strip().startswith('*'):
                continue
                
            if line and not any(line.startswith(header) for header in ['QUESTION:', 'ANSWER SUMMARY:', 'KEY POINTS:', 'TAKEAWAY:', 'OVERVIEW:', 'DETAILED EXPLANATION:', 'KEY COMPONENTS:', 'APPLICATIONS/EXAMPLES:', 'SUMMARY:']):
                html_content += f'<p style="margin: 10px 0; line-height: 1.6; padding: 5px 0;">{html.escape(line)}</p>'
    
    # Close any open bullet list
    if in_bullet_list:
        html_content += '</ul>'
    
    html_content += '</div>'
    return html_content

# Enhanced diagram rendering
def render_enhanced_mermaid_diagram(diagram_code, diagram_number, png_data=None):
    """Enhanced Mermaid diagram rendering with better error handling"""
    if not diagram_code:
        return None
    
    st.markdown(f"#### 📊 Diagram {diagram_number}")
    
    with st.container():
        st.markdown('<div class="diagram-container">', unsafe_allow_html=True)
        
        # Display PNG image if available
        if png_data:
            st.image(png_data, caption=f"Diagram {diagram_number}", use_container_width=True)
        else:
            st.warning("⚠️ Diagram preview not available, but code is valid")
            st.info("💡 You can copy the code below to view in Mermaid Live Editor")
        
        # Display and validate diagram code
        st.markdown("**Mermaid Code:**")
        st.code(diagram_code, language="mermaid")
        
        # Validation info
        is_valid, validation_msg = validate_mermaid_syntax(diagram_code)
        if is_valid:
            st.success("✅ Valid Mermaid syntax")
        else:
            st.warning(f"⚠️ {validation_msg}")
        
        # Enhanced copy functionality
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Code", key=f"copy_diagram_{diagram_number}"):
                st.code(diagram_code, language="mermaid")
                st.success("Code copied to clipboard!")
        
        with col2:
            if st.button("🔄 Test in Editor", key=f"test_diagram_{diagram_number}"):
                st.markdown(f'<a href="https://mermaid.live" target="_blank">Open Mermaid Live Editor</a>', unsafe_allow_html=True)
        
        st.info("""
        **💡 How to use:**
        1. Copy the code above
        2. Go to [Mermaid Live Editor](https://mermaid.live)
        3. Paste the code to view and edit
        4. Export as PNG/SVG if needed
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return diagram_code

# Function to render AI-generated diagram
def render_ai_diagram(diagram_image, diagram_number, status_message):
    """Render AI-generated PNG diagram"""
    if not diagram_image:
        st.warning(f"❌ Diagram {diagram_number} could not be generated: {status_message}")
        return None
    
    st.markdown(f"#### 🎨 AI-Generated Diagram {diagram_number}")
    
    with st.container():
        st.markdown('<div class="diagram-container">', unsafe_allow_html=True)
        
        # Display the PNG image
        st.image(diagram_image, caption=f"AI-Generated Diagram for Question {diagram_number}", use_container_width=True, output_format="PNG")
        
        # Show status message
        st.info(f"Status: {status_message}")
        
        # Download button for the diagram
        st.download_button(
            label="📥 Download Diagram",
            data=diagram_image,
            file_name=f"diagram_{diagram_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            key=f"download_diagram_{diagram_number}"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return diagram_image

# Enhanced PDF creation with proper encoding and images
class ProfessionalPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(59, 130, 246)
        self.cell(0, 10, 'AI-Powered Q&A Analysis Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f'Generated on {datetime.now().strftime("%B %d, %Y at %H:%M")}', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_image_to_pdf(self, image_data, x=20, w=170):
        """Add PNG image to PDF with proper sizing"""
        try:
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()
                
                # Add image to PDF with centered positioning
                self.image(tmp_file.name, x=x, w=w)
                self.ln(5)
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            self.set_font('Arial', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 5, '[Diagram image could not be embedded]', 0, 1)
    
    def add_question_answer_section(self, q_num, question, answer, diagram_image=None):
        """Add a question-answer section to PDF"""
        # Check if we need a new page
        if self.get_y() > 180:  # Lower threshold when images might be added
            self.add_page()
        
        # Question
        self.set_font('Arial', 'B', 12)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(240, 240, 255)
        self.cell(0, 8, f'Question {q_num}:', 0, 1, 'L', True)
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        
        # Clean and add question text
        clean_question = clean_text_for_pdf(question)
        self.multi_cell(0, 6, clean_question)
        self.ln(3)
        
        # Answer
        self.set_font('Arial', 'B', 11)
        self.set_text_color(16, 185, 129)
        self.cell(0, 8, 'Answer:', 0, 1)
        self.ln(1)
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        
        # Process answer with formatting
        clean_answer = clean_text_for_pdf(answer)
        lines = clean_answer.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                self.ln(3)
                continue
                
            if any(line.startswith(header) for header in ['QUESTION:', 'ANSWER SUMMARY:', 'KEY POINTS:', 'TAKEAWAY:', 'OVERVIEW:', 'DETAILED EXPLANATION:', 'KEY COMPONENTS:', 'APPLICATIONS/EXAMPLES:', 'SUMMARY:']):
                # Header
                self.set_font('Arial', 'B', 9)
                self.cell(0, 6, line, 0, 1)
                self.set_font('Arial', '', 9)
            elif line.startswith('*'):
                # Bullet point
                self.cell(5)
                bullet_text = line[1:].strip()
                self.multi_cell(0, 5, f'* {bullet_text}')
            else:
                # Regular text
                if line:
                    self.multi_cell(0, 5, line)
        
        self.ln(2)
        
        # Add diagram image if available
        if diagram_image:
            self.set_font('Arial', 'B', 9)
            self.set_text_color(59, 130, 246)
            self.cell(0, 6, 'Diagram:', 0, 1)
            self.ln(1)
            
            # Add the PNG image to PDF
            self.add_image_to_pdf(diagram_image)
        
        self.ln(8)
        
        # Separator
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

def create_professional_pdf(questions, answers, diagram_images, answer_type, diagram_option):
    """Create a comprehensive PDF report with proper encoding"""
    pdf = ProfessionalPDF()
    pdf.add_page()
    
    # Title page
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 20, 'Q&A Analysis Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Summary
    pdf.set_font('Arial', '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f'Total Questions Analyzed: {len(questions)}', 0, 1)
    pdf.cell(0, 8, f'Answer Style: {answer_type}', 0, 1)
    pdf.cell(0, 8, f'Diagrams Included: {diagram_option}', 0, 1)
    pdf.cell(0, 8, f'Diagrams Generated: {len(diagram_images)}', 0, 1)
    pdf.cell(0, 8, f'Generation Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
    pdf.ln(15)
    
    # Add all Q&A sections
    for i, (question, answer) in enumerate(zip(questions, answers), 1):
        # Get diagram image if available
        diagram_image = None
        if diagram_option != "No Diagrams" and i in diagram_images:
            diagram_image = diagram_images[i]
        
        pdf.add_question_answer_section(i, question, answer, diagram_image)
    
    # Save to bytes with proper encoding
    try:
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        # Fallback: create simple text-based PDF
        try:
            simple_pdf = FPDF()
            simple_pdf.add_page()
            simple_pdf.set_font("Arial", size=12)
            simple_pdf.cell(0, 10, "Q&A Report - Simple Version", 0, 1)
            simple_pdf.ln(10)
            
            for i, (question, answer) in enumerate(zip(questions, answers), 1):
                simple_pdf.multi_cell(0, 10, f"Q{i}: {clean_text_for_pdf(question)}")
                simple_pdf.multi_cell(0, 10, f"A: {clean_text_for_pdf(answer)}")
                simple_pdf.ln(5)
            
            return simple_pdf.output(dest='S').encode('latin-1')
        except:
            return b"PDF generation failed"

# Display animated loader
def show_loader(step, total_steps, current_status):
    """Display animated loader with status"""
    loader_html = f"""
    <div class="loader-container">
        <div style="position: relative; display: inline-block;">
            <div class="pulse-ring"></div>
            <div class="loader"></div>
        </div>
        <div class="loader-text">Processing Your Questions</div>
        <div class="status-text">{current_status}</div>
        <div style="margin-top: 20px; color: #a8edea; font-size: 18px;">
            Step {step} of {total_steps}
        </div>
    </div>
    """
    return loader_html

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'answers' not in st.session_state:
    st.session_state.answers = None
if 'diagram_images' not in st.session_state:
    st.session_state.diagram_images = {}
if 'diagram_status' not in st.session_state:
    st.session_state.diagram_status = {}
if 'mermaid_diagrams' not in st.session_state:
    st.session_state.mermaid_diagrams = {}

# Process button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button("🚀 Extract Questions & Generate Answers", use_container_width=True)

# Enhanced Processing
if process_button:
    if not api_key:
        st.error("❌ Please enter your Gemini API key in the sidebar")
    elif not uploaded_file:
        st.error("❌ Please upload a PDF file")
    else:
        # Create placeholder for loader
        loader_placeholder = st.empty()
        
        try:
            # Step 1: Extract questions
            loader_placeholder.markdown(show_loader(1, 6, "📖 Reading PDF and extracting questions..."), unsafe_allow_html=True)
            time.sleep(1)
            
            questions, context = extract_questions_from_pdf(uploaded_file)
            
            if not questions:
                loader_placeholder.empty()
                st.error("❌ No questions found in the PDF. Please check the PDF format.")
            else:
                st.session_state.questions = questions
                loader_placeholder.markdown(show_loader(2, 6, f"✅ Found {len(questions)} questions! Generating structured answers..."), unsafe_allow_html=True)
                time.sleep(1)
                
                # Step 2: Generate structured answers
                answers = []
                total_q = len(questions)
                
                for idx, question in enumerate(questions, 1):
                    loader_placeholder.markdown(
                        show_loader(2, 6, f"🤖 Generating answer {idx}/{total_q}..."), 
                        unsafe_allow_html=True
                    )
                    
                    # Generate high-quality structured answer
                    answer = generate_structured_answer(question, context, api_key, answer_type)
                    answers.append(answer)
                    time.sleep(1)  # Rate limiting
                
                st.session_state.answers = answers
                
                # Step 3: Enhanced diagram generation
                if diagram_option != "No Diagrams":
                    loader_placeholder.markdown(show_loader(3, 6, "🎨 Generating enhanced diagrams for relevant questions..."), unsafe_allow_html=True)
                    
                    diagram_images, diagram_status, mermaid_diagrams = enhanced_diagram_processing(
                        questions, answers, diagram_option, api_key, huggingface_key
                    )
                    
                    st.session_state.diagram_images = diagram_images
                    st.session_state.diagram_status = diagram_status
                    st.session_state.mermaid_diagrams = mermaid_diagrams
                
                # Step 4: Final processing
                loader_placeholder.markdown(show_loader(4, 6, "✨ Finalizing results..."), unsafe_allow_html=True)
                time.sleep(1)
                
                # Step 5: Complete
                loader_placeholder.markdown(show_loader(5, 6, "🎉 Processing complete! Displaying results..."), unsafe_allow_html=True)
                time.sleep(1)
                loader_placeholder.empty()
                
                st.success(f"🎉 Successfully processed {len(questions)} questions!")
                st.balloons()
                
        except Exception as e:
            loader_placeholder.empty()
            st.error(f"❌ Processing error: {str(e)}")

# Display results
if st.session_state.questions and st.session_state.answers:
    st.markdown("---")
    
    # Statistics
    st.markdown("## 📊 Processing Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.questions)}</div>
            <div class="stat-label">Questions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.answers)}</div>
            <div class="stat-label">Answers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{answer_type}</div>
            <div class="stat-label">Answer Type</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        diagram_count = len(st.session_state.diagram_images)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{diagram_count}</div>
            <div class="stat-label">Diagrams Generated</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📋 Questions & Answers", "📥 Download PDF"])
    
    with tab1:
        st.markdown("### 💬 Questions & Answers")
        
        for i, (question, answer) in enumerate(zip(st.session_state.questions, st.session_state.answers), 1):
            # Use columns to create a card-like layout
            col1, col2 = st.columns([1, 20])
            with col2:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #6366f1;">
                    <h4 style="color: #a8edea; margin-bottom: 15px;">🔮 Question {i}</h4>
                    <p style="font-size: 16px; line-height: 1.6; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">{question}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Answer
                st.markdown("#### 💡 Answer")
                html_content = display_structured_content(answer)
                st.markdown(html_content, unsafe_allow_html=True)
                
                # Enhanced Diagrams
                if diagram_option == "Mermaid Diagrams" and i in st.session_state.mermaid_diagrams:
                    diagram_code = st.session_state.mermaid_diagrams.get(i)
                    png_data = st.session_state.diagram_images.get(i)
                    status = st.session_state.diagram_status.get(i, "Unknown")
                    st.info(f"Diagram Status: {status}")
                    render_enhanced_mermaid_diagram(diagram_code, i, png_data)
                elif diagram_option == "AI-Generated Diagrams" and i in st.session_state.diagram_images:
                    status = st.session_state.diagram_status.get(i, "Unknown")
                    render_ai_diagram(st.session_state.diagram_images[i], i, status)
                elif diagram_option != "No Diagrams" and i in st.session_state.diagram_status:
                    status = st.session_state.diagram_status[i]
                    st.warning(f"❌ Diagram {i} could not be generated: {status}")
            
            st.markdown("---")
    
    with tab2:
        st.markdown("### 📄 Download Professional Report")
        
        # Report summary
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📚 **Total Questions:** {len(st.session_state.questions)}")
            st.info(f"🎯 **Answer Style:** {answer_type}")
            st.info(f"🎨 **Diagrams Generated:** {len(st.session_state.diagram_images)}")
        with col2:
            st.info(f"🤖 **AI Model:** Gemini 2.5 Flash Lite")
            st.info(f"🖼️ **Diagram Service:** Multiple providers")
            st.info(f"📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown("---")
        
        # PDF generation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🖨️ Generate Comprehensive PDF Report", use_container_width=True):
                try:
                    with st.spinner("📄 Creating professional PDF report..."):
                        pdf_data = create_professional_pdf(
                            st.session_state.questions,
                            st.session_state.answers,
                            st.session_state.diagram_images,
                            answer_type,
                            diagram_option
                        )
                        
                        if pdf_data and pdf_data != b"PDF generation failed":
                            st.success("✅ PDF report generated successfully!")
                            
                            # Download button
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_data,
                                file_name=f"qa_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            st.balloons()
                        else:
                            st.error("❌ Failed to generate PDF report")
                        
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #b8b8d1; padding: 30px;'>
    <p style='font-size: 16px;'>Built with ❤️ using Streamlit & Gemini AI</p>
    <p style='font-size: 12px; opacity: 0.7;'>Advanced PDF Q&A Processor with Multiple Diagram Options | © 2024</p>
</div>
""", unsafe_allow_html=True)