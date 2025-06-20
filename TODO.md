# D&D Companion MVP — Development To-Do List

---

## Phase 1: Project Setup & Foundations

- [x] Initialize Git repository and remote origin
- [x] Create Django project and core app (e.g., `campaigns`)
- [x] Setup Python virtual environment and dependencies
- [ ] Configure Docker and docker-compose with Django and PostgreSQL (for prod)
  - [x] dev
  - [ ] prod
- [x] Setup basic Django settings (environment variables, secret keys, allowed hosts)
- [ ] Setup database connections for dev (SQLite) and prod (PostgreSQL)
  - [x] dev
  - [ ] prod
- [ ] Add Tailwind CSS to the frontend build pipeline (via Django-Tailwind or PostCSS)
  - [x] campaigns
  - [x] chapters
  - [ ] characters
  - [ ] encounters
  - [ ] locations
  - [ ] npcs
- [x] Setup basic URL routing and home page placeholder
- [x] Add basic user model with invite-only registration flow (disable public signup)
- [x] Implement authentication (login/logout) with Django’s built-in views

---

## Phase 2: Core Models & Admin

- [ ] Define models: User, Campaign, Session, Note, UploadedFile, AISummary
- [ ] Create and apply initial migrations
- [ ] Register models with Django admin for data management
- [ ] Implement invite-only user creation in admin panel
- [ ] Add model fields for metadata (tags, statuses, timestamps, cover images)
- [ ] Implement file storage backend for uploaded files (local for dev)
- [x] Add basic permissions so users only access their own campaigns/sessions

---

## Phase 3: Campaign & Session CRUD

- [ ] Build campaign list and detail views with Tailwind styling
- [ ] Implement campaign create/edit/delete forms (with validations)
- [ ] Add campaign cover image upload and display
- [ ] Implement session list view within campaigns, grouped by status
- [ ] Add session create/edit/delete with metadata and cover images
- [ ] Implement “mark as complete” toggle for campaigns and sessions
- [ ] Add tagging UI and backend logic with max 10 tags limit

---

## Phase 4: Notes CRUD and Live Notepad

- [ ] Implement note list view within session encounters, ordered by creation date
- [ ] Build note create/edit/delete views with Markdown text area
- [ ] Add live Markdown preview toggle using client-side rendering (e.g., Marked.js)
- [ ] Implement live notepad style input allowing continuous note-taking
- [ ] Display created and updated timestamps on each note
- [ ] Show source tags (manual/audio/image) on notes
- [ ] Ensure real-time note list updates after submissions (via HTMX/AJAX)

---

## Phase 5: File Upload & Processing Integration

- [ ] Add multiple audio/image file upload forms within sessions
- [ ] Validate file size and types on server (and client if possible)
- [ ] Store uploaded files temporarily with retention policy
- [ ] Implement status tracking for upload processing (processing, complete, failed)
- [ ] Integrate OpenAI Whisper API for audio transcription (mock in dev)
- [ ] Integrate Google Vision API for OCR on images (mock in dev)
- [ ] On processing completion, create single note with extracted text and tag source
- [ ] Display upload processing status and allow retry/delete on failure
- [ ] Log all upload and processing events in DB

---

## Phase 6: AI Summarization Feature

- [ ] Add “Summarize Session” button on session pages
- [ ] Integrate OpenAI GPT with custom prompt tailored to D&D sessions (mock in dev)
- [ ] Send all session notes to AI for summarization on demand
- [ ] Store AI summary and raw prompt/response temporarily in DB
- [ ] Display read-only AI summary in dedicated section with Markdown rendering
- [ ] Show UI feedback during summarization process and on errors

---

## Phase 7: UI/UX Improvements & Onboarding

- [ ] Implement onboarding messages for new users and empty states
- [ ] Add visual distinction between active and completed campaigns/sessions
- [ ] Display tags as badges on campaigns, sessions, and notes
- [ ] Add basic account settings page for email/password changes
- [ ] Implement UI notifications for success/error messages (toasts/alerts)
- [ ] Ensure desktop-first responsive layout with Tailwind

---

## Phase 8: Testing & Quality Assurance

- [ ] Write unit tests for models and validations
- [ ] Write unit tests for views and forms (including permission checks)
- [ ] Mock external API calls for Whisper, Vision, and OpenAI GPT
- [ ] Write integration tests for main user workflows (registration, CRUD, uploads, summaries)
- [ ] Setup CI pipeline to run tests on commits/pull requests

---

## Phase 9: Deployment & Maintenance

- [ ] Prepare production settings and secrets management
- [ ] Deploy to Fly.io with Docker container and PostgreSQL addon
- [ ] Setup automated cleanup for temporary files
- [ ] Implement basic logging and monitoring for errors and performance
- [ ] Document environment setup, deployment, and development workflow

---

# Optional/Future Enhancements (Not MVP)

- Add player character roles and note sharing
- Implement soft delete and note versioning
- Add note categories and advanced filtering/search
- Enable @mentions and linking between campaign entities
- Build multi-DM collaboration features
- Enhance AI capabilities with campaign-building conversational LLM
- Add richer media playback and annotation support
- Implement analytics dashboards

---

# Notes

- Break features into smaller sub-tasks when executing each phase
- Prioritize manual testing early, automate tests progressively
- Mock external services in development to avoid usage costs
- Use Django admin extensively for quick data inspection and debugging
- Maintain security best practices, especially around authentication and file handling

---

This checklist is designed to be iterative and incremental, enabling safe, test-driven progress while delivering functional features throughout development.

---

_Ready to start coding? Feel free to ask for help generating detailed task breakdowns, API specs, or frontend component outlines!_
