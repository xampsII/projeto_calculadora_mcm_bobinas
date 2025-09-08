import React, { useState } from 'react';
import { Plus, Edit2, Trash2, Save, X, ShoppingCart, Tag, Package, Calculator } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { ProdutoComponente } from '../types';
import { formatCurrency } from '../utils/formatters';
import NotificationToast from './NotificationToast';

const CrudProdutos: React.FC = () => {
  const { 
    produtosFinais, 
    materiasPrimas, 
    unidadesMedida, 
    adicionarProdutoFinal, 
    atualizarProdutoFinal, 
    excluirProdutoFinal 
  } = useApp();
  
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [formData, setFormData] = useState({
    nome: '',
    idUnico: '',
    componentes: [] as ProdutoComponente[],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const resetForm = () => {
    setFormData({
      nome: '',
      idUnico: '',
      componentes: [],
    });
    setErrors({});
    setShowForm(false);
    setEditingId(null);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) newErrors.nome = 'Nome é obrigatório';
    if (!formData.idUnico.trim()) newErrors.idUnico = 'ID único é obrigatório';

    // Validar componentes
    formData.componentes.forEach((componente, index) => {
      if (!componente.materiaPrimaNome.trim()) {
        newErrors[`componente-${index}-materiaPrimaNome`] = 'Matéria-prima é obrigatória';
      }
      if (!componente.quantidade || componente.quantidade <= 0) {
        newErrors[`componente-${index}-quantidade`] = 'Quantidade deve ser maior que zero';
      }
      if (!componente.unidadeMedida.trim()) {
        newErrors[`componente-${index}-unidadeMedida`] = 'Unidade de medida é obrigatória';
      }
    });

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

  const handleComponentChange = (index: number, field: keyof ProdutoComponente, value: string | number) => {
    const newComponents = [...formData.componentes];
    newComponents[index] = { 
      ...newComponents[index], 
      [field]: field === 'quantidade' ? Number(value) : value 
    };

    // Se mudou a matéria-prima, buscar a matéria-prima correspondente para pegar dados adicionais
    if (field === 'materiaPrimaNome') {
      const materiaPrima = materiasPrimas.find(m => m.nome === value);
      if (materiaPrima) {
        newComponents[index].materiaPrimaId = materiaPrima.id;
        newComponents[index].unidadeMedida = materiaPrima.unidadeUso; // Usar a unidade de uso da MP
      }
    }

    setFormData(prev => ({ ...prev, componentes: newComponents }));
    
    // Limpar erro se existir
    const errorKey = `componente-${index}-${field}`;
    if (errors[errorKey]) {
      setErrors(prev => ({ ...prev, [errorKey]: '' }));
    }
  };

  const handleAddComponent = () => {
    const newComponent: ProdutoComponente = {
      id: Date.now().toString(),
      materiaPrimaNome: '',
      quantidade: 0,
      unidadeMedida: '',
    };
    
    setFormData(prev => ({
      ...prev,
      componentes: [...prev.componentes, newComponent]
    }));
  };

  const handleRemoveComponent = (index: number) => {
    const newComponents = formData.componentes.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, componentes: newComponents }));
    
    // Limpar erros relacionados ao componente removido
    const newErrors = { ...errors };
    Object.keys(newErrors).forEach(key => {
      if (key.startsWith(`componente-${index}-`)) {
        delete newErrors[key];
      }
    });
    setErrors(newErrors);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      const data = {
        nome: formData.nome.trim(),
        idUnico: formData.idUnico.trim(),
        componentes: formData.componentes,
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
      componentes: produto.componentes || [],
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

  const calcularCustoEstimado = (componentes: ProdutoComponente[]) => {
    // Placeholder para cálculo futuro - será implementado no backend
    return componentes.length > 0 ? 'Aguardando cálculo' : 'N/A';
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
            <ShoppingCart className="h-6 w-6 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Gerenciar Produtos Finais
            </h2>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="h-4 w-4" />
            <span>Novo Produto</span>
          </button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
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
            {/* Dados Básicos */}
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
                  placeholder="Ex: Válvula Esfera 1/2\"
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                    errors.nome ? 'border-red-500' : 'border-gray-300'
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
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                    errors.idUnico ? 'border-red-500' : 'border-gray-300'
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

            {/* Composição do Produto */}
            <div className="border-t border-gray-200 pt-6">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
                  <Package className="h-5 w-5 text-red-600" />
                  <span>Composição do Produto</span>
                </h4>
                <button
                  type="button"
                  onClick={handleAddComponent}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded-md text-sm flex items-center space-x-1 transition-colors"
                >
                  <Plus className="h-4 w-4" />
                  <span>Adicionar Componente</span>
                </button>
              </div>

              {formData.componentes.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Matéria-Prima *
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Quantidade *
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Unidade
                        </th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Custo Estimado
                        </th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          Ações
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {formData.componentes.map((componente, index) => (
                        <tr key={componente.id}>
                          <td className="px-4 py-2">
                            <select
                              value={componente.materiaPrimaNome}
                              onChange={(e) => handleComponentChange(index, 'materiaPrimaNome', e.target.value)}
                              className={`w-full px-2 py-1 bg-white border rounded-md text-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-gray-900 ${
                                errors[`componente-${index}-materiaPrimaNome`] ? 'border-red-500' : 'border-gray-300'
                              }`}
                            >
                              <option value="">Selecione a matéria-prima</option>
                              {materiasPrimas.map((mp) => (
                                <option key={mp.id} value={mp.nome}>
                                  {mp.nome}
                                </option>
                              ))}
                            </select>
                            {errors[`componente-${index}-materiaPrimaNome`] && (
                              <p className="mt-1 text-xs text-red-600">{errors[`componente-${index}-materiaPrimaNome`]}</p>
                            )}
                          </td>
                          <td className="px-4 py-2">
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              value={componente.quantidade}
                              onChange={(e) => handleComponentChange(index, 'quantidade', e.target.value)}
                              placeholder="0.00"
                              className={`w-full px-2 py-1 bg-white border rounded-md text-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                                errors[`componente-${index}-quantidade`] ? 'border-red-500' : 'border-gray-300'
                              }`}
                            />
                            {errors[`componente-${index}-quantidade`] && (
                              <p className="mt-1 text-xs text-red-600">{errors[`componente-${index}-quantidade`]}</p>
                            )}
                          </td>
                          <td className="px-4 py-2">
                            <input
                              type="text"
                              value={componente.unidadeMedida}
                              readOnly
                              className="w-full px-2 py-1 bg-gray-100 border border-gray-300 rounded-md text-sm text-gray-600"
                              placeholder="Auto"
                            />
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-500">
                            Aguardando cálculo
                          </td>
                          <td className="px-4 py-2 text-right">
                            <button
                              type="button"
                              onClick={() => handleRemoveComponent(index)}
                              className="text-red-600 hover:text-red-800 transition-colors"
                              title="Remover componente"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <Package className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                  <p className="text-gray-600">Nenhum componente adicionado</p>
                  <p className="text-sm text-gray-500">Clique em "Adicionar Componente" para começar</p>
                </div>
              )}

              {/* Resumo do Custo */}
              {formData.componentes.length > 0 && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Calculator className="h-5 w-5 text-red-600" />
                    <h5 className="font-medium text-red-800">Resumo de Custos</h5>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-red-700 font-medium">Total de Componentes:</span>
                      <p className="text-red-900 font-semibold">{formData.componentes.length}</p>
                    </div>
                    <div>
                      <span className="text-red-700 font-medium">Custo Total Estimado:</span>
                      <p className="text-red-900 font-semibold">{calcularCustoEstimado(formData.componentes)}</p>
                    </div>
                    <div>
                      <span className="text-red-700 font-medium">Status:</span>
                      <p className="text-red-900">Será calculado após salvar</p>
                    </div>
                  </div>
                </div>
              )}
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
                className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
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
      <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
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
                    Componentes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Custo Calculado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Variação
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
                        <Tag className="h-4 w-4 text-red-500 mr-2" />
                        <span className="text-sm font-mono text-red-600 bg-red-50 px-2 py-1 rounded">
                          {produto.idUnico}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <Package className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{produto.componentes?.length || 0} componente{(produto.componentes?.length || 0) !== 1 ? 's' : ''}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <Calculator className="h-4 w-4 text-gray-400 mr-2" />
                        <span>Aguardando cálculo</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      N/A
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
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-all shadow-lg hover:shadow-xl"
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