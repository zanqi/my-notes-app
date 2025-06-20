class ChatSession < ApplicationRecord
  belongs_to :conversation, optional: true
  belongs_to :target_note, class_name: 'Note', optional: true
  
  validates :session_id, presence: true, uniqueness: true
  validates :session_type, inclusion: { in: %w[query create_note edit_note append_note] }
  validates :status, inclusion: { in: %w[active editing pending_approval completed cancelled] }
  
  enum session_type: {
    query: 'query',
    create_note: 'create_note',
    edit_note: 'edit_note',
    append_note: 'append_note'
  }
  
  enum status: {
    active: 'active',
    editing: 'editing',
    pending_approval: 'pending_approval',
    completed: 'completed',
    cancelled: 'cancelled'
  }
  
  scope :recent, -> { order(created_at: :desc) }
  scope :active_sessions, -> { where(status: ['active', 'editing', 'pending_approval']) }
  scope :for_note, ->(note_id) { where(target_note_id: note_id) }
  scope :edit_sessions, -> { where(session_type: ['edit_note', 'append_note']) }
  
  before_create :set_session_id, :set_started_at
  before_update :set_completed_at_if_finished
  
  def editing_note?
    edit_note? || append_note?
  end
  
  def has_draft_changes?
    draft_content.present? || draft_title.present?
  end
  
  def content_changed?
    return false unless target_note && original_content.present?
    target_note.content != original_content
  end
  
  def title_changed?
    return false unless target_note && draft_title.present?
    target_note.title != draft_title
  end
  
  def duration
    return nil unless started_at
    end_time = completed_at || Time.current
    end_time - started_at
  end
  
  def save_original_content!
    if target_note && original_content.blank?
      update!(original_content: target_note.content)
    end
  end
  
  def apply_changes!
    return false unless target_note && has_draft_changes?
    
    target_note.update!(
      title: draft_title.presence || target_note.title,
      content: draft_content.presence || target_note.content
    )
    
    update!(status: 'completed')
    true
  rescue => e
    Rails.logger.error "Failed to apply chat session changes: #{e.message}"
    false
  end
  
  def cancel!
    update!(status: 'cancelled')
  end
  
  private
  
  def set_session_id
    self.session_id ||= SecureRandom.uuid
  end
  
  def set_started_at
    self.started_at ||= Time.current
  end
  
  def set_completed_at_if_finished
    if status_changed? && (completed? || cancelled?)
      self.completed_at = Time.current
    end
  end
end 