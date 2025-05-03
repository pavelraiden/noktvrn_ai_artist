import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils"; // Assuming utils.ts exists from shadcn init

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

// Mock data (replace with actual API/WebSocket logic)
const initialMessages: Message[] = [
  {
    id: '1',
    sender: 'ai',
    text: 'Hello! How can I help you refine the artistic direction today?',
    timestamp: new Date(Date.now() - 60000 * 5),
  },
  {
    id: '2',
    sender: 'user',
    text: 'Let\'s try making the next track a bit more melancholic, focus on minor keys.',
    timestamp: new Date(Date.now() - 60000 * 3),
  },
  {
    id: '3',
    sender: 'ai',
    text: 'Understood. I will adjust the parameters for the next generation to emphasize a melancholic mood using minor keys.',
    timestamp: new Date(Date.now() - 60000 * 1),
  },
];

const ChatWindow: React.FC<{ artistId?: string }> = ({ artistId }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputMessage, setInputMessage] = useState('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Function to handle sending a message (mock)
  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;

    const newUserMessage: Message = {
      id: Date.now().toString(), // Simple unique ID for mock
      sender: 'user',
      text: inputMessage,
      timestamp: new Date(),
    };

    // Mock AI response
    const aiResponse: Message = {
      id: (Date.now() + 1).toString(),
      sender: 'ai',
      text: `Okay, I received your message about "${inputMessage.substring(0, 30)}...". I'll process that. (Mock response)`, // Mock AI reply
      timestamp: new Date(Date.now() + 500), // Simulate slight delay
    };

    setMessages([...messages, newUserMessage, aiResponse]);
    setInputMessage('');
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages]);

  return (
    <Card className="flex flex-col h-[600px]"> {/* Adjust height as needed */}
      <CardHeader>
        <CardTitle>Chat with Artist AI {artistId ? `(ID: ${artistId})` : ''}</CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-hidden">
        <ScrollArea className="h-full pr-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex items-start gap-3",
                  message.sender === 'user' ? "justify-end" : ""
                )}
              >
                {message.sender === 'ai' && (
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="https://via.placeholder.com/40/800080/FFFFFF?text=AI" alt="AI" />
                    <AvatarFallback>AI</AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={cn(
                    "max-w-[75%] rounded-lg p-3 text-sm",
                    message.sender === 'user'
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  <p>{message.text}</p>
                  <p className="text-xs text-muted-foreground/80 mt-1 text-right">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                {message.sender === 'user' && (
                  <Avatar className="h-8 w-8">
                    {/* Add user avatar if available */}
                    <AvatarFallback>U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
      <CardFooter className="pt-4 border-t">
        <div className="flex w-full items-center space-x-2">
          <Input
            type="text"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            className="flex-1"
          />
          <Button type="submit" onClick={handleSendMessage}>Send</Button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default ChatWindow;

