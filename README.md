# Smart-Reading-Support-System


## PDF/Text-Based Question Answering Web App

This is a web application that allows users to upload text or PDF documents, and then ask questions based on the uploaded content. The system uses a pre-trained machine learning model (`distilbert-base-cased-distilled-squad`) to extract answers from the given context.


### Features

- Upload plain text or PDF files.
- Automatically extract and process text content.
- Ask natural language questions based on uploaded content.
- Receive intelligent answers powered by Transformers QA model.


### Tech Stack

- **Backend**: Python, Flask, Hugging Face Transformers, PyMuPDF
- **Frontend**: HTML, JavaScript (Fetch API)
- **Model**: `distilbert-base-cased-distilled-squad`


### Requirements

Make sure Python 3.7+ is installed.

Install dependencies:

```bash
pip install flask transformers pymupdf
```


### How to Run the Project

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/pdf-qa-app.git
cd pdf-qa-app
```

2. **Run the Flask app**:

```bash
python app.py
```

By default, the app will run on `http://127.0.0.1:8000`.

3. **Open the App**:

In your browser, go to:

```
http://127.0.0.1:8000
```

4. **Usage Flow**:
   - Upload plain **text** using the textarea and upload button.
   - Or upload a **PDF file** using the file input.
   - Ask a **question** using the form.
   - View the **answer** below the form.


### Project Structure

```
smart-reading-support-system-app/
│
├── app.py              # Flask backend app
├── templates/
│   └── index.html      # Frontend interface
└── static/
|    └── styles.css       # css file
|____script.js
```


### Example Questions

If your uploaded content is a physics textbook page, you can ask:

- "What is Newton's first law?"
- "What does inertia mean?"

The app will return the best answer from the text.


### Future Enhancements

- Add support for multiple documents
- Add context memory or history
- Enhance UI with loading spinners and better feedback
- Deploy to Heroku or Render
