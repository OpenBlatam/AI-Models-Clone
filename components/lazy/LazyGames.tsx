import React, { Suspense, lazy } from 'react';

// Lazy load game components
const GameCanvas = lazy(() => import('../games/GameCanvas'));
const GameControls = lazy(() => import('../games/GameControls'));
const GameScoreboard = lazy(() => import('../games/GameScoreboard'));
const GameLeaderboard = lazy(() => import('../games/GameLeaderboard'));
const GameChat = lazy(() => import('../games/GameChat'));
const GameSettings = lazy(() => import('../games/GameSettings'));
const GameTutorial = lazy(() => import('../games/GameTutorial'));
const GameReplay = lazy(() => import('../games/GameReplay'));

// Loading component for games
const GameLoading = () => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-600 mx-auto mb-4"></div>
      <div className="text-gray-600">Loading game...</div>
    </div>
  </div>
);

// Lazy Game Container
export const LazyGameContainer: React.FC<{ 
  gameId: string;
  showAdvanced?: boolean;
}> = ({ gameId, showAdvanced = false }) => {
  return (
    <div className="space-y-6">
      {/* Critical game canvas loaded immediately */}
      <div className="bg-black rounded-lg overflow-hidden">
        <Suspense fallback={<GameLoading />}>
          <GameCanvas gameId={gameId} />
        </Suspense>
      </div>

      {/* Lazy loaded game controls */}
      <div className="bg-white p-4 rounded-lg shadow">
        <Suspense fallback={<GameLoading />}>
          <GameControls gameId={gameId} />
        </Suspense>
      </div>

      {/* Lazy loaded scoreboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Scoreboard</h3>
          <Suspense fallback={<GameLoading />}>
            <GameScoreboard gameId={gameId} />
          </Suspense>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Leaderboard</h3>
          <Suspense fallback={<GameLoading />}>
            <GameLeaderboard gameId={gameId} />
          </Suspense>
        </div>
      </div>

      {/* Advanced features loaded conditionally */}
      {showAdvanced && (
        <Suspense fallback={<GameLoading />}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Game Chat</h3>
              <GameChat gameId={gameId} />
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Tutorial</h3>
              <GameTutorial gameId={gameId} />
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Replay</h3>
              <GameReplay gameId={gameId} />
            </div>
          </div>
        </Suspense>
      )}

      {/* Settings loaded on demand */}
      <Suspense fallback={<GameLoading />}>
        <GameSettings gameId={gameId} />
      </Suspense>
    </div>
  );
};

// Lazy loading with game state management
export const LazyGameWithState: React.FC<{ gameId: string }> = ({ gameId }) => {
  const [gameState, setGameState] = React.useState<'loading' | 'playing' | 'paused' | 'finished'>('loading');
  const [loadedComponents, setLoadedComponents] = React.useState<Set<string>>(new Set());

  React.useEffect(() => {
    // Load essential components immediately
    setLoadedComponents(prev => new Set([...prev, 'canvas', 'controls']));

    // Load additional components based on game state
    const loadComponent = async (component: string) => {
      try {
        switch (component) {
          case 'scoreboard':
            await import('../games/GameScoreboard');
            break;
          case 'leaderboard':
            await import('../games/GameLeaderboard');
            break;
          case 'chat':
            await import('../games/GameChat');
            break;
        }
        setLoadedComponents(prev => new Set([...prev, component]));
      } catch (error) {
        console.error(`Failed to load game component ${component}:`, error);
      }
    };

    // Load components progressively
    setTimeout(() => loadComponent('scoreboard'), 1000);
    setTimeout(() => loadComponent('leaderboard'), 2000);
    setTimeout(() => loadComponent('chat'), 3000);
  }, [gameId]);

  return (
    <div className="space-y-6">
      {/* Game canvas always loaded */}
      <div className="bg-black rounded-lg overflow-hidden">
        <Suspense fallback={<GameLoading />}>
          <GameCanvas gameId={gameId} />
        </Suspense>
      </div>

      {/* Conditionally loaded components */}
      {loadedComponents.has('scoreboard') && (
        <Suspense fallback={<GameLoading />}>
          <GameScoreboard gameId={gameId} />
        </Suspense>
      )}

      {loadedComponents.has('leaderboard') && (
        <Suspense fallback={<GameLoading />}>
          <GameLeaderboard gameId={gameId} />
        </Suspense>
      )}

      {loadedComponents.has('chat') && (
        <Suspense fallback={<GameLoading />}>
          <GameChat gameId={gameId} />
        </Suspense>
      )}
    </div>
  );
};

// Lazy loading with performance monitoring
export const PerformanceAwareGame: React.FC<{ gameId: string }> = ({ gameId }) => {
  const [fps, setFps] = React.useState(60);
  const [shouldLoadHeavy, setShouldLoadHeavy] = React.useState(true);

  React.useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();

    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime - lastTime >= 1000) {
        const currentFps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        setFps(currentFps);
        
        // Load heavy components only if FPS is good
        setShouldLoadHeavy(currentFps > 30);
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };

    requestAnimationFrame(measureFPS);
  }, []);

  return (
    <div className="space-y-6">
      {/* Game canvas always loaded */}
      <div className="bg-black rounded-lg overflow-hidden">
        <Suspense fallback={<GameLoading />}>
          <GameCanvas gameId={gameId} />
        </Suspense>
      </div>

      {/* Performance indicator */}
      <div className="bg-white p-2 rounded-lg shadow text-sm">
        FPS: {fps} - Heavy components: {shouldLoadHeavy ? 'Enabled' : 'Disabled'}
      </div>

      {/* Heavy components loaded based on performance */}
      {shouldLoadHeavy && (
        <Suspense fallback={<GameLoading />}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GameLeaderboard gameId={gameId} />
            <GameReplay gameId={gameId} />
          </div>
        </Suspense>
      )}

      {/* Light components always loaded */}
      <Suspense fallback={<GameLoading />}>
        <GameControls gameId={gameId} />
      </Suspense>
    </div>
  );
};

// Lazy loading with user interaction triggers
export const InteractionTriggeredGame: React.FC<{ gameId: string }> = ({ gameId }) => {
  const [interactions, setInteractions] = React.useState<Set<string>>(new Set());
  const [loadedFeatures, setLoadedFeatures] = React.useState<Set<string>>(new Set(['basic']));

  const handleInteraction = (feature: string) => {
    setInteractions(prev => new Set([...prev, feature]));
    
    // Load feature on first interaction
    if (!loadedFeatures.has(feature)) {
      const loadFeature = async () => {
        try {
          switch (feature) {
            case 'tutorial':
              await import('../games/GameTutorial');
              break;
            case 'settings':
              await import('../games/GameSettings');
              break;
            case 'replay':
              await import('../games/GameReplay');
              break;
          }
          setLoadedFeatures(prev => new Set([...prev, feature]));
        } catch (error) {
          console.error(`Failed to load feature ${feature}:`, error);
        }
      };
      loadFeature();
    }
  };

  return (
    <div className="space-y-6">
      {/* Basic game always loaded */}
      <div className="bg-black rounded-lg overflow-hidden">
        <Suspense fallback={<GameLoading />}>
          <GameCanvas gameId={gameId} />
        </Suspense>
      </div>

      {/* Interaction-triggered features */}
      <div className="flex space-x-4">
        <button 
          onClick={() => handleInteraction('tutorial')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Tutorial
        </button>
        
        <button 
          onClick={() => handleInteraction('settings')}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Settings
        </button>
        
        <button 
          onClick={() => handleInteraction('replay')}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Replay
        </button>
      </div>

      {/* Loaded features */}
      {loadedFeatures.has('tutorial') && (
        <Suspense fallback={<GameLoading />}>
          <GameTutorial gameId={gameId} />
        </Suspense>
      )}

      {loadedFeatures.has('settings') && (
        <Suspense fallback={<GameLoading />}>
          <GameSettings gameId={gameId} />
        </Suspense>
      )}

      {loadedFeatures.has('replay') && (
        <Suspense fallback={<GameLoading />}>
          <GameReplay gameId={gameId} />
        </Suspense>
      )}
    </div>
  );
}; 