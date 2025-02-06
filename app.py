from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Securely load your OpenAI API key

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    image_url = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "")

        try:
            # --- Chat Completion (GPT) ---
            # Note the new method path: openai.chat.completions.create
            chat_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": 
                     "You are a thorough assistant. Provide short, thoughtful answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=50
            )
            # Extract the text from the response
            result = chat_response.choices[0].message.content.strip()

            # --- Image Generation (DALL·E) ---
            # Use openai.images.create instead of openai.Image.create
            image_prompt = f"A hyperrealistic photograph inspired by: '{prompt}' and the response: '{result}'."

            image_response = openai.images.create(
                prompt=image_prompt,
                n=1,
                size="512x512"
            )
            image_url = image_response.data[0].url

        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template("index.html", result=result, image_url=image_url)

if __name__ == "__main__":
    # Debug=True is great for local testing but turn off in production
    app.run(debug=True)
