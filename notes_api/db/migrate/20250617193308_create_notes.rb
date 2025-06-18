class CreateNotes < ActiveRecord::Migration[8.0]
  def change
    create_table :notes do |t|
      t.string :title
      t.text :content

      t.timestamps
    end

    add_index :notes, :title
    add_index :notes, :created_at
  end
end
