import React from 'react';
import { History, Upload, Package, Users, ShoppingCart } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: 'cadastro' | 'historico' | 'materias' | 'fornecedores' | 'produtos';
  onTabChange: (tab: 'cadastro' | 'historico' | 'materias' | 'fornecedores' | 'produtos') => void;
}

const Layout: React.FC<LayoutProps> = ({ children, activeTab, onTabChange }) => {
  return (
    <div className="min-h-screen bg-gray-900">
      <header className="bg-gradient-to-r from-black to-gray-900 shadow-lg border-b border-red-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <img 
                src="https://images.pexels.com/photos/6801648/pexels-photo-6801648.jpeg?auto=compress&cs=tinysrgb&w=80&h=80&fit=crop" 
                alt="MCM Bobinas Logo" 
                className="h-10 w-10 rounded-lg object-cover border-2 border-red-500"
              />
              <div>
                <h1 className="text-xl font-bold text-white">
                  MCM Bobinas
                </h1>
                <p className="text-xs text-blue-200">
                  Sistema de Notas Fiscais
                </p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-gray-300 text-sm">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span>Sistema Online</span>
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-gray-800 border-b border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 overflow-x-auto">
            <button
              onClick={() => onTabChange('cadastro')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === 'cadastro'
                  ? 'border-red-500 text-red-400'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Upload className="h-4 w-4" />
                <span>Cadastro de Notas</span>
              </div>
            </button>
            <button
              onClick={() => onTabChange('historico')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === 'historico'
                  ? 'border-red-500 text-red-400'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-2">
                <History className="h-4 w-4" />
                <span>Histórico de Preços</span>
              </div>
            </button>
            <button
              onClick={() => onTabChange('materias')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === 'materias'
                  ? 'border-red-500 text-red-400'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Package className="h-4 w-4" />
                <span>Matérias-Primas</span>
              </div>
            </button>
            <button
              onClick={() => onTabChange('fornecedores')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === 'fornecedores'
                  ? 'border-red-500 text-red-400'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4" />
                <span>Fornecedores</span>
              </div>
            </button>
            <button
              onClick={() => onTabChange('produtos')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === 'produtos'
                  ? 'border-red-500 text-red-400'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-2">
                <ShoppingCart className="h-4 w-4" />
                <span>Produtos</span>
              </div>
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
      
      <footer className="bg-black border-t border-red-600 mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center text-gray-300 text-sm">
            <div className="flex items-center space-x-2">
              <span>© 2024 MCM Bobinas</span>
              <span className="text-red-500">•</span>
              <span>Sistema de Gestão Industrial</span>
            </div>
            <div className="hidden md:block">
              <span>Versão 1.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;