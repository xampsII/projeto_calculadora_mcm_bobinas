import React, { useState } from 'react';
import { Plus, Edit2, Trash2, Save, X, Package, Info } from 'lucide-react';
import { useApp } from '../context/AppContext';
import NotificationToast from './NotificationToast';

const CrudMateriasPrimas: React.FC = () => {
  const { materiasPrimas, unidadesMedida, adicionarMateriaPrima, atualizarMateriaPrima, excluirMateriaPrima } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [formData, setFormData] = useState({
    nome: '',
    unidadeCompra: '',
    unidadeUso: '',
    fatorConversao: '1',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const resetForm = () => {
    setFormData({
      nome: '',
      unidadeCompra: '',
      unidadeUso: '',
      fatorConversao: '1',
    });
    setErrors({});
    setShowForm(false);
    setEditingId(null);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) newErrors.nome = 'Nome é obrigatório';
    if (!formData.unidadeCompra) newErrors.unidadeCompra = 'Unidade de compra é obrigatória';
    if (!formData.unidadeUso) newErrors.unidadeUso = 'Unidade de uso é obrigatória';
    if (!formData.fatorConversao || parseFloat(formData.fatorConversao) <= 0) {
      newErrors.fatorConversao = 'Fator de conversão deve ser maior que zero';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: string, value: string) => {
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
        unidadeCompra: formData.unidadeCompra,
        unidadeUso: formData.unidadeUso,
        fatorConversao: parseFloat(formData.fatorConversao),
        ativo: true,
      };

      let result;
      if (editingId) {
        result = await atualizarMateriaPrima(editingId, data);
      } else {
        result = await adicionarMateriaPrima(data);
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

  const handleEdit = (materia: any) => {
    setFormData({
      nome: materia.nome,
      unidadeCompra: materia.unidadeCompra,
      unidadeUso: materia.unidadeUso,
      fatorConversao: materia.fatorConversao.toString(),
    });
    setEditingId(materia.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string, nome: string) => {
    if (!confirm(`Tem certeza que deseja excluir "${nome}"?`)) return;

    setLoading(true);
    try {
      const result = await excluirMateriaPrima(id);
      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });
    } catch (error) {
      setNotification({
        message: 'Erro ao excluir matéria-prima.',
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
      <div className="bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-700">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Package className="h-6 w-6 text-red-500" />
            <h2 className="text-xl font-semibold text-white">
              Gerenciar Matérias-Primas
            </h2>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="h-4 w-4" />
            <span>Nova Matéria-Prima</span>
          </button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-700">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-white">
              {editingId ? 'Editar Matéria-Prima' : 'Nova Matéria-Prima'}
            </h3>
            <button
              onClick={resetForm}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Nome */}
              <div className="md:col-span-2">
                <label htmlFor="nome" className="block text-sm font-medium text-gray-300 mb-2">
                  Nome da Matéria-Prima *
                </label>
                <input
                  type="text"
                  id="nome"
                  value={formData.nome}
                  onChange={(e) => handleInputChange('nome', e.target.value)}
                  placeholder="Ex: Aço Carbono 1020"
                  className={`w-full px-3 py-2 bg-gray-700 border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-white placeholder-gray-400 ${
                    errors.nome ? 'border-red-500' : 'border-gray-600'
                  }`}
                />
                {errors.nome && (
                  <p className="mt-1 text-sm text-red-600">{errors.nome}</p>
                )}
              </div>

              {/* Unidade de Compra */}
              <div>
                <label htmlFor="unidadeCompra" className="block text-sm font-medium text-gray-300 mb-2">
                  Unidade de Compra *
                </label>
                <select
                  id="unidadeCompra"
                  value={formData.unidadeCompra}
                  onChange={(e) => handleInputChange('unidadeCompra', e.target.value)}
                  className={`w-full px-3 py-2 bg-gray-700 border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-white ${
                    errors.unidadeCompra ? 'border-red-500' : 'border-gray-600'
                  }`}
                >
                  <option value="">Selecione a unidade</option>
                  {unidadesMedida.map((unidade) => (
                    <option key={unidade.id} value={unidade.sigla}>
                      {unidade.nome} ({unidade.sigla})
                    </option>
                  ))}
                </select>
                {errors.unidadeCompra && (
                  <p className="mt-1 text-sm text-red-600">{errors.unidadeCompra}</p>
                )}
              </div>

              {/* Unidade de Uso */}
              <div>
                <label htmlFor="unidadeUso" className="block text-sm font-medium text-gray-300 mb-2">
                  Unidade de Uso Interno *
                </label>
                <select
                  id="unidadeUso"
                  value={formData.unidadeUso}
                  onChange={(e) => handleInputChange('unidadeUso', e.target.value)}
                  className={`w-full px-3 py-2 bg-gray-700 border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-white ${
                    errors.unidadeUso ? 'border-red-500' : 'border-gray-600'
                  }`}
                >
                  <option value="">Selecione a unidade</option>
                  {unidadesMedida.map((unidade) => (
                    <option key={unidade.id} value={unidade.sigla}>
                      {unidade.nome} ({unidade.sigla})
                    </option>
                  ))}
                </select>
                {errors.unidadeUso && (
                  <p className="mt-1 text-sm text-red-600">{errors.unidadeUso}</p>
                )}
              </div>

              {/* Fator de Conversão */}
              <div className="md:col-span-2">
                <label htmlFor="fatorConversao" className="block text-sm font-medium text-gray-300 mb-2">
                  Fator de Conversão *
                  <span className="text-gray-400 font-normal ml-2">
                    (Quantas unidades de uso em 1 unidade de compra)
                  </span>
                </label>
                <input
                  type="number"
                  id="fatorConversao"
                  step="0.0001"
                  min="0.0001"
                  value={formData.fatorConversao}
                  onChange={(e) => handleInputChange('fatorConversao', e.target.value)}
                  placeholder="1"
                  className={`w-full px-3 py-2 bg-gray-700 border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-white placeholder-gray-400 ${
                    errors.fatorConversao ? 'border-red-500' : 'border-gray-600'
                  }`}
                />
                {errors.fatorConversao && (
                  <p className="mt-1 text-sm text-red-600">{errors.fatorConversao}</p>
                )}
                
                {/* Exemplo de conversão */}
                {formData.unidadeCompra && formData.unidadeUso && formData.fatorConversao && (
                  <div className="mt-2 p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <Info className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
                      <div className="text-sm text-red-200">
                        <div>
                          <strong>Conversão:</strong> 1 {formData.unidadeCompra} = {formData.fatorConversao} {formData.unidadeUso}
                        </div>
                        <div className="text-red-300">
                          💡 <strong>Exemplo:</strong> Se comprar por R$ 10,00/{formData.unidadeCompra}, o custo será <strong>R$ {(10 / parseFloat(formData.fatorConversao || '1')).toFixed(6)}/{formData.unidadeUso}</strong>
                        </div>
                        <div className="text-red-400 text-xs">
                          ✅ Sempre use a <strong>menor unidade de medida</strong> para controle preciso de custos
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-600 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
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
      <div className="bg-gray-800 rounded-lg shadow-sm overflow-hidden border border-gray-700">
        {materiasPrimas.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Unidade Compra
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Unidade Uso
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Fator Conversão
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {materiasPrimas.map((materia) => (
                  <tr key={materia.id} className="hover:bg-gray-700 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white">{materia.nome}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {materia.unidadeCompra}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {materia.unidadeUso}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      <div>
                        <span className="font-medium text-white">{materia.fatorConversao}</span>
                        <div className="text-xs text-gray-400">
                          1 {materia.unidadeCompra} = {materia.fatorConversao} {materia.unidadeUso}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(materia)}
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                          title="Editar"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(materia.id, materia.nome)}
                          className="text-red-400 hover:text-red-300 transition-colors"
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
            <Package className="mx-auto h-12 w-12 text-gray-500 mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">
              Nenhuma matéria-prima cadastrada
            </h3>
            <p className="text-gray-400 mb-4">
              Comece adicionando sua primeira matéria-prima.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-4 py-2 rounded-lg font-medium transition-all shadow-lg hover:shadow-xl"
            >
              Adicionar Matéria-Prima
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CrudMateriasPrimas;