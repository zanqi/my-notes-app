class Api::V1::ChatSessionsController < ApplicationController
  before_action :set_chat_session, only: [:show, :update, :destroy, :start_edit, :process_edit, :apply_changes, :cancel_edit]

  def create
    session_type = params[:session_type] || 'query'
    conversation_id = params[:conversation_id]
    
    @chat_session = ChatSession.new(
      session_type: session_type,
      conversation_id: conversation_id,
      status: 'active'
    )
    
    if @chat_session.save
      render json: {
        session: session_response(@chat_session),
        message: "Chat session created successfully"
      }, status: :created
    else
      render json: { errors: @chat_session.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def show
    render json: {
      session: session_response(@chat_session),
      target_note: @chat_session.target_note ? note_summary(@chat_session.target_note) : nil
    }
  end

  def update
    if @chat_session.update(session_params)
      render json: {
        session: session_response(@chat_session),
        message: "Chat session updated successfully"
      }
    else
      render json: { errors: @chat_session.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def destroy
    @chat_session.destroy
    render json: { message: "Chat session deleted successfully" }
  end

  # ===== EDIT SESSION SPECIFIC METHODS =====

  def start_edit
    note_id = params[:note_id]
    edit_instructions = params[:instructions]
    
    if note_id.blank?
      render json: { error: "Note ID is required" }, status: :bad_request
      return
    end
    
    note = Note.find_by(id: note_id)
    if note.nil?
      render json: { error: "Note not found" }, status: :not_found
      return
    end
    
    # Update session to edit mode
    @chat_session.update!(
      target_note: note,
      session_type: 'edit_note',
      status: 'editing',
      edit_instructions: edit_instructions,
      original_content: note.content
    )
    
    render json: {
      session: session_response(@chat_session),
      target_note: note_summary(note),
      message: "Edit session started for note: #{note.title}"
    }
  end

  def process_edit
    edit_instructions = params[:instructions]
    proposed_title = params[:proposed_title]
    proposed_content = params[:proposed_content]
    
    if edit_instructions.blank? && proposed_title.blank? && proposed_content.blank?
      render json: { error: "Edit instructions or proposed changes are required" }, status: :bad_request
      return
    end
    
    # Update the session with edit data
    update_data = {
      edit_instructions: [
        @chat_session.edit_instructions,
        edit_instructions
      ].compact.join("\n\n"),
      status: 'pending_approval'
    }
    
    update_data[:draft_title] = proposed_title if proposed_title.present?
    update_data[:draft_content] = proposed_content if proposed_content.present?
    
    if @chat_session.update(update_data)
      render json: {
        session: session_response(@chat_session),
        preview: {
          original: {
            title: @chat_session.target_note&.title,
            content: @chat_session.original_content
          },
          proposed: {
            title: @chat_session.draft_title || @chat_session.target_note&.title,
            content: @chat_session.draft_content || @chat_session.target_note&.content
          }
        },
        message: "Edit processed. Review and apply changes."
      }
    else
      render json: { errors: @chat_session.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def apply_changes
    unless @chat_session.editing_note? && @chat_session.target_note
      render json: { error: "No note editing session active" }, status: :bad_request
      return
    end
    
    if @chat_session.apply_changes!
      render json: {
        session: session_response(@chat_session),
        updated_note: note_summary(@chat_session.target_note.reload),
        message: "Changes applied successfully to note: #{@chat_session.target_note.title}"
      }
    else
      render json: { error: "Failed to apply changes" }, status: :internal_server_error
    end
  end

  def cancel_edit
    @chat_session.cancel!
    
    render json: {
      session: session_response(@chat_session),
      message: "Edit session cancelled"
    }
  end

  private

  def set_chat_session
    session_id = params[:id]
    @chat_session = ChatSession.find_by(session_id: session_id)
    
    if @chat_session.nil?
      render json: { error: "Chat session not found" }, status: :not_found
    end
  end

  def session_params
    params.permit(:session_type, :status, :conversation_id, :edit_instructions, :draft_title, :draft_content)
  end
  
  def session_response(session)
    {
      id: session.session_id,
      session_type: session.session_type,
      status: session.status,
      conversation_id: session.conversation_id,
      target_note_id: session.target_note_id,
      has_draft_changes: session.has_draft_changes?,
      started_at: session.started_at,
      completed_at: session.completed_at,
      duration: session.duration&.round(2),
      edit_instructions: session.edit_instructions,
      created_at: session.created_at,
      updated_at: session.updated_at
    }
  end
  
  def note_summary(note)
    {
      id: note.id,
      title: note.title,
      content_snippet: note.content.truncate(200),
      created_at: note.created_at,
      updated_at: note.updated_at
    }
  end
end 