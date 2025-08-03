from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client only if API key is available
if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
else:
    client = None


def generate_session_summary(bullet_points, chapter_title=None):
    if not client:
        raise ValueError("OpenAI API key not configured")
        
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


def compress_session_notes(notes_content_list, encounter_title=None):
    """
    Compress multiple session notes into a single comprehensive note.
    
    Args:
        notes_content_list: List of note content strings
        encounter_title: Title of the encounter (optional)
    
    Returns:
        Compressed note content as a string
    """
    if not client:
        raise ValueError("OpenAI API key not configured")
        
    if not notes_content_list:
        return ""
    
    # Join all notes with clear separators
    all_notes = "\n\n--- Note Separator ---\n\n".join(notes_content_list)
    
    prompt = f"""
You are a professional Dungeons & Dragons campaign writer. You have been given multiple session notes from the same encounter that need to be compressed into a single, comprehensive note.

Encounter: {encounter_title or "Unknown"}

Multiple Session Notes:
{all_notes}

Please compress these notes into a single, well-organized note that:
1. Combines all the important information chronologically
2. Removes redundant information 
3. Maintains all key story beats, character decisions, and outcomes
4. Preserves important NPC interactions and dialogue
5. Keeps combat details and mechanical outcomes
6. Uses clear markdown formatting with bullet points and sections as appropriate

The compressed note should be comprehensive but concise, suitable for future reference during campaign preparation.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert at organizing and compressing D&D session notes while preserving all important information."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,  # Lower temperature for more consistent, factual output
        max_tokens=800,   # Allow more tokens for comprehensive compression
    )

    return response.choices[0].message.content.strip()