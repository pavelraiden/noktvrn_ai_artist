import React from 'react';
import { ChatMessage as ChatMessageType } from '../../types';
import { formatDate } from '../../utils/formatters';

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
            ? 'bg-primary-100 text-primary-900'
            : 'bg-white border border-gray-200 text-gray-900'
        }`}
      >
        <div className="text-sm">{message.content}</div>
        <div className="mt-1 text-xs text-gray-500 text-right">
          {formatDate(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;