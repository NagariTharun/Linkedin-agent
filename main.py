import os
from google import genai

# Grab the Gemini API key securely from GitHub
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing! Please add it to GitHub Secrets.")

client = genai.Client(api_key=api_key)

def generate_linkedin_post():
    prompt = (
        "Write a high-engagement, professional LinkedIn post about "
        "tech career growth, automation, or productivity tips. "
        "Include a strong hook, 3 short paragraphs of value, "
        "a call-to-action question at the end, and 4 professional hashtags."
    )

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )

    print("--- GENERATED LINKEDIN POST ---")
    print(response.text)
    print("-------------------------------")

if __name__ == "__main__":
    generate_linkedin_post()
