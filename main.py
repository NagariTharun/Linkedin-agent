import os
import requests
from groq import Groq

# 1. Initialize Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Generate the post using AI
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
print("--- GENERATED POST ---")
print(post_content)

# 3. Push the post automatically to your Buffer queue
BUFFER_API_KEY = os.environ.get("BUFFER_API_KEY")
PROFILE_ID = os.environ.get("BUFFER_PROFILE_ID") # Your LinkedIn profile ID in Buffer

url = "https://api.bufferapp.com/1/updates/create.json"
payload = {
    "text": post_content,
    "profile_ids": [PROFILE_ID],
    "access_token": BUFFER_API_KEY,
    "sharing_mode": "queue" # Automatically drops it into your posting schedule queue!
}

response = requests.post(url, data=payload)
if response.status_code == 200:
    print("Successfully scheduled post via Buffer!")
else:
    print("Failed to queue post:", response.text)
