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
end 