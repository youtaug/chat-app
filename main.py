import os
from flask import Flask, render_template, request, jsonify
import openai
import PyPDF2

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") or "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"

# Load PDF content (conversation log and manual) on startup
pdf_text = ""
pdf_path = os.path.join("data", "prompt_data.pdf")
try:
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text
except FileNotFoundError:
    print(f"PDF file not found at {pdf_path}. Starting without initial context.")
except Exception as e:
    print(f"Error reading PDF: {e}")

# Initialize conversation history with PDF content as system prompt
conversation_history = []
if pdf_text:
    conversation_history.append({"role": "system", "content": pdf_text})
else:
    conversation_history.append({"role": "system", "content": "You are a helpful assistant."})

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if user_message == "":
        return jsonify({"assistant": ""})
    # Add user message to conversation
    conversation_history.append({"role": "user", "content": user_message})
    assistant_message = ""
    # If API key is not set, return an error message
    if not openai.api_key or openai.api_key.startswith("YOUR_OPENAI_API_KEY"):
        assistant_message = "I'm sorry, I cannot answer because the OpenAI API key is not set."
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation_history
            )
            assistant_message = response.choices[0].message.content.strip()
        except Exception as e:
            assistant_message = f"(Error: {str(e)})"
    # Add assistant response to conversation
    conversation_history.append({"role": "assistant", "content": assistant_message})
    return jsonify({"assistant": assistant_message})

if __name__ == "__main__":
    app.run(debug=True)
