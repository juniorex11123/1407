import React, { useState } from 'react';
import { authAPI } from '../services/api';

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await authAPI.login(username, password);
      
      if (result.access_token && result.user) {
        onLogin(result.user, result.access_token);
      } else {
        setError('Błędne dane logowania');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.response?.status === 401) {
        setError('Błędne dane logowania');
      } else {
        setError('Błąd połączenia z serwerem');
      }
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            System Ewidencji
          </h1>
          <p className="text-gray-600">Czasu Pracy</p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Nazwa użytkownika
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Hasło
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200"
          >
            {loading ? 'Logowanie...' : 'Zaloguj się'}
          </button>
        </form>

        {/* Demo credentials */}
        <div className="mt-8 space-y-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">
              🧪 Demo Credentials
            </h3>
            <div className="text-xs text-blue-700 space-y-1">
              <p><strong>Owner:</strong> owner / owner123</p>
              <p><strong>Admin:</strong> admin / admin123</p>
              <p><strong>User:</strong> user / user123</p>
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-green-800 mb-2">
              🏢 System Multi-Firm
            </h3>
            <div className="text-xs text-green-700 space-y-1">
              <p>• Właściciele systemu mogą zarządzać wszystkimi firmami</p>
              <p>• Administratorzy firm mogą zarządzać pracownikami</p>
              <p>• Użytkownicy mogą skanować kody QR</p>
              <p>• Każda firma ma własnych administratorów i użytkowników</p>
              <p>• Dane firm są całkowicie oddzielone</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;