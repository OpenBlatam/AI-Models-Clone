'use client';

import { useState, useRef, useEffect } from 'react';
import { useRobotStore } from '@/lib/store/robotStore';
import { Send, Bot, User } from 'lucide-react';
import { format } from 'date-fns';

export default function ChatPanel() {
  const { chatMessages, sendChatMessage, isChatConnected } = useRobotStore();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const message = input.trim();
    setInput('');
    await sendChatMessage(message);
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Chat con el Robot</h2>
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isChatConnected ? 'bg-green-400' : 'bg-gray-400'
            }`}
          />
          <span className="text-sm text-gray-400">
            {isChatConnected ? 'Conectado' : 'Desconectado'}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Envía un mensaje para comenzar</p>
            <p className="text-sm mt-2">
              Ejemplo: "move to (0.5, 0.3, 0.2)" o "go home"
            </p>
          </div>
        ) : (
          chatMessages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}
              <div
                className={`max-w-[70%] rounded-lg p-3 ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-100'
                }`}
              >
                <p className="text-sm">{msg.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {format(msg.timestamp, 'HH:mm:ss')}
                </p>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe un comando o pregunta..."
            className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            type="submit"
            disabled={!input.trim()}
            className="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-5 h-5" />
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}

