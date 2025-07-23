import React, { Suspense, lazy } from 'react';

// Lazy load academy components
const VideoPlayer = lazy(() => import('../videos/VideoPlayer'));
const InteractiveQuiz = lazy(() => import('../academy/InteractiveQuiz'));
const ProgressTracker = lazy(() => import('../academy/ProgressTracker'));
const DiscussionForum = lazy(() => import('../academy/DiscussionForum'));
const ResourceLibrary = lazy(() => import('../academy/ResourceLibrary'));
const CertificateGenerator = lazy(() => import('../academy/CertificateGenerator'));
const PeerReview = lazy(() => import('../academy/PeerReview'));
const LiveSession = lazy(() => import('../academy/LiveSession'));

// Loading component for academy
const AcademyLoading = () => (
  <div className="flex items-center justify-center h-48">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <div className="text-gray-600">Loading academy content...</div>
    </div>
  </div>
);

// Lazy Academy Container
export const LazyAcademyContainer: React.FC<{ 
  showAdvanced?: boolean; 
  courseId?: string;
}> = ({ showAdvanced = false, courseId }) => {
  return (
    <div className="space-y-6">
      {/* Critical content loaded immediately */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-4">Course Overview</h1>
        {/* Critical course info */}
      </div>

      {/* Lazy loaded video player */}
      <Suspense fallback={<AcademyLoading />}>
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Video Lesson</h2>
          <VideoPlayer courseId={courseId} />
        </div>
      </Suspense>

      {/* Lazy loaded interactive components */}
      <Suspense fallback={<AcademyLoading />}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Quiz</h2>
            <InteractiveQuiz courseId={courseId} />
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Progress</h2>
            <ProgressTracker courseId={courseId} />
          </div>
        </div>
      </Suspense>

      {/* Advanced features loaded conditionally */}
      {showAdvanced && (
        <Suspense fallback={<AcademyLoading />}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Discussion</h2>
              <DiscussionForum courseId={courseId} />
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Resources</h2>
              <ResourceLibrary courseId={courseId} />
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Peer Review</h2>
              <PeerReview courseId={courseId} />
            </div>
          </div>
        </Suspense>
      )}

      {/* Certificate and live session on demand */}
      <Suspense fallback={<AcademyLoading />}>
        <div className="flex space-x-4">
          <CertificateGenerator courseId={courseId} />
          <LiveSession courseId={courseId} />
        </div>
      </Suspense>
    </div>
  );
};

// Lazy loading with route-based code splitting
export const LazyAcademyRoute: React.FC<{ route: string }> = ({ route }) => {
  const Component = React.useMemo(() => {
    switch (route) {
      case 'video':
        return lazy(() => import('../academy/VideoLesson'));
      case 'quiz':
        return lazy(() => import('../academy/QuizLesson'));
      case 'assignment':
        return lazy(() => import('../academy/AssignmentLesson'));
      case 'discussion':
        return lazy(() => import('../academy/DiscussionLesson'));
      default:
        return lazy(() => import('../academy/DefaultLesson'));
    }
  }, [route]);

  return (
    <Suspense fallback={<AcademyLoading />}>
      <Component />
    </Suspense>
  );
};

// Preload critical academy components
export const preloadAcademyComponents = (): void => {
  // Preload components that are likely to be needed
  import('../academy/VideoLesson');
  import('../academy/QuizLesson');
};

// Lazy loading with priority queue
export const usePriorityLazyLoading = (
  components: Array<{
    key: string;
    loader: () => Promise<{ default: React.ComponentType<any> }>;
    priority: 'high' | 'medium' | 'low';
  }>
) => {
  const [loadedComponents, setLoadedComponents] = React.useState<Record<string, React.ComponentType<any>>>({});
  const [loadingStates, setLoadingStates] = React.useState<Record<string, boolean>>({});

  React.useEffect(() => {
    const loadComponent = async (key: string, loader: () => Promise<{ default: React.ComponentType<any> }>) => {
      setLoadingStates(prev => ({ ...prev, [key]: true }));
      
      try {
        const module = await loader();
        setLoadedComponents(prev => ({ ...prev, [key]: module.default }));
      } catch (error) {
        console.error(`Failed to load component ${key}:`, error);
      } finally {
        setLoadingStates(prev => ({ ...prev, [key]: false }));
      }
    };

    // Load high priority components first
    const highPriority = components.filter(c => c.priority === 'high');
    const mediumPriority = components.filter(c => c.priority === 'medium');
    const lowPriority = components.filter(c => c.priority === 'low');

    // Load high priority immediately
    highPriority.forEach(({ key, loader }) => {
      loadComponent(key, loader);
    });

    // Load medium priority after a delay
    setTimeout(() => {
      mediumPriority.forEach(({ key, loader }) => {
        loadComponent(key, loader);
      });
    }, 1000);

    // Load low priority after longer delay
    setTimeout(() => {
      lowPriority.forEach(({ key, loader }) => {
        loadComponent(key, loader);
      });
    }, 3000);
  }, [components]);

  return { loadedComponents, loadingStates };
}; 