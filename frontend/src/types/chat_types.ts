export type MessageType = 'user' | 'system' | 'artist';

export interface ChatMessage {
  id: string;
  type: MessageType;
  content: string;
  timestamp: string;
  sender: string;
}