'use client';

import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { useAuth } from '@/lib/contexts/AuthContext';
import toast from 'react-hot-toast';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToRegister: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({
  isOpen,
  onClose,
  onSwitchToRegister,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const success = await login(email, password);
    if (success) {
      onClose();
      setEmail('');
      setPassword('');
    }
    setIsLoading(false);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Iniciar Sesión" size="sm">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="tu@email.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contraseña
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="••••••••"
          />
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            ¿No tienes cuenta? Regístrate
          </button>
        </div>

        <div className="flex space-x-3 pt-4">
          <Button
            type="submit"
            isLoading={isLoading}
            className="flex-1"
          >
            Iniciar Sesión
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancelar
          </Button>
        </div>
      </form>
    </Modal>
  );
};

