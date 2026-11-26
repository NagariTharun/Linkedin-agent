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
tone = os.environ.get("GREETING_TONE", "peer").strip().lower()

if not input_text:
    raise ValueError("INPUT_TEXT is empty. Paste the profile headline/bio or comment text.")

client = Groq(api_key=groq_api_key)

TONE_GUIDES = {
    "peer": (
        "Warm, friendly, peer-to-peer developer/admin tone. Sound like a fellow hands-on ServiceNow builder "
        "who enjoys talking about Flow Designer, scripting, integrations, and platform craft—natural and never salesy."
    ),
    "recruiter": (
        "Polite, appreciative, and career-forward tone. Thank them for connecting and express enthusiasm "
        "about staying connected within the ServiceNow hiring and tech community."
    ),
    "formal": (
        "Polished, respectful, and executive tone suitable for senior architects, delivery heads, and practice leaders."
    ),
}

selected_tone_guide = TONE_GUIDES.get(tone, TONE_GUIDES["peer"])

if mode == "connection":
    prompt = f"""
You are a LinkedIn networking assistant for a ServiceNow Administrator & Developer with 3 years of hands-on platform experience.

Evaluate whether the person below belongs to the ServiceNow ecosystem.
ACCEPT if their headline, bio, or note matches ANY of these target categories:
1. Technical Builders: ServiceNow Developer, System Administrator, Technical Consultant, Solution/Platform Architect, Integration Specialist, Portal/UI Builder Developer, Scripting/Glide/Flow Designer Engineer.
2. Module & Operations Specialists: ITSM, ITOM, CMDB, Discovery, HRSD, CSM, SecOps, GRC/IRM, HAM/SAM, or ServiceNow Application/NOC Support Engineer.
3. Ecosystem & Hiring: ServiceNow Practice Lead, Engagement/Delivery Manager, ServiceNow Partner/Vendor Consultant, or Technical Recruiter hiring for ServiceNow roles.
4. Certified / Active Learners: Mentions CSA, CAD, CIS certifications, or building on ServiceNow PDI / Now Platform.

SKIP if they have zero connection to ServiceNow or enterprise IT service/workflow platforms (e.g., generic sales pitches, unrelated domains, crypto/marketing spam).

Person Name: {person_name or "Not provided"}
Profile Headline / Bio / Note: {input_text}

Greeting Tone Style: {selected_tone_guide}

Return ONLY valid JSON with these exact keys:
{{
  "decision": "ACCEPT" or "SKIP",
  "matched_role_category": "Technical Builder" | "Module/Ops Specialist" | "Ecosystem/Hiring" | "Certified/Learner" | "None",
  "reason": "1 short sentence explaining why",
  "greeting_message": "If ACCEPT, write a personalized, natural LinkedIn message (under 280 characters) using their first name if available, expressing that you're happy to connect with fellow ServiceNow professionals and referencing their specific focus area if mentioned. Never use clichés like 'I hope this message finds you well'. If SKIP, return an empty string."
}}
"""
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    result = json.loads(completion.choices[0].message.content)

    print("========================================")
    print(f"DECISION      : {result.get('decision')}")
    print(f"ROLE CATEGORY : {result.get('matched_role_category')}")
    print(f"TONE USED     : {tone}")
    print(f"REASON        : {result.get('reason')}")
    print("----------------------------------------")
    if result.get("decision") == "ACCEPT":
        print("COPY-PASTE GREETING MESSAGE:")
        print(result.get("greeting_message"))
    else:
        print("No greeting generated (not ServiceNow-related).")
    print("========================================")

elif mode == "comment":
    prompt = f"""
You are a hands-on ServiceNow Developer & Administrator replying to a comment on your LinkedIn post.

Your Post Topic / Summary: {post_context or "ServiceNow development, workflow automation, and tech career growth"}
Commenter Name: {person_name or "Someone"}
Comment Text: {input_text}
Reply Tone Style: {selected_tone_guide}

Write a warm, authentic, concise reply (2-3 sentences max) that acknowledges their point, adds a practical ServiceNow or automation insight if relevant, and keeps the conversation going naturally. Avoid robotic phrasing and hashtags.
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
