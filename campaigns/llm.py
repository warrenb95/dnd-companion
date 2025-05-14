from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_session_summary(bullet_points, chapter_title=None):
    prompt = f"""
You are a professional Dungeons & Dragons campaign writer. Based on the following bullet point notes from a game session, 
generate a clean and engaging narrative summary of what happened in the session.

Chapter: {chapter_title or "Unknown"}

Notes:
{bullet_points}

Write in the past tense. Summarize character decisions, story events, and any notable NPCs or encounters. Make it useful for session prep.

Add a section at the bottom titled 'Next Session Prep' with notes for notes that DM can use to prepare the next session.

Keep all of the notes short and precise, there's no need to add extra fluff around the notes.

Thanks!
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

