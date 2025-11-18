'use client';

import { useState } from 'react';
import { MessageSquare, Send, Star, AlertCircle } from 'lucide-react';
import { toast } from '@/lib/utils/toast';

type FeedbackType = 'bug' | 'feature' | 'improvement' | 'other';

export default function FeedbackPanel() {
  const [feedbackType, setFeedbackType] = useState<FeedbackType>('feature');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [rating, setRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!title.trim() || !description.trim()) {
      toast.error('Por favor completa todos los campos');
      return;
    }

    setIsSubmitting(true);
    try {
      // Simulate feedback submission
      await new Promise((resolve) => setTimeout(resolve, 2000));
      toast.success('¡Gracias por tu feedback!');
      setTitle('');
      setDescription('');
      setRating(0);
    } catch (error: any) {
      toast.error(`Error: ${error.message || 'Failed to submit feedback'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-6">
          <MessageSquare className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Enviar Feedback</h3>
        </div>

        {/* Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tipo de Feedback
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {(['bug', 'feature', 'improvement', 'other'] as FeedbackType[]).map((type) => (
              <button
                key={type}
                onClick={() => setFeedbackType(type)}
                className={`p-3 rounded-lg border-2 transition-colors ${
                  feedbackType === type
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-gray-600 bg-gray-700/50 hover:border-gray-500'
                }`}
              >
                <p className="text-sm text-white capitalize">{type}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Rating */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Calificación
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                onClick={() => setRating(star)}
                className="p-2 hover:scale-110 transition-transform"
              >
                <Star
                  className={`w-6 h-6 ${
                    star <= rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-400'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Title */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Título
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Resumen breve..."
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Description */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Descripción
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe tu feedback en detalle..."
            rows={6}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          />
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={isSubmitting || !title.trim() || !description.trim()}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
          {isSubmitting ? 'Enviando...' : 'Enviar Feedback'}
        </button>

        {/* Info */}
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/50 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
            <div>
              <p className="text-sm text-blue-400 font-medium mb-1">Información</p>
              <p className="text-xs text-gray-300">
                Tu feedback es muy valioso para nosotros. Revisaremos cada sugerencia y la
                consideraremos para futuras actualizaciones.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


