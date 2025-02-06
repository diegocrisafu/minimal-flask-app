from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Securely load API key

@app.route("/", methods=["GET", "POST"])
def index():
    interpretation = None
    image_url = None

    if request.method == "POST":
        # Get dream description from the user
        dream_text = request.form.get("dream_text", "")

        try:
            # --- GPT: Jungian Interpretation ---
            # We construct messages for ChatCompletion. 
            # System role sets the overall behavior & context. 
            # User role is the dream text input.
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a psychoanalyst well-versed in Carl Jung’s theories. "
                        "You provide dream interpretations that explore archetypes, the collective unconscious, "
                        "and symbolic meaning in a concise, thoughtful way. "
                        "You are not a mental health professional and cannot give medical advice. "
                        "Always remind the user that this is an interpretation, not a diagnosis."
                    )
                },
                {
                    "role": "user",
                    "content": f"Dream description: {dream_text}"
                },
            ]

            # Create a chat completion for the dream interpretation
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=messages,
                temperature=0.9
            )
            interpretation = response.choices[0].message.content.strip()

            # --- DALL·E: Image Generation ---
            # Use the dream text and the resulting interpretation
            # to guide the image prompt. Keep it succinct but descriptive.
            image_prompt = (
                f"Create a surreal, dream-like scene inspired by the following dream:\n"
                f"\"{dream_text}\"\n"
                f"and this Jungian interpretation:\n"
                f"\"{interpretation}\"\n"
                f"Focus on archetypal symbols and a mystical, introspective atmosphere."
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
