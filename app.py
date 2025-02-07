from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in your .env

@app.route("/", methods=["GET", "POST"])
def index():
    interpretation = None
    image_url = None

    if request.method == "POST":
        # Grab the user's dream text from the form
        dream_text = request.form.get("dream_text", "")

        try:
            # 1) Jungian Dream Interpretation (via ChatCompletion)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Or "gpt-4" if your key has access
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a psychoanalyst well-versed in Carl Jung's theories. "
                            "Provide a concise, symbolic interpretation of the dream. "
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
            interpretation = response.choices[0].message.content.strip()

            # 2) DALL·E Image Generation (via openai.Image)
            # Prompt uses both dream_text and the generated interpretation
            image_prompt = (
                f"A surreal and mystical scene inspired by the following dream:\n\n"
                f"Dream: \"{dream_text}\"\n\n"
                f"Interpretation: \"{interpretation}\"\n\n"
                "Focus on Jungian archetypes, symbolism, and a contemplative mood."
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
    # Debug=True is useful for local development but disable it in production
    app.run(debug=True)
