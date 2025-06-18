class Api::V1::NotesController < ApplicationController
  before_action :set_note, only: [:show, :update, :destroy]

  def index
    @notes = Note.all.order(created_at: :desc)
    render json: @notes
  end

  def show
    render json: @note
  end

  def create
    @note = Note.new(note_params)
    if @note.save
      render json: @note, status: :created
    else
      render json: { errors: @note.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def update
    if @note.update(note_params)
      render json: @note
    else
      render json: { errors: @note.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def destroy
    @note.destroy
    head :no_content
  end

  private

  def set_note
    @note = Note.find(params[:id])
    if @note.nil?
      render json: { error: "Note not found" }, status: :not_found
    end
  end

  def note_params
    params.require(:note).permit(:title, :content)
  end
end
