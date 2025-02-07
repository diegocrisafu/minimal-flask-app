from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Securely load your OpenAI API key

@app.route("/", methods=["GET", "POST"])
def index():
    interpretation = None
    image_url = None

    if request.method == "POST":
        # Retrieve user input from the form
        dream_text = request.form.get("dream_text", "")

        try:
            # --- 1) Chat Completion (GPT) ---
            # Use openai.ChatCompletion.create(...) for chat-based interpretation.
            chat_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",   # or "gpt-4" if you have access
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a psychoanalyst well-versed in Carl Jung’s theories. "
                            "You provide dream interpretations that explore archetypes, the collective unconscious, "
                            "and symbolic meaning in a concise, thoughtful way. "
                            "You are not a mental health professional and cannot give medical advice. "
                            "Remind the user this is an interpretation, not a diagnosis."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Dream description: {dream_text}"
                    }
                ],
                temperature=0.9,
                max_tokens=300
            )

            interpretation = chat_response.choices[0].message.content.strip()

            # --- 2) Image Generation (DALL·E) ---
            # Switch from `openai.images.create(...)` to `openai.Image.create(...)`.
            # "Images" vs "Image" is often the cause of the 'no attribute create' error.
            image_prompt = (
                f"A surreal, dream-like scene inspired by the user's dream:\n"
                f"\"{dream_text}\"\n"
                f"And the following Jungian interpretation:\n"
                f"\"{interpretation}\"\n"
                f"Focus on symbolic archetypes and a mystical, introspective atmosphere."
            )

            image_response = openai.Image.create(
                prompt=image_prompt,
                n=1,
                size="512x512"
            )
            image_url = image_response["data"][0]["url"]

        except Exception as e:
            interpretation = f"Error: {str(e)}"

    return render_template("index.html", interpretation=interpretation, image_url=image_url)


if __name__ == "__main__":
    app.run(debug=True)
