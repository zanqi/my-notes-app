class Note < ApplicationRecord
  validates :title, presence: true, length: { maximum: 255 }
  validates :content, presence: true
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_title, ->(title) { where("title ILIKE ?", "%#{title}%") }
end 