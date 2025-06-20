class CreateChatSessions < ActiveRecord::Migration[8.0]
  def change
    create_table :chat_sessions do |t|
      t.string :session_id, null: false
      t.string :session_type, null: false, default: 'query'
      t.string :status, null: false, default: 'active'
      t.references :conversation, null: true, foreign_key: true
      t.references :target_note, null: true, foreign_key: { to_table: :notes }
      t.text :draft_title
      t.text :draft_content
      t.text :original_content
      t.json :metadata, default: {}
      t.text :edit_instructions
      t.datetime :started_at
      t.datetime :completed_at
      t.timestamps
    end
    
    add_index :chat_sessions, :session_id, unique: true
    add_index :chat_sessions, [:session_type, :status]
    add_index :chat_sessions, :started_at
  end
end
