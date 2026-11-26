import os
import random
import requests
from groq import Groq

# 1. Grab keys from GitHub Secrets
groq_api_key = os.environ.get("GROQ_API_KEY")
buffer_api_key = os.environ.get("BUFFER_API_KEY")
profile_id = os.environ.get("BUFFER_PROFILE_ID")

print(f"DEBUG -> Groq Key Present: {bool(groq_api_key)}")
print(f"DEBUG -> Buffer API Key Present: {bool(buffer_api_key)}")
print(f"DEBUG -> Buffer Profile ID Present: {bool(profile_id)}")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing!")

# 2. Pick a weekly ServiceNow / automation theme so posts stay fresh every week
weekly_themes = [
    "Flow Designer vs. legacy Workflows: when to use subflows, error handling, and clean action design in ServiceNow",
    "Server-side vs. Client-side scripting best practices: avoiding synchronous GlideRecord in Client Scripts and using GlideAjax + Script Includes cleanly",
    "UI Policies vs. Client Scripts: keeping forms fast, maintainable, and upgrade-safe in ServiceNow",
    "ITSM & NOC incident automation: reducing manual triage and MTTR using smart assignment rules, SLAs, and automated flows",
    "ServiceNow CSA to developer growth: practical lessons from building custom tables, views, and process flows on a PDI",
    "Combining ServiceNow integrations (REST/APIs) with modern automation and GenAI to eliminate repetitive ops tickets",
]

selected_theme = random.choice(weekly_themes)
print(f"DEBUG -> Selected Weekly Theme: {selected_theme}")

# 3. Generate post using Groq
groq_client = Groq(api_key=groq_api_key)
prompt = f"""
You are a hands-on ServiceNow Administrator & Developer sharing a practical weekly LinkedIn post.

Weekly Focus Topic: {selected_theme}

Write a high-engagement, authentic LinkedIn post with:
1. A sharp, relatable hook in the first 1-2 lines (no generic hype or clichés).
2. 3 concise, practical takeaways or real-world implementation tips that ServiceNow admins, developers, and IT ops engineers can immediately apply.
3. A brief closing reflection on automation or career growth in the ServiceNow ecosystem.
4. A specific question at the end to spark discussion in the comments.
5. Exactly 4 relevant hashtags: #ServiceNow #ServiceNowDev #Automation #ITSM

Keep formatting clean with short paragraphs and bullet points so it is easy to read on mobile. Avoid robotic filler phrases.
"""

completion = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}],
)

post_content = completion.choices[0].message.content
print("--- GENERATED WEEKLY LINKEDIN POST ---")
print(post_content)
print("--------------------------------------")

# 4. Send post to Buffer queue via official GraphQL API endpoint
if buffer_api_key and profile_id:
    url = "https://api.buffer.com"

    query = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post {
            id
            text
          }
        }
        ... on MutationError {
          message
        }
      }
    }
    """

    variables = {
        "input": {
            "text": post_content,
            "channelId": profile_id,
            "schedulingType": "automatic",
            "mode": "addToQueue",
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {buffer_api_key}",
    }

    response = requests.post(
        url, json={"query": query, "variables": variables}, headers=headers
    )
    print("Buffer Response Status:", response.status_code)
    print("Buffer Response Body:", response.text)

    res_data = response.json()
    if response.status_code == 200 and "errors" not in res_data:
        create_res = res_data.get("data", {}).get("createPost", {})
        if "message" in create_res:
            print("Buffer API Error Message:", create_res["message"])
        else:
            print("Successfully pushed weekly post to your Buffer LinkedIn queue!")
    else:
        print("Buffer API Error detected above.")
else:
    print("CRITICAL: Buffer keys are missing from GitHub Secrets.")
