
import React, { useRef, useEffect, useState } from 'react';
import type { Message } from '../types';
import { Button } from './common/Button';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  isScenarioSet: boolean;
}

const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  const roleStyles = {
    user: 'border-l-blue-400 text-blue-300',
    assistant: 'border-l-cyan-400 text-cyan-300',
    system: 'border-l-yellow-500 text-yellow-400 italic text-sm',
    tool: 'border-l-purple-400 text-purple-300 text-xs',
  };

  return (
    <div className={`mb-4 pl-4 border-l-2 ${roleStyles[message.role]}`}>
      <strong className="block capitalize font-bold tracking-wider">{message.role}</strong>
      <p className="whitespace-pre-wrap font-mono">{message.text}</p>
    </div>
  );
};


export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, onSendMessage, isLoading, isScenarioSet }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = () => {
    if (input.trim() && !isLoading && isScenarioSet) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-cyan-700 scrollbar-track-gray-900">
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}
         {isLoading && messages[messages.length - 1]?.role === 'user' && (
            <div className="flex items-center gap-2 text-cyan-400 mt-4">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-cyan-400"></div>
                <span>GM is thinking...</span>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex-shrink-0 p-4 border-t border-cyan-500/30">
        <div className="flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isScenarioSet ? "Describe your action..." : "Generate a scenario to begin chat"}
            disabled={isLoading || !isScenarioSet}
            className="flex-1 bg-black/50 border border-cyan-700 text-cyan-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50"
          />
          <Button onClick={handleSend} disabled={isLoading || !isScenarioSet}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
