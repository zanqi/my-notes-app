require 'net/http'
require 'uri'
require 'json'

class ProcessChatMessageJob < ApplicationJob
  queue_as :default

  def perform(message_id)
    message = Message.find(message_id)
    conversation = message.conversation
    
    # Only process user messages
    return unless message.user_message?
    
    # Get AI response from LangChain service
    ai_response = get_ai_response(message, conversation)
    
    # Create assistant message with the response
    conversation.messages.create!(
      content: ai_response[:content],
      role: 'assistant'
    )
    
    Rails.logger.info "Successfully processed chat message #{message.id}"
  rescue StandardError => e
    Rails.logger.error "Failed to process chat message #{message_id}: #{e.message}"
    
    # Create error message for user
    conversation = Message.find(message_id).conversation
    conversation.messages.create!(
      content: "Sorry, I encountered an error processing your message. Please try again.",
      role: 'assistant'
    )
    
    raise e
  end

  private

  def get_ai_response(message, conversation)
    uri = URI('http://localhost:8001/chat')
    
    # Prepare conversation history
    messages_history = conversation.messages
                                   .chronological
                                   .limit(10) # Last 10 messages for context
                                   .map { |msg| { role: msg.role, content: msg.content } }
    
    payload = {
      message: message.content,
      conversation_id: conversation.id,
      history: messages_history
    }

    response = Net::HTTP.post(uri, payload.to_json, {
      'Content-Type' => 'application/json',
      'Accept' => 'application/json'
    })

    if response.code == '200'
      JSON.parse(response.body).with_indifferent_access
    else
      raise "LangChain service error: #{response.code} - #{response.body}"
    end
  end
end 