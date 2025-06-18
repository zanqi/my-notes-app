class Note < ApplicationRecord
  has_one :note_embedding, dependent: :destroy
  
  validates :title, presence: true, length: { maximum: 255 }
  validates :content, presence: true
  
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
end 