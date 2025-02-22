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
            # 1) Jungian Dream Interpretation using GPT-4
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

            # 2) DALL·E Image Generation using the image prompt you like:
            image_prompt = (
                f"A highly detailed, realistic painting based on the user's dream:\n\n"
                f"Dream: \"{dream_text}\"\n\n"
                "Use the following interpretation only as minor inspiration if it aligns with the dream’s literal details:\n\n"
                f"{interpretation}\n\n"
                "Maintain a classical realism style with clear, vivid details that depict the dream's literal setting. "
                "Subtle Jungian motifs may be added only if they don't overshadow the scene."
            )

            # Ensure the image prompt is within the 1000-character limit:
            if len(image_prompt) > 1000:
                image_prompt = image_prompt[:997] + "..."

            image_response = openai.images.generate(
                prompt=image_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = image_response.data[0].url

        except Exception as e:
            interpretation = f"Error: {str(e)}"

    return render_template("index.html", interpretation=interpretation, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
