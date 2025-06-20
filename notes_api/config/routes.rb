Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :notes, only: [:index, :show, :create, :update, :destroy] do
        member do
          patch :update_from_chat  # Update note through chat
          get :preview_changes     # Preview changes before applying
        end
        collection do
          get :find_by_description # Find notes by natural language description
        end
      end
      
      # Chat functionality routes
      resources :chat, only: [] do
        collection do
          post :sync_notes        # Existing sync functionality
          get :sync_status        # Existing sync status
          get :health_check       # Existing health check
        end
      end
      
      # Chat session management routes (new for edit functionality)
      resources :chat_sessions, only: [:create, :show, :update, :destroy] do
        member do
          post :start_edit        # Start editing a note
          post :process_edit      # Process edit instructions
          post :apply_changes     # Apply pending changes
          delete :cancel_edit     # Cancel edit session
        end
      end
    end
  end
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Defines the root path route ("/")
  # root "posts#index"
end
