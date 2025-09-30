import React, { useState, useEffect } from 'react';
import { Search, Filter, Plus, Eye, Edit2, Calendar, Building, FileText, Pin } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { NotaFiscalFilters, NotaFiscal } from '../types';
import { formatCurrency, formatDate, formatCNPJ } from '../utils/formatters';
import Pagination from './ui/Pagination';
import LoadingSpinner from './ui/LoadingSpinner';
import EmptyState from './ui/EmptyState';
import NotificationToast from './NotificationToast';

interface NotaFiscalListProps {
  onNovaNota: () => void;
  onEditarNota: (id: string) => void;
  onVerNota: (id: string) => void;
}

const NotaFiscalList: React.FC<NotaFiscalListProps> = ({ onNovaNota, onEditarNota, onVerNota }) => {
  const { buscarNotasFiscais } = useApp();
  const [notas, setNotas] = useState<NotaFiscal[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [filters, setFilters] = useState<NotaFiscalFilters>({
    busca: '',
    fornecedor: '',
    materiaPrima: '',
    dataInicio: '',
    dataFim: '',
    sortBy: 'dataEmissao',
    sortOrder: 'desc',
  });

  const [showFilters, setShowFilters] = useState(false);

  const handleTogglePin = async (notaId: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/notas/${notaId}/pin`, {
        method: 'PATCH',
      });
      if (response.ok) {
        loadNotas(); // Recarregar lista
        setNotification({
          message: 'Status de fixação alterado com sucesso!',
          type: 'success'
        });
      }
    } catch (error) {
      console.error('Erro ao fixar nota:', error);
      setNotification({
        message: 'Erro ao alterar status de fixação.',
        type: 'error'
      });
    }
  };

  const loadNotas = async () => {
    setLoading(true);
    try {
      const result = await buscarNotasFiscais({
        ...filters,
        page: currentPage,
        limit: itemsPerPage,
      });
      setNotas(result.data);
      setTotal(result.total);
    } catch (error) {
      setNotification({
        message: 'Erro ao carregar notas fiscais.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotas();
  }, [currentPage, itemsPerPage, filters]);

  const handleFilterChange = (field: keyof NotaFiscalFilters, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setCurrentPage(1);
  };

  const handleSort = (field: 'dataEmissao' | 'valorTotal') => {
    const newOrder = filters.sortBy === field && filters.sortOrder === 'desc' ? 'asc' : 'desc';
    setFilters(prev => ({ ...prev, sortBy: field, sortOrder: newOrder }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      busca: '',
      fornecedor: '',
      materiaPrima: '',
      dataInicio: '',
      dataFim: '',
      sortBy: 'dataEmissao',
      sortOrder: 'desc',
    });
    setCurrentPage(1);
  };

  const getSortIcon = (field: 'dataEmissao' | 'valorTotal') => {
    if (filters.sortBy !== field) return '↕️';
    return filters.sortOrder === 'asc' ? '↑' : '↓';
  };

  return (
    <div className="space-y-6">
      {notification && (
        <NotificationToast
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900">Notas Fiscais</h2>
          </div>
          <button
            onClick={onNovaNota}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="h-4 w-4" />
            <span>Nova Nota</span>
          </button>
        </div>
      </div>

      {/* Busca e Filtros */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="space-y-4">
          {/* Barra de busca principal */}
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
              <input
                type="text"
                placeholder="Buscar por fornecedor, CNPJ ou número da nota..."
                value={filters.busca || ''}
                onChange={(e) => handleFilterChange('busca', e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-red-600 focus:border-red-600"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-4 py-2 rounded-lg border transition-colors flex items-center space-x-2 ${
                showFilters
                  ? 'bg-red-600 border-red-600 text-white'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Filter className="h-4 w-4" />
              <span>Filtros</span>
            </button>
          </div>

          {/* Filtros avançados */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fornecedor
                </label>
                <input
                  type="text"
                  placeholder="Nome do fornecedor"
                  value={filters.fornecedor || ''}
                  onChange={(e) => handleFilterChange('fornecedor', e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-red-600 focus:border-red-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Matéria-prima
                </label>
                <input
                  type="text"
                  placeholder="Nome da matéria-prima"
                  value={filters.materiaPrima || ''}
                  onChange={(e) => handleFilterChange('materiaPrima', e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-red-600 focus:border-red-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data início
                </label>
                <input
                  type="date"
                  value={filters.dataInicio || ''}
                  onChange={(e) => handleFilterChange('dataInicio', e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-red-600 focus:border-red-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data fim
                </label>
                <input
                  type="date"
                  value={filters.dataFim || ''}
                  onChange={(e) => handleFilterChange('dataFim', e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 focus:ring-2 focus:ring-red-600 focus:border-red-600"
                />
              </div>
              <div className="lg:col-span-4 flex justify-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Limpar filtros
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
        {loading ? (
          <LoadingSpinner text="Carregando notas fiscais..." />
        ) : Array.isArray(notas) && notas.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nº Nota
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fornecedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CNPJ
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => handleSort('dataEmissao')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Emissão</span>
                        <span className="text-red-600">{getSortIcon('dataEmissao')}</span>
                      </div>
                    </th>
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => handleSort('valorTotal')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Valor Total</span>
                        <span className="text-red-600">{getSortIcon('valorTotal')}</span>
                      </div>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Qtde Itens
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {(notas ?? []).map((nota) => (
                    <tr key={nota.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{nota.numeroNota}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Building className="h-4 w-4 text-gray-500 mr-2" />
                          <div className="text-sm text-gray-900">{nota.fornecedorNome}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {nota.cnpjFornecedor ? formatCNPJ(nota.cnpjFornecedor) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 text-gray-500 mr-2" />
                          <div className="text-sm text-gray-900">{formatDate(nota.dataEmissao)}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(nota.valorTotal)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {nota.itens ? nota.itens.length : 0} {nota.itens && nota.itens.length === 1 ? 'item' : 'itens'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => handleTogglePin(nota.id)}
                            className={`${nota.is_pinned ? 'text-yellow-600' : 'text-gray-400'} hover:text-yellow-800 transition-colors`}
                            title={nota.is_pinned ? "Desafixar" : "Fixar"}
                          >
                            <Pin className="h-4 w-4" fill={nota.is_pinned ? 'currentColor' : 'none'} />
                          </button>
                          <button
                            onClick={() => onVerNota(nota.id)}
                            className="text-blue-600 hover:text-blue-800 transition-colors"
                            title="Ver detalhes"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => onEditarNota(nota.id)}
                            className="text-green-600 hover:text-green-800 transition-colors"
                            title="Editar"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(total / itemsPerPage)}
              onPageChange={setCurrentPage}
              itemsPerPage={itemsPerPage}
              onItemsPerPageChange={setItemsPerPage}
              totalItems={total}
            />
          </>
        ) : (
          <EmptyState
            icon={FileText}
            title="Nenhuma nota fiscal encontrada"
            description="Não há notas fiscais cadastradas ou que correspondam aos filtros aplicados."
            action={{
              label: "Cadastrar primeira nota",
              onClick: onNovaNota,
            }}
          />
        )}
      </div>
    </div>
  );
};

export default NotaFiscalList;