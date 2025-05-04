import React, { useEffect, useRef, useState } from 'react';
import { useSocket } from '../../hooks/socket_hook'; // Adjusted path
import ChatMessage from './ChatMessage';
import { ChatMessage as ChatMessageType } from '../../types'; // Adjusted path

interface ChatWindowProps {
  artistId: string;
}

/**
 * ChatWindow component for real-time chat with an artist
 * @param props ChatWindow properties
 * @returns ChatWindow component
 */
const ChatWindow: React.FC<ChatWindowProps> = ({ artistId }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // TODO: Replace localhost with actual backend URL from config/env
  const { socket, connected } = useSocket(`ws://localhost:8000/ws/chat/${artistId}`);

  useEffect(() => {
    if (socket) {
      // Listen for incoming messages
      socket.on('message', (message: ChatMessageType) => {
        // Ensure message has a unique ID, timestamp, and correct type
        const receivedMessage: ChatMessageType = {
          ...message,
          id: message.id || Date.now().toString(), // Fallback ID
          timestamp: message.timestamp || new Date().toISOString(), // Fallback timestamp
          type: message.type || 'artist', // Assume non-user messages are from artist
        };
        setMessages((prevMessages) => [...prevMessages, receivedMessage]);
      });

      // Load message history
      // TODO: Implement proper history loading if backend supports it
      // socket.emit('get_history', { artistId }, (response: { history: ChatMessageType[] }) => {
      //   setMessages(response.history);
      // });

      // Example: Add a welcome message
      setMessages([
        {
          id: 'welcome',
          type: 'system',
          content: `Connected to chat for artist ${artistId}.`,
          timestamp: new Date().toISOString(),
          sender: 'system',
        }
      ]);
    }

    return () => {
      if (socket) {
        socket.off('message');
      }
    };
  }, [socket, artistId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handles sending a message
   */
  const handleSendMessage = () => {
    if (inputMessage.trim() && socket && connected) {
      const newMessage: ChatMessageType = {
        id: Date.now().toString(),
        type: 'user',
        content: inputMessage,
        timestamp: new Date().toISOString(),
        sender: 'user', // Assuming 'user' is the sender ID or role
      };

      // Send message to server
      // TODO: Verify backend event name and payload structure
      socket.emit('send_message', {
        artist_id: artistId, // Match backend expectation if needed
        text: inputMessage, // Match backend expectation if needed
      });

      // Add message to local state immediately for responsiveness
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInputMessage('');
    }
  };

  /**
   * Handles key press events in the input field
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[600px] border border-gray-200 rounded-lg bg-white">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <div className="text-lg font-medium">Chat with Artist</div>
        <div className="flex items-center">
          <span
            className={`inline-block w-2.5 h-2.5 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}
          ></span>
          <span className="ml-2 text-sm text-gray-500">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
        {messages.length === 0 && !connected && (
           <div className="flex items-center justify-center h-full text-gray-500">
             Connecting to chat...
           </div>
        )}
        {messages.length === 0 && connected && (
          <div className="flex items-center justify-center h-full text-gray-500">
            No messages yet. Start the conversation!
          </div>
        )}
        {messages.length > 0 && (
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="px-4 py-3 border-t border-gray-200 bg-white">
        <div className="flex">
          <input
            type="text"
            placeholder={connected ? "Type your message..." : "Connecting..."}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!connected}
          />
          {/* Using the Button component implemented earlier */}
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleSendMessage}
            disabled={!connected || !inputMessage.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;

