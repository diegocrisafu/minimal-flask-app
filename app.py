from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is set in .env

@app.route("/", methods=["GET", "POST"])
def index():
    interpretation = None
    image_url = None

    if request.method == "POST":
        # Grab the user's dream text from the form
        dream_text = request.form.get("dream_text", "")

        try:
            # 1) Jungian Dream Interpretation using the new chat completions endpoint:
            chat_response = openai.chat.completions.create(
                model="gpt-4",  
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Jungian psychoanalyst. Analyze the dream using core Jungian concepts such as the collective unconscious, "
                            "archetypes (the Shadow, Anima/Animus, Self, and the ego), and the process of individuation. Explain how the dream symbols "
                            "connect to inner conflicts and potential for personal growth. Emphasize symbolic imagery and remind the user that this is a creative interpretation, not a diagnosis."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Dream description: {dream_text}"
                    }
                ],
                temperature=0.9,
                max_tokens=200
            )
            interpretation = chat_response.choices[0].message.content.strip()

            # 2) DALL·E Image Generation using the new images endpoint:
            base_image_prompt = (
                "Create a surreal, dream-like image that represents the literal elements of the dream. "
                "Focus primarily on the scene described rather than excessive symbolic details. "
                "For example, if the dream involves a person drowning and then waking up in bed, emphasize those elements clearly."
            )
            middle_text = "\n\nDream: "
            combined_text = dream_text.strip()  # Using just the user's dream for the image prompt
            full_prompt = base_image_prompt + middle_text + combined_text

            # Check prompt length (must be <= 1000 characters)
            if len(full_prompt) > 1000:
                # Truncate the combined text so that full_prompt fits within 1000 characters
                allowed_chars = 1000 - len(base_image_prompt) - len(middle_text)
                truncated_combined_text = combined_text[:allowed_chars - 3] + "..."
                full_prompt = base_image_prompt + middle_text + truncated_combined_text

            image_response = openai.images.generate(
                prompt=full_prompt,
                n=1,
                size="512x512"
            )
            image_url = image_response.data[0].url

        except Exception as e:
            interpretation = f"Error: {str(e)}"

    return render_template("index.html", interpretation=interpretation, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
