class Api::V1::MessagesController < ApplicationController
  before_action :set_conversation
  before_action :set_message, only: [:show, :update, :destroy]

  def index
    @messages = @conversation.messages.chronological.includes(:conversation)
    render json: @messages.map { |message| message_json(message) }
  end

  def show
    render json: message_json(@message)
  end

  def create
    @message = @conversation.messages.build(message_params)
    
    if @message.save
      # Background job will automatically trigger AI response for user messages
      render json: message_json(@message), status: :created
    else
      render json: { errors: @message.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def update
    if @message.update(message_params)
      render json: message_json(@message)
    else
      render json: { errors: @message.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def destroy
    @message.destroy
    head :no_content
  end

  private

  def set_conversation
    @conversation = Conversation.find(params[:conversation_id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: "Conversation not found" }, status: :not_found
  end

  def set_message
    @message = @conversation.messages.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: "Message not found" }, status: :not_found
  end

  def message_params
    params.require(:message).permit(:content, :role)
  end

  def message_json(message)
    {
      id: message.id,
      content: message.content,
      role: message.role,
      conversation_id: message.conversation_id,
      created_at: message.created_at,
      updated_at: message.updated_at
    }
  end
end 