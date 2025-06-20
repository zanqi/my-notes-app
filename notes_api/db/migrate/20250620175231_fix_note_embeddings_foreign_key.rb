class FixNoteEmbeddingsForeignKey < ActiveRecord::Migration[8.0]
  def up
    # Remove the existing foreign key constraint
    remove_foreign_key :note_embeddings, :notes
    
    # Add the foreign key with cascade delete
    add_foreign_key :note_embeddings, :notes, on_delete: :cascade
  end

  def down
    # Remove the cascade foreign key
    remove_foreign_key :note_embeddings, :notes
    
    # Add back the original foreign key (without cascade)
    add_foreign_key :note_embeddings, :notes
  end
end
