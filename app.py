from flask import Flask, render_template, request, jsonify
from transformers import pipeline
from gtts import gTTS
import os
import fitz  # PyMuPDF to handle PDF extraction
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
import spacy
import requests




app = Flask(__name__)

# Load models and spaCy
summarizer = pipeline("summarization", model="t5-base")
UPLOAD_FOLDER = 'uploads'
nlp = spacy.load('en_core_web_sm')


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

context_text=""
def process_text(input_text):
    """
    This function will handle text processing:
    - Clean up extra spaces
    - Remove unnecessary characters, etc.
    """
    # This is a simple cleanup step, you can add more advanced text preprocessing as needed
    global context_text 
    cleaned_text = input_text.strip()  # Remove leading/trailing whitespaces
    context_text = cleaned_text
    return cleaned_text

def extract_text_from_pdf(pdf_file):
    """
    This function will extract text from the uploaded PDF file using PyMuPDF.
    """
    global context_text 
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text("text")  # Extract text from each page
    context_text=text 
    return text

# Load the QA pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def answer_question(question, context):
    result = qa_pipeline(question=question, context=context)
    return result['answer']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if uploaded_file:
        # ✅ Make sure uploads folder exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        pdf_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(pdf_path)

        reader = PyPDF2.PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

        return jsonify({'text': text})

    return jsonify({'error': 'Invalid file'}), 400


@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text')
    if text:
        # Process the input text before passing it to the model
        text = process_text(text)
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = summarizer(text, max_length=500, min_length=30, do_sample=False)
        return jsonify({'summary': summary[0]['summary_text']})
    return jsonify({'error': 'No text provided'}), 400

@app.route('/keywords', methods=['POST'])
def keywords():
    data = request.get_json()
    text = data.get('text')
    if text:
        text = process_text(text)
        doc = nlp(text)
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = X.toarray().flatten()
        keywords_with_scores = sorted(zip(scores, feature_names), reverse=True)

        # Only take the words
        words_only = [word for score, word in keywords_with_scores]

        return jsonify({'keywords': words_only})
    
    return jsonify({'error': 'No text provided'}), 400


@app.route('/definitions', methods=['POST'])
def definitions():
    data = request.get_json()
    word = data.get('word')

    if not word:
        return jsonify({'error': 'No word provided'}), 400

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    response = requests.get(url)
    if response.status_code == 200:
        definitions_data = response.json()
        definitions = [d['meanings'][0]['definitions'][0]['definition'] for d in definitions_data]
        return jsonify({'definitions': definitions})
    else:
        return jsonify({'error': 'Definition not found'}), 404

@app.route('/audio', methods=['POST'])
def audio():
    data = request.get_json()
    text = data.get('text')
    if text:
        tts = gTTS(text)
        audio_file = "static/generated_audio.mp3"
        tts.save(audio_file)
        return jsonify({'audio_url': audio_file})
    return jsonify({'error': 'No text provided'}), 400

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    if not context_text:
        return jsonify({'error': 'No context available yet. Upload text or PDF first.'}), 400
    result = qa_pipeline(question=question, context=context_text)
    answer = result['answer']
    return jsonify({'answer': answer})


if __name__ == '__main__':
    app.run(debug=True)
