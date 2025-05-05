from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_session_summary(bullet_points, chapter_title=None):
    prompt = f"""
You are a professional Dungeons & Dragons campaign writer. Based on the following bullet point notes from a game session, generate a clean and engaging narrative summary of what happened in the session.

Chapter: {chapter_title or "Unknown"}

Notes:
{bullet_points}

Write in the past tense. Summarize character decisions, story events, and any notable NPCs or encounters. Make it useful for session prep.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Or gpt-4 if available
        messages=[
            {"role": "system", "content": "You summarize D&D game sessions."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def get_campaign_chat_response(campaign, messages):
    context = f"You are helping build a Dungeons & Dragons campaign called '{campaign.title}'. {campaign.description or ''}"
    history = [{"role": "system", "content": context}]

    for msg in messages:
        history.append({"role": msg.role, "content": msg.content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=history, temperature=0.8, max_tokens=600
    )

    return response.choices[0].message.content.strip()


def extract_locations_from_text(message_content):
    prompt = f"""
You are helping a D&D campaign builder extract structured data for in-world locations.

Return your answer as ONLY a JSON list of objects. Each object should contain:

- name (str)
- description (str)
- region (optional, str)
- tags (list of strings)

Here's the message to extract from:
\"\"\"
{message_content}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Extract location data from a D&D assistant message into structured JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=600,
    )

    return response.choices[0].message.content.strip()


def extract_multiple_npcs(message_content):
    prompt = f"""
You are helping a D&D campaign builder extract multiple non-player characters (NPCs) from a message.

Return your answer as ONLY a JSON list of objects. Each object should contain:

- name (str)
- role (str)
- description (str)
- tags (list of strings)
- location (optional, str)
- status (alive, dead, missing, unknown)

Here's the message:
\"\"\"
{message_content}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Extract multiple NPCs from a message into structured JSON list.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=800,
    )

    return response.choices[0].message.content.strip()


def generate_chapter_from_context(
    campaign, confirmed_messages, previous_chapters, recent_notes
):
    history_text = "\n\n".join(
        [f"{msg.role.capitalize()}: {msg.content}" for msg in confirmed_messages]
    )
    chapter_summaries = "\n".join(
        [f"Chapter {ch.order}: {ch.title} — {ch.summary}" for ch in previous_chapters]
    )

    prompt = f"""
You are helping a Dungeon Master write the next chapter of their D&D campaign.

### Campaign Summary
Title: {campaign.title}
User Description: {campaign.user_description}
Generated Summary: {campaign.generated_summary}


### Previous Chapters
{chapter_summaries or '_None yet_'}

### Confirmed Planning Conversation
{history_text}

### Session Notes (if applicable)
{recent_notes or '_No recent notes_'}

Based on the above, create the next chapter outline. Return your answer in this JSON structure:
{{
  "title": "string",
  "summary": "string",
  "prep_notes": "string",
  "suggested_npcs": [ "NPC Name 1", "NPC Name 2" ],
  "suggested_locations": [ "Location 1", "Location 2" ]
}}

Return only strict JSON. 
Use double quotes for all keys and strings. 
No trailing commas. No comments. No markdown formatting. No extra text.

Keep it concise but helpful for session planning.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a campaign co-writer for a D&D Dungeon Master.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=1000,
    )

    return response.choices[0].message.content.strip()


def get_chapter_chat_response(campaign, messages):
    history = [
        {
            "role": "system",
            "content": f"You are planning chapters for a D&D campaign called '{campaign.title}'.",
        }
    ]
    for msg in messages:
        history.append({"role": msg.role, "content": msg.content})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=history, temperature=0.7, max_tokens=600
    )
    return response.choices[0].message.content.strip()


def parse_text_with_llm(chapter_text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a D&D module assistant. Given the full text of a chapter, extract structured chapter and encounter data for use in a DM campaign app.",
            },
            {
                "role": "user",
                "content": f"Here is the chapter text:\n\n{chapter_text}\n\nPlease return structured JSON in this format: {CHAPTER_JSON_FORMAT}",
            },
        ],
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()


# --- Template for the LLM to follow ---
CHAPTER_JSON_FORMAT = """{
  "title": "",
  "level_range": "",
  "adventure_hook": "",
  "overview": "",
  "dm_guidance": "",
  "locations": [
    {
      "name": "",
      "read_aloud": "",
      "dm_notes": ""
    }
  ],
  "encounters": [
    {
      "title": "",
      "type": "",
      "level_range": "",
      "summary": "",
      "setup": "",
      "read_aloud": "",
      "tactics": "",
      "stat_blocks": "",
      "treasure": "",
      "map_reference": ""
    }
  ],
  "conclusion": ""
}"""
