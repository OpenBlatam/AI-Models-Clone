import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { MessageCircle, Send, X, Bot, User, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { toast } from 'react-hot-toast';

const ChatbotContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  height: 600px;
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transform: ${props => props.isOpen ? 'translateY(0)' : 'translateY(100%)'};
  transition: transform 0.3s ease;
`;

const ChatbotHeader = styled.div`
  padding: 16px;
  background: ${props => props.theme.colors.primary};
  color: white;
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
`;

const ChatbotTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }
`;

const ChatbotBody = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const MessageAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${props => props.isUser ? 
    props.theme.colors.primary : 
    props.theme.colors.surface
  };
  color: ${props => props.isUser ? 'white' : props.theme.colors.text};
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  background-color: ${props => props.isUser ? 
    props.theme.colors.primary : 
    props.theme.colors.surface
  };
  color: ${props => props.isUser ? 'white' : props.theme.colors.text};
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
`;

const MessageMeta = styled.div`
  font-size: 11px;
  color: ${props => props.theme.colors.textSecondary};
  margin-top: 4px;
  ${props => props.isUser ? 'text-align: right;' : ''}
`;

const InputContainer = styled.div`
  padding: 16px;
  border-top: 1px solid ${props => props.theme.colors.border};
  display: flex;
  gap: 8px;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 24px;
  font-size: 14px;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const SendButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: ${props => props.theme.colors.primary};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.theme.colors.primaryDark};
    transform: scale(1.05);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const VoiceButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid ${props => props.theme.colors.border};
  background-color: ${props => props.isListening ? 
    props.theme.colors.error : 
    props.theme.colors.background
  };
  color: ${props => props.isListening ? 'white' : props.theme.colors.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: ${props => props.isListening ? 
      props.theme.colors.errorDark : 
      props.theme.colors.surface
    };
  }
`;

const ToggleButton = styled.button`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background-color: ${props => props.theme.colors.primary};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  z-index: 1001;
  
  &:hover {
    background-color: ${props => props.theme.colors.primaryDark};
    transform: scale(1.1);
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.theme.colors.textSecondary};
  font-size: 12px;
  padding: 8px 16px;
`;

const TypingDots = styled.div`
  display: flex;
  gap: 4px;
  
  div {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: ${props => props.theme.colors.textSecondary};
    animation: typing 1.4s infinite ease-in-out;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
  
  @keyframes typing {
    0%, 80%, 100% {
      transform: scale(0);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;

const ChatbotInterface = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chatbot session
  useEffect(() => {
    if (isOpen && !sessionId) {
      initializeChatbot();
    }
  }, [isOpen]);

  const initializeChatbot = async () => {
    try {
      const response = await fetch('/api/chatbot/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'default_user'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        connectWebSocket(data.session_id);
      } else {
        toast.error('Error inicializando chatbot');
      }
    } catch (error) {
      console.error('Error inicializando chatbot:', error);
      toast.error('Error conectando con el chatbot');
    }
  };

  const connectWebSocket = (sessionId) => {
    try {
      const websocket = new WebSocket(`ws://localhost:8000/api/chatbot/ws/${sessionId}`);
      
      websocket.onopen = () => {
        setIsConnected(true);
        console.log('Conectado al chatbot WebSocket');
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'message_response') {
          const newMessage = {
            id: `msg_${Date.now()}`,
            message: '',
            response: data.response,
            timestamp: data.timestamp,
            message_type: 'assistant',
            confidence: data.confidence,
            intent: data.intent,
            source_documents: data.source_documents
          };
          
          setMessages(prev => [...prev, newMessage]);
          setIsLoading(false);
        } else if (data.type === 'chat_history') {
          setMessages(data.messages);
        } else if (data.type === 'connection_established') {
          console.log('Conexión establecida con el chatbot');
        }
      };
      
      websocket.onclose = () => {
        setIsConnected(false);
        console.log('Desconectado del chatbot WebSocket');
      };
      
      websocket.onerror = (error) => {
        console.error('Error en WebSocket del chatbot:', error);
        setIsConnected(false);
      };
      
      setWs(websocket);
    } catch (error) {
      console.error('Error conectando WebSocket:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || !ws) return;

    const userMessage = {
      id: `msg_${Date.now()}`,
      message: inputMessage,
      response: '',
      timestamp: new Date().toISOString(),
      message_type: 'user'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      ws.send(JSON.stringify({
        action: 'send_message',
        message: inputMessage
      }));
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      setIsLoading(false);
      toast.error('Error enviando mensaje');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleVoiceListening = async () => {
    if (isListening) {
      // Stop listening
      try {
        await fetch('/api/voice/stop-listening', { method: 'POST' });
        setIsListening(false);
      } catch (error) {
        console.error('Error deteniendo escucha:', error);
      }
    } else {
      // Start listening
      try {
        const response = await fetch('/api/voice/start-listening', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: 'user_id=default_user'
        });
        
        if (response.ok) {
          setIsListening(true);
          // Simular detención automática después de 5 segundos
          setTimeout(() => {
            setIsListening(false);
          }, 5000);
        }
      } catch (error) {
        console.error('Error iniciando escucha:', error);
        toast.error('Error con el micrófono');
      }
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatConfidence = (confidence) => {
    return `${Math.round(confidence * 100)}%`;
  };

  return (
    <>
      <ToggleButton onClick={() => setIsOpen(!isOpen)}>
        <MessageCircle size={24} />
      </ToggleButton>

      <ChatbotContainer isOpen={isOpen}>
        <ChatbotHeader onClick={() => setIsOpen(false)}>
          <ChatbotTitle>
            <Bot size={20} />
            Asistente IA
          </ChatbotTitle>
          <CloseButton>
            <X size={16} />
          </CloseButton>
        </ChatbotHeader>

        <ChatbotBody>
          <MessagesContainer>
            {messages.map((message) => (
              <Message key={message.id} isUser={message.message_type === 'user'}>
                <MessageAvatar isUser={message.message_type === 'user'}>
                  {message.message_type === 'user' ? <User size={16} /> : <Bot size={16} />}
                </MessageAvatar>
                <div style={{ flex: 1 }}>
                  <MessageContent isUser={message.message_type === 'user'}>
                    {message.message_type === 'user' ? message.message : message.response}
                  </MessageContent>
                  <MessageMeta isUser={message.message_type === 'user'}>
                    {formatTimestamp(message.timestamp)}
                    {message.confidence && (
                      <span> • Confianza: {formatConfidence(message.confidence)}</span>
                    )}
                    {message.intent && (
                      <span> • {message.intent}</span>
                    )}
                  </MessageMeta>
                </div>
              </Message>
            ))}
            
            {isLoading && (
              <Message>
                <MessageAvatar>
                  <Bot size={16} />
                </MessageAvatar>
                <LoadingIndicator>
                  <TypingDots>
                    <div></div>
                    <div></div>
                    <div></div>
                  </TypingDots>
                  El asistente está escribiendo...
                </LoadingIndicator>
              </Message>
            )}
            
            <div ref={messagesEndRef} />
          </MessagesContainer>

          <InputContainer>
            <VoiceButton
              isListening={isListening}
              onClick={toggleVoiceListening}
              title={isListening ? "Detener escucha" : "Iniciar escucha"}
            >
              {isListening ? <MicOff size={16} /> : <Mic size={16} />}
            </VoiceButton>
            
            <MessageInput
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje..."
              disabled={isLoading}
            />
            
            <SendButton
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
            >
              <Send size={16} />
            </SendButton>
          </InputContainer>
        </ChatbotBody>
      </ChatbotContainer>
    </>
  );
};

export default ChatbotInterface;


























