class BulkSyncNotesJob < ApplicationJob
  queue_as :default

  def perform(force_resync: false)
    notes_to_sync = if force_resync
                     Note.all
                   else
                     Note.without_embeddings
                   end

    total_notes = notes_to_sync.count
    Rails.logger.info "Starting bulk sync for #{total_notes} notes (force_resync: #{force_resync})"

    notes_to_sync.find_each.with_index do |note, index|
      begin
        SyncNoteEmbeddingJob.perform_later(note.id)
        Rails.logger.debug "Queued sync job for note #{note.id} (#{index + 1}/#{total_notes})"
      rescue StandardError => e
        Rails.logger.error "Failed to queue sync job for note #{note.id}: #{e.message}"
      end
    end

    Rails.logger.info "Successfully queued #{total_notes} note sync jobs"
    
    # Optionally clean up old, unsynced embeddings
    cleanup_stale_embeddings if force_resync
  end

  private

  def cleanup_stale_embeddings
    # Remove embeddings that haven't been synced in over a week
    stale_count = NoteEmbedding.where('synced_at < ?', 1.week.ago).count
    NoteEmbedding.where('synced_at < ?', 1.week.ago).destroy_all
    
    Rails.logger.info "Cleaned up #{stale_count} stale embeddings"
  end
end 