class CreateNoteEmbeddings < ActiveRecord::Migration[8.0]
  def change
    create_table :note_embeddings do |t|
      t.references :note, null: false, foreign_key: true
      t.string :embedding_id
      t.datetime :synced_at

      t.timestamps
    end
  end
end
