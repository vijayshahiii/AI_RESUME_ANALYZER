from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import PyPDF3
import docx
from ml_model import ResumeAnalyzerML

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize ML model
ml_analyzer = ResumeAnalyzerML()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF3.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return None

def extract_text(file_path, filename):
    """Extract text based on file type"""
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        return extract_text_from_txt(file_path)
    
    return None

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Analyze uploaded resume"""
    
    # Check if file is present
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text
        text = extract_text(file_path, filename)
        
        if not text or len(text.strip()) < 50:
            os.remove(file_path)
            return jsonify({'error': 'Could not extract text from file or file is too short'}), 400
        
        # Analyze with ML model
        analysis_result = ml_analyzer.analyze_complete(text)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify(analysis_result)
    
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/demo')
def get_demo_resume():
    """Get demo resume analysis"""
    try:
        with open('demo_resume.txt', 'r', encoding='utf-8') as f:
            demo_text = f.read()
        
        analysis_result = ml_analyzer.analyze_complete(demo_text)
        return jsonify(analysis_result)
    
    except Exception as e:
        print(f"Error with demo: {e}")
        return jsonify({'error': 'Demo resume not found'}), 404

@app.route('/download-demo')
def download_demo():
    """Download demo resume file"""
    try:
        return send_file('demo_resume.txt', as_attachment=True, download_name='demo_resume.txt')
    except:
        return jsonify({'error': 'Demo file not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)