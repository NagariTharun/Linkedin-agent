import os
from groq import Groq

# Grab the Groq API key securely from GitHub Secrets
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing! Please add it to GitHub Secrets.")

client = Groq(api_key=api_key)

def generate_linkedin_post():
    prompt = (
        "Write a high-engagement, professional LinkedIn post about "
        "tech career growth, automation, or productivity tips. "
        "Include a strong hook, 3 short paragraphs of value, "
        "a call-to-action question at the end, and 4 professional hashtags."
    )

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    print("--- GENERATED LINKEDIN POST (VIA GROQ) ---")
    print(completion.choices[0].message.content)
    print("------------------------------------------")

if __name__ == "__main__":
    generate_linkedin_post()
