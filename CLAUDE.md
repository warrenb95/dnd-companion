# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based D&D Campaign Builder web application that helps Dungeon Masters plan, build, and manage campaigns with AI assistance. The application features campaign management, chapter/encounter building, character tracking, and LLM-powered session summarization.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
OPENAI_API_KEY=your-openai-api-key-here
```

### Database Management
```bash
# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser
```

### Development Server
```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test campaigns

# Run with verbose output
python manage.py test --verbosity=2
```

### Django Management
```bash
# Access Django shell
python manage.py shell

# Collect static files (if needed)
python manage.py collectstatic

# Check for common issues
python manage.py check
```

## Architecture Overview

### Core Models & Relationships

**Campaign** (Central entity)
- Owner: User (ForeignKey)
- Related: chapters, locations, npcs, characters, chat_messages

**Chapter** (Ordered campaign segments)
- Campaign: Campaign (ForeignKey)
- Order: PositiveIntegerField (for sequencing)
- Status: choices (not_started, in_progress, completed)
- Contains: encounters (related_name)

**Encounter** (Chapter components)
- Chapter: Chapter (ForeignKey)
- Type: choices (combat, social, puzzle, exploration, mixed)
- Order: PositiveIntegerField (for sequencing)
- Contains: session_notes (related_name)

**Supporting Models**
- **Location**: Campaign locations with region/tags
- **NPC**: Campaign characters with status tracking
- **CharacterSummary**: Player character details
- **SessionNote**: Encounter-based notes with LLM summaries
- **ChatMessage**: Campaign-level chat for AI interaction
- **ChapterChatMessage**: Chapter-specific chat for generation

### Authentication & Permissions

- User-based ownership for all major models
- Each model has `owner` ForeignKey to User
- Views use `LoginRequiredMixin` and filter by owner
- Users can only access their own campaigns/data

### LLM Integration

**File**: `campaigns/llm.py`
- OpenAI client initialized with API key from settings
- `generate_session_summary()` function for D&D session summarization
- Uses `gpt-3.5-turbo` model with custom prompts
- Configured for D&D-specific context and formatting

**Usage Pattern**:
```python
from .llm import generate_session_summary
summary = generate_session_summary(bullet_points, chapter_title)
```

## Key Features

### Campaign Management
- Full CRUD operations for campaigns, chapters, encounters
- Hierarchical structure: Campaign → Chapter → Encounter
- Ordered chapters and encounters with drag-and-drop capability
- Status tracking for campaign progress

### AI-Powered Features
- Session note summarization using OpenAI GPT
- Campaign and chapter chat for brainstorming
- Chapter generation based on confirmed chat messages
- Markdown rendering for AI-generated content

### User Experience
- Bootstrap-based responsive templates
- Markdown support throughout application
- Image upload for encounter maps
- Export campaigns to Markdown format

## Important Patterns

### Model Conventions
- All major models include `owner` field for user isolation
- Use `related_name` for reverse relationships
- `Meta` class with `ordering` for sequenced models
- Status choices defined as class constants

### View Structure
- Generic class-based views (ListView, DetailView, CreateView, UpdateView)
- LoginRequiredMixin for authentication
- Custom views for AI functionality and export features
- HTMX endpoints for dynamic UI updates

### Template Organization
```
templates/
├── base.html (main layout)
├── campaigns/ (campaign-specific templates)
├── chapters/ (chapter-specific templates)
├── characters/ (character management)
├── encounters/ (encounter components)
└── components/ (reusable template parts)
```

### URL Patterns
- Namespaced URLs with `app_name = "campaigns"`
- RESTful patterns for CRUD operations
- Nested URLs for hierarchical relationships (campaign/chapter/encounter)

## Development Notes

### Database Schema
- Uses SQLite for development (configured in settings.py)
- Migration files track schema evolution
- Models include helpful help_text for complex fields

### Static Files & Media
- Media files stored in `media/` directory
- Image uploads for encounter maps supported
- Static files served through Django's development server

### Environment Configuration
- Settings use `python-dotenv` for environment variables
- OpenAI API key loaded from .env file
- Debug mode enabled for development

### Dependencies
- Django 5.2 as core framework
- OpenAI library for LLM integration
- Markdown library for content rendering
- Pillow for image handling
- Widget tweaks for form styling

## Security Considerations

- User isolation enforced through ownership models
- Django's built-in CSRF protection enabled
- API keys stored in environment variables
- User authentication required for all main functionality

## Current Branch Context

The repository is currently on the `encounter-ordering` branch, suggesting active development on encounter sequencing functionality. Recent commits show work on object ownership for security and encounter ordering features.