import os
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

# 2. Generate post using Groq (Balanced mix of Tech, Automation, & ServiceNow)
groq_client = Groq(api_key=groq_api_key)
prompt = (
    "Write a high-engagement, professional LinkedIn post that covers a balanced mix of "
    "tech career growth, automation, ServiceNow development, and emerging technologies (like GenAI, cloud, or DevOps). "
    "Include a strong hook, 3 short paragraphs of value, "
    "a call-to-action question at the end, and 4 relevant hashtags like #ServiceNow #TechTrends #Automation #CareerGrowth."
)

completion = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}],
)

post_content = completion.choices[0].message.content
print("--- GENERATED LINKEDIN POST ---")
print(post_content)
print("-------------------------------")

# 3. Send post to Buffer queue via official GraphQL API endpoint
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
            "mode": "addToQueue"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {buffer_api_key}"
    }
    
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    print("Buffer Response Status:", response.status_code)
    print("Buffer Response Body:", response.text)
    
    res_data = response.json()
    if response.status_code == 200 and "errors" not in res_data:
        create_res = res_data.get("data", {}).get("createPost", {})
        if "message" in create_res:
            print("Buffer API Error Message:", create_res["message"])
        else:
            print("Successfully pushed post to your Buffer LinkedIn queue!")
    else:
        print("Buffer API Error detected above.")
else:
    print("CRITICAL: Buffer keys are missing from GitHub Secrets.")
