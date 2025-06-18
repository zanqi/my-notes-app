class Message < ApplicationRecord
  belongs_to :conversation
  
  validates :content, presence: true
  validates :role, presence: true, inclusion: { in: %w[user assistant system] }
  
  scope :by_role, ->(role) { where(role: role) }
  scope :user_messages, -> { where(role: 'user') }
  scope :assistant_messages, -> { where(role: 'assistant') }
  scope :system_messages, -> { where(role: 'system') }
  scope :recent, -> { order(created_at: :desc) }
  scope :chronological, -> { order(created_at: :asc) }
  
  def user_message?
    role == 'user'
  end
  
  def assistant_message?
    role == 'assistant'
  end
  
  def system_message?
    role == 'system'
  end
  
  def to_s
    "#{role.capitalize}: #{content.truncate(50)}"
  end
end
