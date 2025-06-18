class Conversation < ApplicationRecord
  has_many :messages, dependent: :destroy
  
  validates :title, presence: true, length: { maximum: 255 }
  
  scope :recent, -> { order(created_at: :desc) }
  scope :with_messages, -> { joins(:messages).distinct }
  
  def last_message
    messages.order(:created_at).last
  end
  
  def message_count
    messages.count
  end
  
  def user_messages
    messages.where(role: 'user')
  end
  
  def assistant_messages
    messages.where(role: 'assistant')
  end
  
  def to_s
    title.presence || "Conversation ##{id}"
  end
end
