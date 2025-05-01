// Handle file upload (PDF or TXT)
function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();

        if (file.type === "application/pdf") {
            // Read the PDF content
            readPDF(file);
        } else if (file.type === "text/plain") {
            // Read the TXT file content
            reader.onload = function(e) {
                document.getElementById('inputText').value = e.target.result;
            };
            reader.readAsText(file);
        } else {
            alert("Unsupported file type! Please upload a .txt or .pdf file.");
        }
    }
}

// Read PDF content and display it in textarea
function readPDF(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const typedarray = new Uint8Array(e.target.result);

        pdfjsLib.getDocument(typedarray).promise.then(function(pdf) {
            let textContent = "";
            let pagesPromises = [];

            for (let i = 1; i <= pdf.numPages; i++) {
                pagesPromises.push(
                    pdf.getPage(i).then(function(page) {
                        return page.getTextContent().then(function(text) {
                            text.items.forEach(function(item) {
                                textContent += item.str + " ";
                            });
                        });
                    })
                );
            }

            Promise.all(pagesPromises).then(function() {
                document.getElementById('inputText').value = textContent;
            });
        });
    };
    reader.readAsArrayBuffer(file);
}

// Utility: Show and hide loading spinner
function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

// Utility: Get text input from textarea
function getInputText() {
    return document.getElementById('inputText').value.trim();
}

// Process Text - Summarize, Extract Keywords, Generate Definitions, etc.
async function processText() {
    const text = getInputText();
    if (!text) {
        alert("Please upload a file or enter text first!");
        return;
    }

    showLoading();
    
    const response = await fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    const data = await response.json();
    
    if (data.error) {
        alert(data.error);
    } else {
        // Display the processed results
        document.getElementById('summaryOutput').innerText = "Summary: " + data.summary;
        //document.getElementById('keywordsOutput').innerText = "Keywords: " + data.keywords.join(', ');
        document.getElementById('keywordsOutput').innerText = "Keywords: " + data.keywords.join(', ');

        document.getElementById('definitionsOutput').innerText = "Definitions:\n" + JSON.stringify(data.definitions, null, 2);
        document.getElementById('ttsOutput').innerText = "Audio generated!";
        document.getElementById('audioOutput').src = data.audio_url;
        document.getElementById('qaOutput').innerText = "AI Question: " + data.question;
    }

    hideLoading();
}

// Process PDF Upload and Extract Text (for use with '/upload_pdf')
async function processPDF() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        showLoading();
        
        const response = await fetch('/upload_pdf', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.text) {
            document.getElementById('inputText').value = data.text;
        } else {
            alert(data.error || "Error processing the PDF.");
        }
        
        hideLoading();
    } else {
        alert("Please upload a PDF file first.");
    }
}

// Generate TTS Audio from Text (if you want a separate button for TTS)
async function generateAudio() {
    const text = getInputText();
    if (!text) {
        alert("Please enter text to generate audio.");
        return;
    }

    showLoading();
    
    const response = await fetch('/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    const data = await response.json();
    
    if (data.audio_url) {
        document.getElementById('audioOutput').src = data.audio_url;
        document.getElementById('ttsOutput').innerText = "Audio generated!";
    } else {
        alert(data.error || "Error generating audio.");
    }
    
    hideLoading();
}

// Ask AI to generate a question based on the text
async function generateQuestion() {
    const text = getInputText();
    if (!text) {
        alert("Please enter text to generate a question.");
        return;
    }

    showLoading();
    
    const response = await fetch('/question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    const data = await response.json();
    
    if (data.question) {
        document.getElementById('qaOutput').innerText = "AI Question: " + data.question;
    } else {
        alert(data.error || "Error generating question.");
    }

    hideLoading();
}
