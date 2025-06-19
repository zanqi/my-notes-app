### Project Overview
Goal: Create a simple proof-of-concept where users can create notes by saying "Create a note about [topic]" in the chat interface.

Architecture:
- Keep existing chat system as foundation
- Add basic intent detection in LangChain service
- Extend existing note creation flow
- Minimal UI changes to show the feature

# Chat-to-Edit Notes Feature - 1 Day Implementation Plan

## 🏗️ Phase 1: Rails Backend Updates (2 hours)

**Step 1.1: Add Chat Session Model**
- Create `ChatSession` model to track edit sessions
- Add fields: `session_id`, `target_note_id`, `draft_content`, `status`
- Create migration: `rails g migration CreateChatSessions`

**Step 1.2: Add Note Edit Endpoints**
- Add `start_edit_session` method to NotesController
- Add `update_from_chat` method to apply chat-generated changes
- Add `preview_changes` method to show diff before applying

**Step 1.3: Extend Chat Controller**
- Add `edit_note` action to handle note editing requests
- Add session management for tracking edit context
- Include note validation and error handling

**Step 1.4: Update Routes**
- Add `post :start_edit_session` to notes member routes
- Add `patch :update_from_chat` to notes member routes
- Add `get :preview_changes` to notes member routes

**Step 1.5: Add Required Gems**
- Add `diff-lcs` gem for content diffing
- Add `sanitize` gem for content cleaning
- Run `bundle install` to install dependencies

## 🤖 Phase 2: LangChain Service (3 hours)

**Step 2.1: Add Edit Intent Detection**
- Extend `rag_service.py` with `_detect_edit_intent()` method
- Add patterns for "edit my note", "update the note", "change this note"
- Include note identification from user message

**Step 2.2: Add Note Context Loading**
- Create `_load_note_context(note_id)` method
- Fetch current note content from Rails API
- Format note content for LLM context

**Step 2.3: Create Edit Generation Service**
- Add `_generate_note_edits(current_content, edit_instructions)` method
- Create specialized prompts for different edit types (append, rewrite, restructure)
- Include diff generation and change explanation

**Step 2.4: Add Edit Endpoints**
- Create `/start_note_edit` endpoint to begin edit session
- Create `/generate_edit` endpoint to process edit instructions
- Create `/apply_edit` endpoint to finalize changes

**Step 2.5: Add Edit Response Models**
- Create `EditRequest` and `EditResponse` Pydantic models
- Include `original_content`, `updated_content`, `changes_summary`
- Add validation for edit operations and note IDs

## 💻 Phase 3: Frontend Integration (2-3 hours)

**Step 3.1: Update API Client**
- Add `startNoteEdit(noteId)` method to api.ts
- Add `generateNoteEdit(sessionId, instructions)` method
- Add `applyNoteEdit(sessionId, updatedContent)` method
- Add TypeScript interfaces for edit requests/responses

**Step 3.2: Create Edit Components**
- Create `NoteEditModal.tsx` with before/after content view
- Create `EditInstructions.tsx` component for chat-style input
- Create `ChangesDiff.tsx` component to highlight modifications
- Add `EditConfirmation.tsx` for final approval step

**Step 3.3: Create Edit Chat Interface**
- Create `useNoteEdit.ts` hook for edit session management
- Add edit mode to existing chat interface
- Include note selection dropdown for edit target
- Add real-time preview of suggested changes

**Step 3.4: Update Note List Interface**
- Add "Edit with Chat" button to note cards
- Add edit session status indicators
- Include quick access to recent edit sessions
- Update navigation to show edit mode

## 🚀 Phase 4: Launch & Test (1 hour)

**Step 4.1: Start All Services**
```bash
# Terminal 1: Rails API
cd notes_api && rails server -p 3001

# Terminal 2: LangChain Service
cd langchain_service && python main.py

# Terminal 3: Frontend
cd notes_frontend && npm run dev
```

**Step 4.2: Initial Setup**
- **Add OpenAI API Key**: Update `langchain_service/.env` with your OpenAI API key
- **Create test notes**: Add 3-4 sample notes with different content types
- **Sync notes**: Ensure notes are synced to vector store for context
- **Test edit flow**: 
  - Select a note to edit
  - Open chat edit interface
  - Try basic edit instruction

**Step 4.3: Test Scenarios**
Try these edit interactions:
- **Simple append**: "Add a section about best practices to my React notes"
- **Content restructure**: "Reorganize my meeting notes by priority"
- **Tone change**: "Make my project notes more formal"
- **Add examples**: "Add code examples to my JavaScript notes"
- **Fix formatting**: "Clean up the formatting in my recipe note"
- **Expand section**: "Expand the introduction in my blog post draft"

**Step 4.4: Validation Tests**
- Verify original note content is preserved during editing
- Confirm changes are clearly highlighted in diff view
- Test cancel/abort functionality to discard changes
- Ensure edit history is maintained for rollback capability


### User Experience Workflow
Create Note Workflow:
1. User types: "Create a note about machine learning algorithms"
2. System detects intent: create_note
3. System asks clarifying questions if needed
4. System generates structured note from conversation
5. User previews and confirms/edits note
6. Note is saved and synced to vector store

Edit Note Workflow:
1. User selects note to edit or types: "Edit my note about React hooks"
2. System loads note context
3. User provides editing instructions: "Add a section about useCallback"
4. System generates updated note content
5. User previews changes and confirms
6. Note is updated and re-synced

Append Note Workflow:
1. User references existing note: "Add this to my JavaScript notes"
2. System identifies target note
3. System generates additional content
4. User previews appended content
5. Content is added to existing note


