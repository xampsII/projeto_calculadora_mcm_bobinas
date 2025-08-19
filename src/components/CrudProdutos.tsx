import React, { useState } from 'react';
import { Plus, Edit2, Trash2, Save, X, ShoppingCart, Tag } from 'lucide-react';
import { useApp } from '../context/AppContext';
import NotificationToast from './NotificationToast';

const CrudProdutos: React.FC = () => {
  const { produtosFinais, adicionarProdutoFinal, atualizarProdutoFinal, excluirProdutoFinal } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [formData, setFormData] = useState({
    nome: '',
    idUnico: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const resetForm = () => {
    setFormData({
      nome: '',
      idUnico: '',
    });
    setErrors({});
    setShowForm(false);
    setEditingId(null);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) newErrors.nome = 'Nome é obrigatório';
    if (!formData.idUnico.trim()) newErrors.idUnico = 'ID único é obrigatório';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: string, value: string) => {
    if (field === 'idUnico') {
      // Converter para maiúsculo e remover caracteres especiais
      value = value.toUpperCase().replace(/[^A-Z0-9-]/g, '');
    }
    
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      const data = {
        nome: formData.nome.trim(),
        idUnico: formData.idUnico.trim(),
        ativo: true,
      };

      let result;
      if (editingId) {
        result = await atualizarProdutoFinal(editingId, data);
      } else {
        result = await adicionarProdutoFinal(data);
      }

      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });

      if (result.success) {
        resetForm();
      }
    } catch (error) {
      setNotification({
        message: 'Erro inesperado. Tente novamente.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (produto: any) => {
    setFormData({
      nome: produto.nome,
      idUnico: produto.idUnico,
    });
    setEditingId(produto.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string, nome: string) => {
    if (!confirm(`Tem certeza que deseja excluir "${nome}"?`)) return;

    setLoading(true);
    try {
      const result = await excluirProdutoFinal(id);
      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });
    } catch (error) {
      setNotification({
        message: 'Erro ao excluir produto.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
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
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <ShoppingCart className="h-6 w-6 text-orange-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Gerenciar Produtos Finais
            </h2>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="h-4 w-4" />
            <span>Novo Produto</span>
          </button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {editingId ? 'Editar Produto' : 'Novo Produto'}
            </h3>
            <button
              onClick={resetForm}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Nome */}
              <div>
                <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-2">
                  Nome do Produto *
                </label>
                <input
                  type="text"
                  id="nome"
                  value={formData.nome}
                  onChange={(e) => handleInputChange('nome', e.target.value)}
                  placeholder="Ex: Válvula Esfera 1/2&quot;"
                  className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                    errors.nome ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.nome && (
                  <p className="mt-1 text-sm text-red-600">{errors.nome}</p>
                )}
              </div>

              {/* ID Único */}
              <div>
                <label htmlFor="idUnico" className="block text-sm font-medium text-gray-700 mb-2">
                  ID Único da Empresa *
                </label>
                <input
                  type="text"
                  id="idUnico"
                  value={formData.idUnico}
                  onChange={(e) => handleInputChange('idUnico', e.target.value)}
                  placeholder="Ex: VE-001"
                  className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 ${
                    errors.idUnico ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.idUnico && (
                  <p className="mt-1 text-sm text-red-600">{errors.idUnico}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Código interno usado pela sua empresa para identificar este produto
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 disabled:from-gray-400 disabled:to-gray-400 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Salvando...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>{editingId ? 'Atualizar' : 'Salvar'}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {produtosFinais.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID Único
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data Cadastro
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {produtosFinais.map((produto) => (
                  <tr key={produto.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <ShoppingCart className="h-5 w-5 text-gray-400 mr-3" />
                        <div className="text-sm font-medium text-gray-900">{produto.nome}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Tag className="h-4 w-4 text-orange-500 mr-2" />
                        <span className="text-sm font-mono text-orange-600 bg-orange-50 px-2 py-1 rounded">
                          {produto.idUnico}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(produto.createdAt).toLocaleDateString('pt-BR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(produto)}
                          className="text-blue-600 hover:text-blue-900 transition-colors"
                          title="Editar"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(produto.id, produto.nome)}
                          className="text-red-600 hover:text-red-900 transition-colors"
                          title="Excluir"
                          disabled={loading}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-6 py-12 text-center">
            <ShoppingCart className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum produto cadastrado
            </h3>
            <p className="text-gray-600 mb-4">
              Comece adicionando seu primeiro produto final.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white px-4 py-2 rounded-lg font-medium transition-all shadow-lg hover:shadow-xl"
            >
              Adicionar Produto
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CrudProdutos;