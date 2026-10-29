import os
import requests
from groq import Groq

# 1. Grab keys from GitHub Secrets
groq_api_key = os.environ.get("GROQ_API_KEY")
buffer_api_key = os.environ.get("BUFFER_API_KEY")
profile_id = os.environ.get("BUFFER_PROFILE_ID")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing!")

# 2. Generate post using Groq
groq_client = Groq(api_key=groq_api_key)
prompt = (
    "Write a high-engagement, professional LinkedIn post about "
    "tech career growth, automation, or productivity tips. "
    "Include a strong hook, 3 short paragraphs of value, "
    "and 4 professional hashtags."
)

completion = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}],
)

post_content = completion.choices[0].message.content
print("--- GENERATED LINKEDIN POST ---")
print(post_content)
print("-------------------------------")

# 3. Send post to Buffer queue
if buffer_api_key and profile_id:
    url = "https://api.bufferapp.com/1/updates/create.json"
    payload = {
        "text": post_content,
        "profile_ids": [profile_id],
        "access_token": buffer_api_key,
        "sharing_mode": "queue"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Successfully pushed post to your Buffer LinkedIn queue!")
    else:
        print("Buffer API Error:", response.text)
else:
    print("Buffer keys not found, skipping auto-queue.")
