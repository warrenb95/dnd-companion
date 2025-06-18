# D&D Companion MVP — Developer Specification

---

## 1. Project Overview

A full-stack web application designed for Dungeon Masters (DMs) to replace handwritten and audio session notes with digital notes, enriched by AI-powered session summarization and insights.

**Core MVP Goals:**

- Replace handwritten/audio notes with typed and transcribed digital notes
- Provide AI summarization of session notes on demand
- Manage campaigns, sessions, notes, and uploads securely with user accounts
- Simple, desktop-first responsive UI with Tailwind CSS
- Use third-party APIs for transcription (OpenAI Whisper), OCR (Google Vision), and summarization (OpenAI GPT)

---

## 2. Architecture & Tech Stack

- **Backend Framework:** Django (Python)
  - Provides rapid development with built-in ORM, authentication, admin interface
- **Frontend:**
  - Tailwind CSS for styling (desktop-first, responsive-ready)
  - HTMX or AJAX for dynamic UI parts (live note input, preview toggling)
  - Markdown rendering client-side (e.g., Marked.js) for notes and summaries
- **Database:**
  - SQLite for development
  - PostgreSQL for production
- **Containerization:**
  - Docker & docker-compose for local dev and production deployment
- **Third-Party Integrations:**
  - OpenAI Whisper API for audio transcription
  - Google Cloud Vision API for OCR on handwritten images
  - OpenAI GPT API with custom prompts for AI summarization

---

## 3. Data Model & Relationships

| Model            | Key Fields & Notes                                                                                                                                | Relations                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **User**         | id, email, password (hashed), invite-only registration enforced                                                                                   | Owns campaigns             |
| **Campaign**     | id, user (owner), name (req), description (opt), system (opt), level_range (opt), cover_image (opt), tags                                         | Has many sessions          |
|                  | status (active/completed)                                                                                                                         |                            |
| **Chapter**      | id, chapter, name/title (req), description (opt), cover_image (opt), tags, status (active/completed)                                              | Has many notes, uploads    |
| **Encounter**    | id, chapter, name/title (req), description (opt), cover_image (opt), tags, status (active/completed)                                              | Has many notes, uploads    |
| **Note**         | id, encounter, text (Markdown), source_tag (`manual`/`audio`/`image`), created_at, updated_at                                                     | Linked to session          |
| **UploadedFile** | id, session, file_path/url, file_type (`audio`/`image`), size, status (`processing`, `complete`, `failed`), created_at, linked_note_id (nullable) | Linked to session and note |
| **AISummary**    | id, session, summary_text (Markdown), raw_prompt, raw_response, created_at                                                                        | Linked to session          |

---

## 4. Feature Requirements

### 4.1 User Authentication & Authorization

- Invite-only registration during development
- Email/password login with session management
- Users can only access their own campaigns, sessions, notes, uploads, and summaries

### 4.2 Campaign & Session Management

- Create, edit, delete campaigns & sessions
- Campaign/session metadata (name, description, system, level range, tags, cover images)
- Status management: mark campaigns/sessions as active or completed
- Lists grouped by status, visually distinguished in UI

### 4.3 Notes

- Full CRUD operations on notes
- Notes input supports Markdown with live toggle preview
- Notes tagged by source: manual, audio, image
- Display creation and updated timestamps on notes
- Notes ordered chronologically by creation date/time
- Live notepad style input allowing continuous note-taking without page reload

### 4.4 File Uploads (Audio & Image)

- Multiple files per session allowed
- Server-side validation:
  - Images max 5MB, types: `.jpg`, `.jpeg`, `.png`
  - Audio max 25MB, types: `.mp3`, `.wav`, `.m4a`
- Upload processing status tracked (`processing`, `complete`, `failed`) and displayed in UI
- Files temporarily stored (e.g., 7–30 days retention), then auto-deleted
- Each processed file generates a single new note with extracted text
- Event logging for upload and processing lifecycle

### 4.5 AI Summarization

- “Summarize Session” button triggers AI call
- Custom prompt tailored for D&D sessions to highlight key moments and character actions
- Summary stored and displayed read-only in dedicated section
- Raw prompt and response stored temporarily for debugging
- Summaries support Markdown formatting

### 4.6 UI & UX

- Tailwind CSS with desktop-first approach
- Simple navigation: campaign list → session list → session notes + AI summary
- Visual distinction and grouping of active/completed campaigns and sessions
- Onboarding messages for new users (e.g., “Create your first campaign”)
- Basic success/error UI feedback (toasts, alerts)
- Live Markdown preview toggle for notes
- Timestamps shown for notes
- Tag display as badges on campaigns, sessions, and notes
- Basic account settings page (email/password change)

---

## 5. Error Handling Strategy

- **Form Validation:**

  - Client-side (where feasible) and server-side validation for all inputs, especially uploads and text fields
  - Clear error messages returned and shown in UI

- **File Uploads:**

  - Reject files exceeding size limits or unsupported formats
  - Show processing errors with retry or delete options

- **Third-Party API Calls:**

  - Graceful handling of API failures (timeout, rate limit, etc.)
  - Inform user with clear UI messages
  - Implement retry policies with backoff if needed (for transcription and summarization)

- **Authentication:**

  - Secure password handling and session management
  - Protect endpoints so users access only their own data
  - Proper HTTP status codes for unauthorized/forbidden access

- **General:**
  - Logging of unexpected server errors for debugging
  - User-friendly fallback UI for failures (e.g., “Something went wrong, please try again”)

---

## 6. Testing Plan

### 6.1 Unit Tests

- Model validations and relations
- Form input validation
- View logic for CRUD endpoints (campaigns, sessions, notes, uploads)
- Permissions and access control
- API integration mocks for Whisper, Vision, and OpenAI GPT
- Utilities for Markdown rendering and file handling

### 6.2 Integration Tests (Stretch Goals)

- Full workflow tests: user registration/login → create campaign/session → add notes and uploads → trigger summarization → view summaries
- Authentication flow
- File upload and processing lifecycle
- UI feedback on success and error states

### 6.3 Test Environment Setup

- Use SQLite with an in-memory database for fast tests
- Mock external API calls to avoid costs and flakiness
- Use Django’s test client for HTTP requests and user session simulation

---

## 7. Deployment & DevOps

- Dockerized app with `Dockerfile` and `docker-compose.yml` for local development
- Environment variables to configure database, API keys, and debug settings
- Fly.io deployment leveraging containerization and PostgreSQL add-on
- Automated cleanup of temporary uploaded files via scheduled jobs or background tasks
- Logging and monitoring to track errors and performance (basic setup)

---

## 8. Additional Notes & Future Directions

- Extend notes with categories and filtering
- Add player characters with user roles and note contributions
- Implement soft deletes and versioning for notes
- Enhance AI interactions with richer prompt engineering and session building tools
- Add tagging filters and advanced search
- Integrate @mentions and cross-linking of campaign entities
- Build collaboration features for multiple DMs
- Implement richer media playback and annotation

---

_If you want me to help with anything else—like breaking this down into tickets or drafting API specs—just ask!_
