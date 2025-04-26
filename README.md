# 🐉 D&D Campaign Builder

A Django-based web application to help Dungeon Masters plan, build, and manage Dungeons & Dragons campaigns—with the help of an LLM assistant.

## ✨ Features

- 🧠 **LLM-Powered Campaign and Chapter Chat**

  - Brainstorm ideas with an AI assistant
  - Confirm messages for generating structured chapter drafts

- 🗺️ **Campaign Management**

  - Track campaigns, chapters, NPCs, locations, and session notes
  - Auto-generate summaries and prep notes based on bullet points and context

- 🛠️ **Chapter Builder Workflow**

  - Plan a chapter through chat
  - Generate a draft with context from previous chapters and session notes
  - Confirm and save chapters to the campaign

- 📄 **Markdown Export**
  - Export your entire campaign as a `.md` file with chapters, NPCs, locations, and session notes

## 📦 Tech Stack

- Python 3.x
- Django 4.x
- SQLite (default)
- OpenAI API (`gpt-4o-mini`) need to add permissions for (`gpt-3.5-turbo`)
- Bootstrap (via Django templates)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/dnd-campaign-builder.git
cd dnd-campaign-builder
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your OpenAI API Key

Create a `.env` file or set an environment variable:

```
OPENAI_API_KEY=your-openai-api-key-here
```

Or add it in `settings.py` securely (not recommended for production).

### 5. Apply Migrations and Run

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Development Notes

- To use Markdown rendering in summaries:
  - Install markdown: `pip install markdown`
  - Use `{{ summary|markdown }}` in templates
- Customize LLM prompts in `llm.py`
- Control chapter/chat flow in `views.py`

---

## 📁 Project Structure

```
campaigns/
├── models.py       # Campaign, Chapter, NPC, Location, etc.
├── views.py        # Campaign & chat views
├── forms.py        # Form logic
├── templates/      # All app templates
├── llm.py          # OpenAI logic + prompt structure
```

---

## 📋 License

MIT — use it, hack it, roll a nat 20.

---

## 🧙‍♂️ Maintained By

Warren ([@warrenb95](https://github.com/warrenb95))  
Ideas, issues, or bugs? Open an issue or roll for initiative.
