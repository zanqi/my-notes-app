class Note < ApplicationRecord
  has_one :note_embedding, dependent: :destroy
  
  validates :title, presence: true, length: { maximum: 255 }
  validates :content, presence: true
  
  # Callbacks to trigger embedding sync
  after_create :queue_embedding_sync
  after_update :queue_embedding_sync_if_content_changed
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_title, ->(title) { where("title ILIKE ?", "%#{title}%") }
  scope :with_embeddings, -> { joins(:note_embedding) }
  scope :without_embeddings, -> { left_joins(:note_embedding).where(note_embeddings: { id: nil }) }
  
  def has_embedding?
    note_embedding.present?
  end
  
  def embedding_synced?
    has_embedding? && note_embedding.synced?
  end
  
  private
  
  def queue_embedding_sync
    SyncNoteEmbeddingJob.perform_later(id)
  end
  
  def queue_embedding_sync_if_content_changed
    if saved_change_to_title? || saved_change_to_content?
      SyncNoteEmbeddingJob.perform_later(id)
    end
  end
end 