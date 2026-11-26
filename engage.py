import os
import json
from groq import Groq

groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing!")

mode = os.environ.get("TASK_MODE", "connection").strip().lower()
person_name = os.environ.get("PERSON_NAME", "").strip()
input_text = os.environ.get("INPUT_TEXT", "").strip()
post_context = os.environ.get("POST_CONTEXT", "").strip()

if not input_text:
    raise ValueError("INPUT_TEXT is empty. Paste the profile headline/bio or comment text.")

client = Groq(api_key=groq_api_key)

if mode == "connection":
    prompt = f"""
You are a LinkedIn networking assistant for a ServiceNow Administrator & Developer.
Evaluate whether the person below has a ServiceNow background or works closely with the ServiceNow ecosystem (e.g., ServiceNow, ITSM, ITOM, CMDB, HRSD, CSM, CSA, CAD, Glide, Flow Designer, Now Platform, ServiceNow partner/recruiter/architect/consultant).

Person Name: {person_name or "Not provided"}
Profile Headline / Bio / Note: {input_text}

Return ONLY valid JSON with these exact keys:
{{
  "decision": "ACCEPT" or "SKIP",
  "reason": "1 short sentence explaining why",
  "greeting_message": "If ACCEPT, write a warm, concise, human initial LinkedIn message (under 300 characters) thanking them for connecting and saying you're happy to connect with fellow ServiceNow professionals. If SKIP, return an empty string."
}}
"""
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    result = json.loads(completion.choices[0].message.content)

    print("========================================")
    print(f"DECISION : {result.get('decision')}")
    print(f"REASON   : {result.get('reason')}")
    print("----------------------------------------")
    if result.get("decision") == "ACCEPT":
        print("COPY-PASTE GREETING MESSAGE:")
        print(result.get("greeting_message"))
    else:
        print("No greeting generated (not ServiceNow-related).")
    print("========================================")

elif mode == "comment":
    prompt = f"""
You are a helpful, approachable ServiceNow Developer and tech professional replying to a comment on your LinkedIn post.

Your Post Topic / Summary: {post_context or "ServiceNow, automation, and tech career growth"}
Commenter Name: {person_name or "Someone"}
Comment Text: {input_text}

Write a warm, authentic, concise reply (2-3 sentences max) that acknowledges their point, adds a quick practical insight if relevant, and keeps the conversation going naturally without sounding robotic or overusing hashtags.
"""
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    reply = completion.choices[0].message.content.strip()

    print("========================================")
    print("COPY-PASTE COMMENT REPLY:")
    print(reply)
    print("========================================")
else:
    raise ValueError(f"Unknown TASK_MODE: {mode}")
