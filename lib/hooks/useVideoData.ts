import { useState, useEffect } from 'react';
import { toast } from 'sonner';

interface VideoData {
  video: {
    id: string;
    title: string;
    description: string;
    url: string;
    thumbnail: string;
    duration: string;
    progress: number;
    experience: number;
    isCompleted: boolean;
  };
  resources: {
    id: string;
    title: string;
    type: "file" | "reading";
    url: string;
  }[];
  comments: {
    id: string;
    content: string;
    createdAt: string;
    likes: number;
    isLiked: boolean;
    user: {
      name: string;
      image: string;
      email: string;
    };
    replies?: any[];
  }[];
}

export function useVideoData(videoId: string, courseId: string) {
  const [data, setData] = useState<VideoData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVideoData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [videoRes, resourcesRes, commentsRes] = await Promise.all([
          fetch(`/api/videos/${videoId}?courseId=${courseId}`),
          fetch(`/api/resources?videoId=${videoId}&courseId=${courseId}`),
          fetch(`/api/comments?videoId=${videoId}&courseId=${courseId}`)
        ]);

        if (!videoRes.ok || !resourcesRes.ok || !commentsRes.ok) {
          throw new Error('Error fetching video data');
        }

        const [video, resources, comments] = await Promise.all([
          videoRes.json(),
          resourcesRes.json(),
          commentsRes.json()
        ]);

        setData({
          video,
          resources,
          comments
        });
      } catch (err) {
        console.error('Error:', err);
        setError('Error al cargar los datos del video');
        toast.error('Error al cargar los datos del video');
      } finally {
        setIsLoading(false);
      }
    };

    if (videoId && courseId) {
      fetchVideoData();
    }
  }, [videoId, courseId]);

  const updateProgress = async (progress: number) => {
    try {
      const response = await fetch(`/api/videos/${videoId}/progress`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ progress, courseId }),
      });

      if (!response.ok) throw new Error('Error updating progress');

      setData(prev => prev ? {
        ...prev,
        video: {
          ...prev.video,
          progress
        }
      } : null);
    } catch (err) {
      console.error('Error:', err);
      toast.error('Error al actualizar el progreso');
    }
  };

  const addComment = async (content: string) => {
    try {
      const response = await fetch('/api/comments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          videoId,
          courseId,
        }),
      });

      if (!response.ok) throw new Error('Error adding comment');

      const newComment = await response.json();
      setData(prev => prev ? {
        ...prev,
        comments: [newComment, ...prev.comments]
      } : null);
    } catch (err) {
      console.error('Error:', err);
      toast.error('Error al agregar el comentario');
    }
  };

  const addResource = async (resource: { title: string; type: "file" | "reading"; url: string }) => {
    try {
      const response = await fetch('/api/resources', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...resource,
          videoId,
          courseId,
        }),
      });

      if (!response.ok) throw new Error('Error adding resource');

      const newResource = await response.json();
      setData(prev => prev ? {
        ...prev,
        resources: [...prev.resources, newResource]
      } : null);
    } catch (err) {
      console.error('Error:', err);
      toast.error('Error al agregar el recurso');
    }
  };

  return {
    data,
    isLoading,
    error,
    updateProgress,
    addComment,
    addResource,
  };
} 