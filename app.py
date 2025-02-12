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
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Jungian psychoanalyst. Analyze the dream using core Jungian concepts such as the collective unconscious, "
                            "archetypes (e.g., the Shadow, Anima/Animus, Self), and the process of individuation. Explain how the dream symbols "
                            "might reflect inner conflicts or personal transformation. Emphasize symbolic imagery and the potential for growth, "
                            "and remind the user that this is a creative interpretation, not a diagnosis."
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

            # 2) DALL·E Image Generation using the new images endpoint:
            # Build the base image prompt and the combined text parts
            base_image_prompt = (
                "Create a dream-like, surreal image that visually represents the inner journey of the dreamer. "
                "Incorporate symbolic elements such as dark, mysterious silhouettes (the Shadow), ethereal figures (Anima/Animus), "
                "and transformative motifs like labyrinths or mythic creatures to evoke the collective unconscious and individuation. "
                "Blend elements of the dream:\n\n"
            )
            middle_text = "\n\nwith the following interpretation:\n\n"
            combined_text = dream_text.strip() + middle_text + interpretation.strip()
            full_prompt = base_image_prompt + combined_text

            # Check prompt length (must be <= 1000 characters)
            if len(full_prompt) > 1000:
                # Determine allowed characters for combined text
                allowed = 1000 - len(base_image_prompt) - len(middle_text)
                # Divide allowed space equally between dream_text and interpretation
                half_allowed = allowed // 2
                truncated_dream = dream_text.strip()[:half_allowed] + "..."
                truncated_interpretation = interpretation.strip()[:half_allowed] + "..."
                combined_text = truncated_dream + middle_text + truncated_interpretation
                full_prompt = base_image_prompt + combined_text

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
