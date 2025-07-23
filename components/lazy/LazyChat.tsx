import React, { Suspense, lazy } from 'react';

// Lazy load chat components
const ChatMessage = lazy(() => import('../chat/ChatMessage'));
const ChatInput = lazy(() => import('../chat/ChatInput'));
const ChatHistory = lazy(() => import('../chat/ChatHistory'));
const ChatAttachments = lazy(() => import('../chat/ChatAttachments'));
const ChatEmojis = lazy(() => import('../chat/ChatEmojis'));
const ChatVoice = lazy(() => import('../chat/ChatVoice'));
const ChatVideo = lazy(() => import('../chat/ChatVideo'));
const ChatSettings = lazy(() => import('../chat/ChatSettings'));

// Loading component for chat
const ChatLoading = () => (
  <div className="flex items-center justify-center h-16">
    <div className="animate-pulse flex space-x-2">
      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
    </div>
  </div>
);

// Lazy Chat Container
export const LazyChatContainer: React.FC<{ 
  showAdvanced?: boolean;
  channelId?: string;
}> = ({ showAdvanced = false, channelId }) => {
  return (
    <div className="flex flex-col h-full">
      {/* Critical chat header */}
      <div className="bg-white border-b p-4">
        <h2 className="text-lg font-semibold">Chat</h2>
      </div>

      {/* Lazy loaded chat history */}
      <div className="flex-1 overflow-y-auto">
        <Suspense fallback={<ChatLoading />}>
          <ChatHistory channelId={channelId} />
        </Suspense>
      </div>

      {/* Lazy loaded chat input */}
      <div className="bg-white border-t p-4">
        <Suspense fallback={<ChatLoading />}>
          <ChatInput channelId={channelId} />
        </Suspense>
      </div>

      {/* Advanced chat features loaded conditionally */}
      {showAdvanced && (
        <Suspense fallback={<ChatLoading />}>
          <div className="bg-white border-t p-4">
            <div className="flex space-x-2">
              <ChatAttachments channelId={channelId} />
              <ChatEmojis />
              <ChatVoice channelId={channelId} />
              <ChatVideo channelId={channelId} />
            </div>
          </div>
        </Suspense>
      )}

      {/* Settings panel loaded on demand */}
      <Suspense fallback={<ChatLoading />}>
        <ChatSettings channelId={channelId} />
      </Suspense>
    </div>
  );
};

// Lazy loading with virtual scrolling for chat
export const LazyVirtualChat: React.FC<{ 
  messages: Array<any>;
  itemHeight: number;
  containerHeight: number;
}> = ({ messages, itemHeight, containerHeight }) => {
  const [visibleRange, setVisibleRange] = React.useState({ start: 0, end: 10 });
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;
      
      const scrollTop = containerRef.current.scrollTop;
      const start = Math.floor(scrollTop / itemHeight);
      const end = Math.min(start + Math.ceil(containerHeight / itemHeight) + 2, messages.length);
      
      setVisibleRange({ start, end });
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [itemHeight, containerHeight, messages.length]);

  const visibleMessages = messages.slice(visibleRange.start, visibleRange.end);
  const totalHeight = messages.length * itemHeight;
  const offsetY = visibleRange.start * itemHeight;

  return (
    <div 
      ref={containerRef}
      className="overflow-y-auto"
      style={{ height: containerHeight }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          <Suspense fallback={<ChatLoading />}>
            {visibleMessages.map((message, index) => (
              <div key={message.id} style={{ height: itemHeight }}>
                <ChatMessage message={message} />
              </div>
            ))}
          </Suspense>
        </div>
      </div>
    </div>
  );
};

// Lazy loading with progressive enhancement
export const ProgressiveChat: React.FC<{ 
  channelId?: string;
  features?: string[];
}> = ({ channelId, features = [] }) => {
  const [loadedFeatures, setLoadedFeatures] = React.useState<Set<string>>(new Set(['basic']));

  React.useEffect(() => {
    // Load basic features immediately
    setLoadedFeatures(prev => new Set([...prev, 'basic']));

    // Load advanced features progressively
    const loadFeature = async (feature: string) => {
      try {
        switch (feature) {
          case 'attachments':
            await import('../chat/ChatAttachments');
            break;
          case 'voice':
            await import('../chat/ChatVoice');
            break;
          case 'video':
            await import('../chat/ChatVideo');
            break;
          case 'emojis':
            await import('../chat/ChatEmojis');
            break;
        }
        setLoadedFeatures(prev => new Set([...prev, feature]));
      } catch (error) {
        console.error(`Failed to load feature ${feature}:`, error);
      }
    };

    // Load features with different priorities
    features.forEach((feature, index) => {
      setTimeout(() => loadFeature(feature), index * 500);
    });
  }, [features]);

  return (
    <div className="space-y-4">
      {/* Basic chat always loaded */}
      <div className="bg-white p-4 rounded-lg shadow">
        <Suspense fallback={<ChatLoading />}>
          <ChatInput channelId={channelId} />
        </Suspense>
      </div>

      {/* Progressive feature loading */}
      {loadedFeatures.has('attachments') && (
        <Suspense fallback={<ChatLoading />}>
          <ChatAttachments channelId={channelId} />
        </Suspense>
      )}

      {loadedFeatures.has('voice') && (
        <Suspense fallback={<ChatLoading />}>
          <ChatVoice channelId={channelId} />
        </Suspense>
      )}

      {loadedFeatures.has('video') && (
        <Suspense fallback={<ChatLoading />}>
          <ChatVideo channelId={channelId} />
        </Suspense>
      )}

      {loadedFeatures.has('emojis') && (
        <Suspense fallback={<ChatLoading />}>
          <ChatEmojis />
        </Suspense>
      )}
    </div>
  );
};

// Lazy loading with network-aware loading
export const NetworkAwareChat: React.FC<{ channelId?: string }> = ({ channelId }) => {
  const [connectionSpeed, setConnectionSpeed] = React.useState<'fast' | 'slow' | 'unknown'>('unknown');

  React.useEffect(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const updateConnectionSpeed = () => {
        if (connection.effectiveType === '4g') {
          setConnectionSpeed('fast');
        } else if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
          setConnectionSpeed('slow');
        } else {
          setConnectionSpeed('unknown');
        }
      };

      updateConnectionSpeed();
      connection.addEventListener('change', updateConnectionSpeed);
      return () => connection.removeEventListener('change', updateConnectionSpeed);
    }
  }, []);

  // Load different components based on connection speed
  const shouldLoadAdvanced = connectionSpeed === 'fast';

  return (
    <div className="space-y-4">
      {/* Basic chat always loaded */}
      <Suspense fallback={<ChatLoading />}>
        <ChatInput channelId={channelId} />
      </Suspense>

      {/* Advanced features only on fast connections */}
      {shouldLoadAdvanced && (
        <Suspense fallback={<ChatLoading />}>
          <div className="flex space-x-2">
            <ChatAttachments channelId={channelId} />
            <ChatVoice channelId={channelId} />
            <ChatVideo channelId={channelId} />
          </div>
        </Suspense>
      )}
    </div>
  );
}; 