class NoteEmbedding < ApplicationRecord
  belongs_to :note
  
  validates :embedding_id, presence: true, uniqueness: { scope: :note_id }
  validates :note_id, presence: true
  
  scope :synced, -> { where.not(synced_at: nil) }
  scope :unsynced, -> { where(synced_at: nil) }
  scope :recently_synced, -> { where('synced_at > ?', 1.hour.ago) }
  scope :needs_sync, -> { where('synced_at IS NULL OR synced_at < ?', 1.day.ago) }
  
  def synced?
    synced_at.present?
  end
  
  def needs_sync?
    synced_at.blank? || synced_at < 1.day.ago
  end
  
  def mark_as_synced!
    update!(synced_at: Time.current)
  end
  
  def sync_age
    return nil unless synced?
    Time.current - synced_at
  end
  
  def to_s
    "Embedding for Note ##{note_id} (#{embedding_id})"
  end
end
