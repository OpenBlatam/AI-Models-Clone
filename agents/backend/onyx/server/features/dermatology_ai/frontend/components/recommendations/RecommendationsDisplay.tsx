'use client';

import React from 'react';
import { Recommendations } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Sparkles, Sun, Moon, Calendar } from 'lucide-react';

interface RecommendationsDisplayProps {
  recommendations: Recommendations;
}

export const RecommendationsDisplay: React.FC<RecommendationsDisplayProps> = ({
  recommendations,
}) => {
  const { routine, specific_recommendations, tips, priority_areas } = recommendations;

  const RoutineSection: React.FC<{
    title: string;
    icon: React.ReactNode;
    products: typeof routine.morning;
  }> = ({ title, icon, products }) => (
    <Card>
      <CardHeader>
        <div className="flex items-center space-x-2">
          {icon}
          <CardTitle>{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {products.map((product, index) => (
            <div
              key={index}
              className="p-4 bg-gray-50 rounded-lg border-l-4 border-primary-500"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold text-gray-900">{product.name}</h4>
                  <p className="text-sm text-gray-600 capitalize">{product.category}</p>
                </div>
                <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                  Prioridad {product.priority}
                </span>
              </div>
              <p className="text-sm text-gray-700 mb-2">{product.description}</p>
              {product.key_ingredients && product.key_ingredients.length > 0 && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-gray-600 mb-1">
                    Ingredientes clave:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {product.key_ingredients.map((ingredient, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-white text-gray-700 text-xs rounded border"
                      >
                        {ingredient}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {product.usage_frequency && (
                <p className="text-xs text-gray-500">
                  <Calendar className="inline h-3 w-3 mr-1" />
                  {product.usage_frequency}
                </p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Routine */}
      <div className="space-y-4">
        <RoutineSection
          title="Rutina de la Mañana"
          icon={<Sun className="h-5 w-5 text-yellow-500" />}
          products={routine.morning}
        />
        <RoutineSection
          title="Rutina de la Noche"
          icon={<Moon className="h-5 w-5 text-blue-500" />}
          products={routine.evening}
        />
        {routine.weekly && routine.weekly.length > 0 && (
          <RoutineSection
            title="Tratamientos Semanales"
            icon={<Calendar className="h-5 w-5 text-purple-500" />}
            products={routine.weekly}
          />
        )}
      </div>

      {/* Specific Recommendations */}
      {specific_recommendations && specific_recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-primary-600" />
              <CardTitle>Recomendaciones Específicas</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {specific_recommendations.map((rec, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-primary-600 mt-1">•</span>
                  <span className="text-gray-700">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Tips */}
      {tips && tips.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Consejos Personalizados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {tips.map((tip, index) => (
                <div
                  key={index}
                  className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded"
                >
                  <p className="text-gray-700">{tip}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Priority Areas */}
      {priority_areas && priority_areas.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Áreas de Enfoque</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {priority_areas.map((area, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                >
                  {area}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

