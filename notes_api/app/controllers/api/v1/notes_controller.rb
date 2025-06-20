class Api::V1::NotesController < ApplicationController
  before_action :set_note, only: [:show, :update, :destroy, :update_from_chat, :preview_changes]

  def index
    @notes = Note.all.order(created_at: :desc)
    render json: @notes
  end

  def show
    render json: @note
  end

  def create
    @note = Note.new(note_params)
    if @note.save
      render json: @note, status: :created
    else
      render json: { errors: @note.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def update
    if @note.update(note_params)
      render json: @note
    else
      render json: { errors: @note.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def destroy
    @note.destroy
    head :no_content
  end

  # ===== NEW METHODS FOR CHAT-TO-EDIT FUNCTIONALITY =====
  
  def find_by_description
    description = params[:description]
    
    if description.blank?
      render json: { error: "Description parameter is required" }, status: :bad_request
      return
    end
    
    # Use the helper method from ChatController logic
    # For now, implement basic search here
    notes = find_notes_by_description(description)
    
    render json: {
      query: description,
      matches: notes.map do |note|
        {
          id: note.id,
          title: note.title,
          content_snippet: note.content.truncate(200),
          similarity_score: calculate_basic_similarity(description.downcase, note.title.downcase),
          created_at: note.created_at,
          updated_at: note.updated_at
        }
      end
    }
  end
  
  def update_from_chat
    chat_session_id = params[:chat_session_id]
    new_title = params[:title] 
    new_content = params[:content]
    
    if chat_session_id.present?
      session = ChatSession.find_by(session_id: chat_session_id)
      if session&.target_note == @note
        # Update from chat session
        if @note.update(title: new_title || @note.title, content: new_content || @note.content)
          session.update(status: 'completed')
          render json: { 
            note: @note, 
            message: "Note updated successfully from chat session",
            session_id: chat_session_id
          }
        else
          render json: { errors: @note.errors.full_messages }, status: :unprocessable_entity
        end
      else
        render json: { error: "Invalid chat session for this note" }, status: :bad_request
      end
    else
      # Direct update (fallback)
      if @note.update(title: new_title || @note.title, content: new_content || @note.content)
        render json: { note: @note, message: "Note updated successfully" }
      else
        render json: { errors: @note.errors.full_messages }, status: :unprocessable_entity
      end
    end
  end
  
  def preview_changes
    chat_session_id = params[:chat_session_id]
    
    if chat_session_id.blank?
      render json: { error: "Chat session ID is required" }, status: :bad_request
      return
    end
    
    session = ChatSession.find_by(session_id: chat_session_id)
    
    if session.nil? || session.target_note != @note
      render json: { error: "Invalid chat session for this note" }, status: :bad_request
      return
    end
    
    render json: {
      original: {
        title: session.original_content ? @note.title : nil,
        content: session.original_content
      },
      proposed: {
        title: session.draft_title || @note.title,
        content: session.draft_content || @note.content
      },
      changes_summary: {
        title_changed: session.draft_title.present? && session.draft_title != @note.title,
        content_changed: session.draft_content.present? && session.draft_content != @note.content,
        has_changes: session.has_draft_changes?
      },
      session: {
        id: session.session_id,
        status: session.status,
        edit_instructions: session.edit_instructions
      }
    }
  end

  private

  def set_note
    @note = Note.find(params[:id])
    if @note.nil?
      render json: { error: "Note not found" }, status: :not_found
    end
  end

  def note_params
    params.require(:note).permit(:title, :content)
  end
  
  # Helper methods for new functionality
  def find_notes_by_description(description)
    return [] if description.blank?
    
    clean_description = description.strip.downcase
    
    # Search by title and content
    notes = Note.where(
      "LOWER(title) ILIKE ? OR LOWER(content) ILIKE ?", 
      "%#{clean_description}%", 
      "%#{clean_description}%"
    ).limit(10)
    
    # Sort by relevance (title matches first, then content matches)
    notes.sort_by do |note|
      title_score = calculate_basic_similarity(clean_description, note.title.downcase)
      content_score = calculate_basic_similarity(clean_description, note.content.downcase) * 0.5
      -(title_score + content_score) # Negative for descending sort
    end
  end
  
  def calculate_basic_similarity(str1, str2)
    return 0.0 if str1.blank? || str2.blank?
    return 1.0 if str1 == str2
    
    # Simple word overlap similarity
    words1 = str1.split
    words2 = str2.split
    
    return 0.0 if words1.empty? || words2.empty?
    
    common_words = words1 & words2
    total_words = [words1.length, words2.length].max
    
    common_words.length.to_f / total_words
  end
end
