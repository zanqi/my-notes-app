require 'net/http'
require 'uri'
require 'json'

class SyncNoteEmbeddingJob < ApplicationJob
  queue_as :default

  def perform(note_id)
    note = Note.find(note_id)
    
    # Create or update the note embedding record
    embedding = note.note_embedding || note.build_note_embedding
    embedding.embedding_id = generate_embedding_id(note)
    embedding.save!
    
    # Make HTTP request to LangChain service to sync the note
    sync_with_langchain_service(note, embedding)
    
    # Mark as synced
    embedding.mark_as_synced!
    
    Rails.logger.info "Successfully synced embedding for note #{note.id}"
  rescue StandardError => e
    Rails.logger.error "Failed to sync embedding for note #{note_id}: #{e.message}"
    raise e
  end

  private

  def generate_embedding_id(note)
    "note_#{note.id}_#{Time.current.to_i}"
  end

  def sync_with_langchain_service(note, embedding)
    # This will make HTTP request to our Python LangChain service
    uri = URI('http://localhost:8001/sync_note')
    
    payload = {
      note_id: note.id,
      title: note.title,
      content: note.content,
      embedding_id: embedding.embedding_id,
      created_at: note.created_at.iso8601,
      updated_at: note.updated_at.iso8601
    }

    response = Net::HTTP.post(uri, payload.to_json, {
      'Content-Type' => 'application/json',
      'Accept' => 'application/json'
    })
    
    # Check if the request was successful
    unless response.code.start_with?('2')
      raise "LangChain service returned error: #{response.code} - #{response.body}"
    end
    
    Rails.logger.debug "LangChain service response: #{response.code}"
    response
  end
end 