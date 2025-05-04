import React from 'react';
import { ChatMessage as ChatMessageType } from '../../types'; // Adjusted path
import { formatDate } from '../../utils/formatters'; // Adjusted path

interface ChatMessageProps {
  message: ChatMessageType;
}

/**
 * ChatMessage component for displaying a single message in the chat
 * @param props ChatMessage properties
 * @returns ChatMessage component
 */
const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.type === 'user';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[80%] p-3 rounded-lg ${
          isUser
            ? 'bg-blue-100 text-blue-900' // Example color, adjust as needed
            : 'bg-white border border-gray-200 text-gray-900'
        }`}
      >
        <div className="text-sm">{message.content}</div>
        <div className="mt-1 text-xs text-gray-500 text-right">
          {/* Assuming formatDate handles ISO strings correctly */}
          {formatDate(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;

