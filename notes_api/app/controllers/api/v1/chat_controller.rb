require 'net/http'
require 'uri'

class Api::V1::ChatController < ApplicationController
  def sync_notes
    force_resync = params[:force_resync] == 'true'
    
    # Queue the bulk sync job
    job = BulkSyncNotesJob.perform_later(force_resync: force_resync)
    
    # Get counts for response
    total_notes = Note.count
    unsynced_notes = Note.without_embeddings.count
    
    render json: {
      message: "Bulk sync job queued successfully",
      job_id: job.job_id,
      total_notes: total_notes,
      unsynced_notes: unsynced_notes,
      force_resync: force_resync
    }
  end

  def sync_status
    total_notes = Note.count
    synced_notes = Note.with_embeddings.count
    unsynced_notes = Note.without_embeddings.count
    
    # Get recent sync jobs status
    recent_jobs = SolidQueue::Job.where(
      job_class_name: ['SyncNoteEmbeddingJob', 'BulkSyncNotesJob']
    ).order(created_at: :desc).limit(5)
    
    render json: {
      total_notes: total_notes,
      synced_notes: synced_notes,
      unsynced_notes: unsynced_notes,
      sync_percentage: total_notes > 0 ? (synced_notes.to_f / total_notes * 100).round(1) : 0,
      recent_jobs: recent_jobs.map do |job|
        {
          id: job.id,
          class_name: job.job_class_name,
          status: job.finished_at ? 'completed' : 'pending',
          created_at: job.created_at,
          finished_at: job.finished_at
        }
      end
    }
  end

  def health_check
    # Check if LangChain service is available
    langchain_status = check_langchain_service
    
    # Check database connectivity
    db_status = check_database_connection
    
    # Check job queue status
    queue_status = check_queue_status
    
    overall_status = [langchain_status, db_status, queue_status].all? ? 'healthy' : 'unhealthy'
    
    render json: {
      status: overall_status,
      services: {
        langchain: langchain_status ? 'up' : 'down',
        database: db_status ? 'up' : 'down',
        job_queue: queue_status ? 'up' : 'down'
      },
      timestamp: Time.current
    }
  end

  private

  def check_langchain_service
    uri = URI('http://localhost:8001/health')
    response = Net::HTTP.get_response(uri)
    response.code == '200'
  rescue
    false
  end

  def check_database_connection
    ActiveRecord::Base.connection.active?
  rescue
    false
  end

  def check_queue_status
    SolidQueue::Job.count >= 0
  rescue
    false
  end

  # ===== NEW HELPER METHODS FOR CHAT-TO-EDIT FUNCTIONALITY =====
  
  def find_note_by_description(description)
    return nil if description.blank?
    
    # Clean and normalize the description
    clean_description = description.strip.downcase
    
    # Try exact title match first
    note = Note.where("LOWER(title) = ?", clean_description).first
    return note if note
    
    # Try partial title match
    note = Note.where("LOWER(title) ILIKE ?", "%#{clean_description}%").first
    return note if note
    
    # Try content search
    note = Note.where("LOWER(content) ILIKE ?", "%#{clean_description}%").first
    return note if note
    
    # Try fuzzy matching on titles (more flexible)
    notes = Note.all.select do |n|
      title_similarity = calculate_similarity(clean_description, n.title.downcase)
      title_similarity > 0.6 # 60% similarity threshold
    end
    
    # Return the most similar note
    notes.max_by { |n| calculate_similarity(clean_description, n.title.downcase) }
  end
  
  def find_or_create_chat_session(conversation_id = nil, session_type = 'query')
    # Try to find existing active session for this conversation
    session = nil
    
    if conversation_id.present?
      session = ChatSession.active_sessions
                          .where(conversation_id: conversation_id)
                          .order(created_at: :desc)
                          .first
    end
    
    # Create new session if none found
    unless session
      session = ChatSession.create!(
        conversation_id: conversation_id,
        session_type: session_type,
        status: 'active'
      )
    end
    
    session
  end
  
  def detect_edit_intent(message)
    return false if message.blank?
    
    message_lower = message.strip.downcase
    
    # Conservative edit patterns - only obvious edit intents
    edit_patterns = [
      /^edit\s+my\s+note/,
      /^update\s+my\s+note/,
      /^change\s+my\s+note/,
      /^modify\s+my\s+note/,
      /edit\s+the\s+note\s+(about|on|titled)/,
      /update\s+the\s+note\s+(about|on|titled)/,
      /change\s+the\s+note\s+(about|on|titled)/,
      /modify\s+the\s+note\s+(about|on|titled)/
    ]
    
    edit_patterns.any? { |pattern| message_lower.match?(pattern) }
  end
  
  def extract_note_description(message)
    return nil if message.blank?
    
    message_lower = message.strip.downcase
    
    # Patterns to extract note descriptions
    patterns = [
      /edit\s+my\s+note\s+about\s+(.+)/,
      /update\s+my\s+note\s+about\s+(.+)/,
      /change\s+my\s+note\s+about\s+(.+)/,
      /modify\s+my\s+note\s+about\s+(.+)/,
      /edit\s+my\s+note\s+on\s+(.+)/,
      /update\s+my\s+note\s+on\s+(.+)/,
      /edit\s+my\s+(.+)\s+note/,
      /update\s+my\s+(.+)\s+note/,
      /edit\s+the\s+note\s+titled\s+(.+)/,
      /update\s+the\s+note\s+titled\s+(.+)/,
      /edit\s+the\s+note\s+about\s+(.+)/,
      /update\s+the\s+note\s+about\s+(.+)/
    ]
    
    patterns.each do |pattern|
      match = message_lower.match(pattern)
      return match[1].strip if match
    end
    
    nil
  end
  
  def calculate_similarity(str1, str2)
    return 0.0 if str1.blank? || str2.blank?
    return 1.0 if str1 == str2
    
    # Simple Levenshtein distance-based similarity
    # This is a basic implementation - in production you might want to use a gem
    require 'levenshtein'
    
    max_length = [str1.length, str2.length].max
    return 0.0 if max_length == 0
    
    distance = Levenshtein.distance(str1, str2)
    1.0 - (distance.to_f / max_length)
  rescue NameError
    # Fallback if levenshtein gem not available
    # Simple word overlap similarity
    words1 = str1.split
    words2 = str2.split
    
    return 0.0 if words1.empty? || words2.empty?
    
    common_words = words1 & words2
    total_words = [words1.length, words2.length].max
    
    common_words.length.to_f / total_words
  end
  
  def create_edit_session_for_note(note, conversation_id = nil, instructions = nil)
    return nil unless note
    
    session = ChatSession.create!(
      conversation_id: conversation_id,
      target_note: note,
      session_type: 'edit_note',
      status: 'editing',
      edit_instructions: instructions,
      original_content: note.content
    )
    
    session.save_original_content!
    session
  end
end 