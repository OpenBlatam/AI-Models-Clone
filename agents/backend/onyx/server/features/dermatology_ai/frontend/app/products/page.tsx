'use client';

import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { ProductInfo, ProductSearchParams } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Search, ShoppingBag, Star } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ProductsPage() {
  const [products, setProducts] = useState<ProductInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const categories = [
    'cleanser',
    'moisturizer',
    'serum',
    'sunscreen',
    'toner',
    'exfoliant',
    'mask',
    'eye_cream',
  ];

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Por favor ingresa un término de búsqueda');
      return;
    }

    setIsLoading(true);
    try {
      const params: ProductSearchParams = {
        query: searchQuery,
        category: selectedCategory || undefined,
        limit: 20,
      };
      const response = await apiClient.searchProducts(params);
      setProducts(response.products || []);
      if (response.products.length === 0) {
        toast.info('No se encontraron productos');
      }
    } catch (error: any) {
      toast.error(error.message || 'Error al buscar productos');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <ShoppingBag className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Productos de Skincare</h1>
          </div>
          <p className="text-gray-600">
            Busca y compara productos recomendados para tu tipo de piel
          </p>
        </div>

        {/* Search Section */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      placeholder="Buscar productos..."
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="md:w-48">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">Todas las categorías</option>
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat.charAt(0).toUpperCase() + cat.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <Button onClick={handleSearch} isLoading={isLoading}>
                  Buscar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Products Grid */}
        {products.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <Card key={product.product_id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                      {product.name}
                    </h3>
                    <p className="text-sm text-gray-600">{product.brand}</p>
                  </div>

                  <div className="mb-4">
                    <span className="inline-block px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                      {product.category}
                    </span>
                  </div>

                  <p className="text-sm text-gray-700 mb-4 line-clamp-3">
                    {product.description}
                  </p>

                  {product.ingredients && product.ingredients.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-medium text-gray-600 mb-2">
                        Ingredientes principales:
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {product.ingredients.slice(0, 3).map((ingredient, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                          >
                            {ingredient}
                          </span>
                        ))}
                        {product.ingredients.length > 3 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                            +{product.ingredients.length - 3} más
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div>
                      <p className="text-lg font-bold text-gray-900">
                        ${product.price?.toFixed(2) || 'N/A'}
                      </p>
                      {product.rating && (
                        <div className="flex items-center space-x-1 mt-1">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span className="text-sm text-gray-600">
                            {product.rating.toFixed(1)}
                            {product.reviews_count && ` (${product.reviews_count})`}
                          </span>
                        </div>
                      )}
                    </div>
                    <Button size="sm" variant="outline">
                      Ver Detalles
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          !isLoading && (
            <Card className="p-12 text-center">
              <ShoppingBag className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                No hay productos
              </h3>
              <p className="text-gray-500">
                Busca productos usando el formulario de arriba
              </p>
            </Card>
          )
        )}

        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Buscando productos...</p>
          </div>
        )}
      </div>
    </div>
  );
}

