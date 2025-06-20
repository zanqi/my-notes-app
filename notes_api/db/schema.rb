# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 2025_06_19_231232) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "chat_sessions", force: :cascade do |t|
    t.string "session_id", null: false
    t.string "session_type", default: "query", null: false
    t.string "status", default: "active", null: false
    t.bigint "conversation_id"
    t.bigint "target_note_id"
    t.text "draft_title"
    t.text "draft_content"
    t.text "original_content"
    t.json "metadata", default: {}
    t.text "edit_instructions"
    t.datetime "started_at"
    t.datetime "completed_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["conversation_id"], name: "index_chat_sessions_on_conversation_id"
    t.index ["session_id"], name: "index_chat_sessions_on_session_id", unique: true
    t.index ["session_type", "status"], name: "index_chat_sessions_on_session_type_and_status"
    t.index ["started_at"], name: "index_chat_sessions_on_started_at"
    t.index ["target_note_id"], name: "index_chat_sessions_on_target_note_id"
  end

  create_table "conversations", force: :cascade do |t|
    t.string "title"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "messages", force: :cascade do |t|
    t.bigint "conversation_id", null: false
    t.text "content"
    t.string "role"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["conversation_id"], name: "index_messages_on_conversation_id"
  end

  create_table "note_embeddings", force: :cascade do |t|
    t.bigint "note_id", null: false
    t.string "embedding_id"
    t.datetime "synced_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["note_id"], name: "index_note_embeddings_on_note_id"
  end

  create_table "notes", force: :cascade do |t|
    t.string "title"
    t.text "content"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["created_at"], name: "index_notes_on_created_at"
    t.index ["title"], name: "index_notes_on_title"
  end

  add_foreign_key "chat_sessions", "conversations"
  add_foreign_key "chat_sessions", "notes", column: "target_note_id"
  add_foreign_key "messages", "conversations"
  add_foreign_key "note_embeddings", "notes"
end
