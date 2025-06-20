// Select DOM elements
const messages = document.getElementById('messages');
const uploadInput = document.getElementById('upload-input');
const form = document.getElementById('file-upload-form');

// Function to append messages to the chat
function appendMessage(text, sender = 'user') {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('p-2', 'my-1', 'rounded', sender === 'user' ? 'bg-blue-100' : 'bg-green-100');
  msgDiv.textContent = sender === 'user' ? `You: ${text}` : `Bot: ${text}`;
  messages.appendChild(msgDiv);
  messages.scrollTop = messages.scrollHeight;
}

// Handle file uploads
form.addEventListener('submit', async (e) => {
  e.preventDefault(); // Prevent the default form submission

  const formData = new FormData(form);
  const file = uploadInput.files[0];

  if (file) {
    // Show the uploaded file message
    appendMessage(`📎 Uploading: ${file.name}`, 'user');

    try {
      const response = await fetch('/chattopdf/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
      });

      if (response.ok) {
        const result = await response.json();
        appendMessage(result.message || `PDF "${file.name}" uploaded successfully!`, 'bot');
        localStorage.setItem('uploadedPDF', file.name); // Save uploaded PDF info
      } else {
        appendMessage('Failed to upload the file. Please try again.', 'bot');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      appendMessage('An error occurred during file upload.', 'bot');
    }
  } else {
    appendMessage('Please select a file to upload.', 'bot');
  }
});

// Load default chat messages or instructions
window.addEventListener('load', () => {
  // Remove chat messages on reload
  messages.innerHTML = '';
  appendMessage('Upload a PDF to start chatting.', 'bot');

  // Persist uploaded PDF information
  const uploadedPDF = localStorage.getItem('uploadedPDF');
  if (uploadedPDF) {
    appendMessage(`Previously uploaded: ${uploadedPDF}`, 'bot');
  }
});
