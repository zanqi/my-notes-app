class Api::V1::ConversationsController < ApplicationController
  before_action :set_conversation, only: [:show, :update, :destroy]

  def index
    @conversations = Conversation.includes(:messages)
                                .recent
                                .limit(50)
    
    render json: @conversations.map { |conv| conversation_json(conv) }
  end

  def show
    render json: conversation_with_messages_json(@conversation)
  end

  def create
    @conversation = Conversation.new(conversation_params)
    
    if @conversation.save
      render json: conversation_json(@conversation), status: :created
    else
      render json: { errors: @conversation.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def update
    if @conversation.update(conversation_params)
      render json: conversation_json(@conversation)
    else
      render json: { errors: @conversation.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def destroy
    @conversation.destroy
    head :no_content
  end

  private

  def set_conversation
    @conversation = Conversation.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: "Conversation not found" }, status: :not_found
  end

  def conversation_params
    params.require(:conversation).permit(:title)
  end

  def conversation_json(conversation)
    {
      id: conversation.id,
      title: conversation.title,
      message_count: conversation.message_count,
      last_message: conversation.last_message&.content&.truncate(100),
      created_at: conversation.created_at,
      updated_at: conversation.updated_at
    }
  end

  def conversation_with_messages_json(conversation)
    {
      id: conversation.id,
      title: conversation.title,
      created_at: conversation.created_at,
      updated_at: conversation.updated_at,
      messages: conversation.messages.chronological.map do |message|
        {
          id: message.id,
          content: message.content,
          role: message.role,
          created_at: message.created_at
        }
      end
    }
  end
end 