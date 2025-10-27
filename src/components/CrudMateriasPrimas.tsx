import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Save, X, Package, Info } from 'lucide-react';
import { useApp } from '../context/AppContext';
import NotificationToast from './NotificationToast';

const UNIDADES_BOBINA = [
  { value: 'kg', label: 'Quilo (kg)' },
  { value: 'g', label: 'Grama (g)' },
  { value: 'm', label: 'Metro (m)' },
  { value: 'mm', label: 'Milímetro (mm)' },
  { value: 'cm', label: 'Centímetro (cm)' },
  { value: 'rolo', label: 'Rolo' },
  { value: 'bobina', label: 'Bobina' },
  { value: 'folha', label: 'Folha' },
  { value: 'peça', label: 'Peça' },
  { value: 'pacote', label: 'Pacote' },
  { value: 'caixa', label: 'Caixa' },
  { value: 'un', label: 'Unidade (un)' },
  { value: 'l', label: 'Litro (l)' },
  { value: 'ml', label: 'Mililitro (ml)' },
  { value: 'outro', label: 'Outra...' },
];

const CrudMateriasPrimas: React.FC = () => {
  const { materiasPrimas, unidadesMedida, adicionarMateriaPrima, atualizarMateriaPrima, excluirMateriaPrima, carregarMateriasPrimas, buscarHistoricoPrecos } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [historicoPrecos, setHistoricoPrecos] = useState<any>({});

  // Carregar matérias-primas e histórico ao montar o componente
  useEffect(() => {
    carregarMateriasPrimas();
    carregarHistorico();
  }, []);


  const carregarHistorico = async () => {
    const historico = await buscarHistoricoPrecos();
    
    // Transformar o array em um objeto para acesso rápido por ID
    const historicoMap: any = {};
    if (historico && historico.materias_primas) {
      historico.materias_primas.forEach((mp: any) => {
        if (mp.historico && mp.historico.length > 0) {
          const precoAtual = mp.historico[0]; // Mais recente
          const precoAnterior = mp.historico[1]; // Segundo mais recente
          
          historicoMap[mp.materia_prima.id] = {
            valorAtual: precoAtual.valor_unitario,
            vigenteSde: precoAtual.vigente_desde,
            variacao: precoAtual.variacao_percentual || null,
            valorAnterior: precoAnterior ? precoAnterior.valor_unitario : null
          };
        }
      });
    }
    
    setHistoricoPrecos(historicoMap);
  };

  const [formData, setFormData] = useState({
    nome: '',
    unidadeCompra: '',
    unidadeUso: '',
    fatorConversao: '1',
    precoInicial: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [customUnidadeCompra, setCustomUnidadeCompra] = useState('');
  const [customUnidadeUso, setCustomUnidadeUso] = useState('');

  const resetForm = () => {
    setFormData({
      nome: '',
      unidadeCompra: '',
      unidadeUso: '',
      fatorConversao: '1',
      precoInicial: '',
    });
    setErrors({});
    setShowForm(false);
    setEditingId(null);
    setCustomUnidadeCompra('');
    setCustomUnidadeUso('');
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nome.trim()) newErrors.nome = 'Nome é obrigatório';
    if (!formData.unidadeCompra) newErrors.unidadeCompra = 'Unidade de compra é obrigatória';
    if (!formData.unidadeUso) newErrors.unidadeUso = 'Unidade de uso é obrigatória';
    if (!formData.fatorConversao || parseFloat(formData.fatorConversao) <= 0) {
      newErrors.fatorConversao = 'Fator de conversão deve ser maior que zero';
    }
    if (formData.precoInicial && parseFloat(formData.precoInicial) < 0) {
      newErrors.precoInicial = 'Preço não pode ser negativo';
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
      const data: any = {
        nome: formData.nome.trim(),
        unidade_codigo: formData.unidadeCompra,
        menor_unidade_codigo: formData.unidadeUso,
      };

      // Adicionar preço inicial se fornecido
      if (formData.precoInicial && parseFloat(formData.precoInicial) > 0) {
        data.preco_inicial = parseFloat(formData.precoInicial);
      }

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
        carregarHistorico(); // Recarregar histórico após adicionar/editar
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
      unidadeCompra: materia.unidade_codigo || materia.unidadeCompra,
      unidadeUso: materia.menor_unidade_codigo || materia.unidadeUso,
      fatorConversao: "1", // Valor padrão
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
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Package className="h-6 w-6 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Gerenciar Matérias-Primas
            </h2>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="h-4 w-4" />
            <span>Nova Matéria-Prima</span>
          </button>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {editingId ? 'Editar Matéria-Prima' : 'Nova Matéria-Prima'}
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
              <div className="md:col-span-2">
                <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-2">
                  Nome da Matéria-Prima *
                </label>
                <input
                  type="text"
                  id="nome"
                  value={formData.nome}
                  onChange={(e) => handleInputChange('nome', e.target.value)}
                  placeholder="Ex: Aço Carbono 1020"
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                    errors.nome ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.nome && (
                  <p className="mt-1 text-sm text-red-600">{errors.nome}</p>
                )}
              </div>

              {/* Unidade de Compra */}
              <div>
                <label htmlFor="unidadeCompra" className="block text-sm font-medium text-gray-700 mb-2">
                  Unidade de Compra *
                </label>
                <select
                  id="unidadeCompra"
                  value={formData.unidadeCompra}
                  onChange={e => {
                    handleInputChange('unidadeCompra', e.target.value);
                    if (e.target.value !== 'outro') setCustomUnidadeCompra('');
                  }}
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 ${errors.unidadeCompra ? 'border-red-500' : 'border-gray-300'}`}
                >
                  <option value="">Selecione a unidade</option>
                  {UNIDADES_BOBINA.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {formData.unidadeCompra === 'outro' && (
                  <input
                    type="text"
                    className="mt-2 w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
                    placeholder="Digite a unidade personalizada"
                    value={customUnidadeCompra}
                    onChange={e => {
                      setCustomUnidadeCompra(e.target.value);
                      handleInputChange('unidadeCompra', e.target.value);
                    }}
                  />
                )}
                {errors.unidadeCompra && (
                  <p className="mt-1 text-sm text-red-600">{errors.unidadeCompra}</p>
                )}
              </div>

              {/* Unidade de Uso */}
              <div>
                <label htmlFor="unidadeUso" className="block text-sm font-medium text-gray-700 mb-2">
                  Unidade de Uso Interno *
                </label>
                <select
                  id="unidadeUso"
                  value={formData.unidadeUso}
                  onChange={e => {
                    handleInputChange('unidadeUso', e.target.value);
                    if (e.target.value !== 'outro') setCustomUnidadeUso('');
                  }}
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 ${errors.unidadeUso ? 'border-red-500' : 'border-gray-300'}`}
                >
                  <option value="">Selecione a unidade</option>
                  {UNIDADES_BOBINA.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {formData.unidadeUso === 'outro' && (
                  <input
                    type="text"
                    className="mt-2 w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
                    placeholder="Digite a unidade personalizada"
                    value={customUnidadeUso}
                    onChange={e => {
                      setCustomUnidadeUso(e.target.value);
                      handleInputChange('unidadeUso', e.target.value);
                    }}
                  />
                )}
                {errors.unidadeUso && (
                  <p className="mt-1 text-sm text-red-600">{errors.unidadeUso}</p>
                )}
              </div>

              {/* Fator de Conversão */}
              <div className="md:col-span-2">
                <label htmlFor="fatorConversao" className="block text-sm font-medium text-gray-700 mb-2">
                  Fator de Conversão *
                  <span className="text-gray-500 font-normal ml-2">
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
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                    errors.fatorConversao ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.fatorConversao && (
                  <p className="mt-1 text-sm text-red-600">{errors.fatorConversao}</p>
                )}
                
                {/* Exemplo de conversão */}
                {formData.unidadeCompra && formData.unidadeUso && formData.fatorConversao && (
                  <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <Info className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                      <div className="text-sm text-red-800">
                        <div>
                          <strong>Conversão:</strong> 1 {formData.unidadeCompra} = {formData.fatorConversao} {formData.unidadeUso}
                        </div>
                        <div className="text-red-700">
                          💡 <strong>Exemplo:</strong> Se comprar por R$ 10,00/{formData.unidadeCompra}, o custo será <strong>R$ {(10 / parseFloat(formData.fatorConversao || '1')).toFixed(6)}/{formData.unidadeUso}</strong>
                        </div>
                        <div className="text-red-600 text-xs">
                          ✅ Sempre use a <strong>menor unidade de medida</strong> para controle preciso de custos
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Preço Inicial */}
              <div className="md:col-span-2">
                <label htmlFor="precoInicial" className="block text-sm font-medium text-gray-700 mb-2">
                  Preço Inicial (Opcional)
                  <span className="text-gray-500 font-normal ml-2">
                    (Valor unitário em R$/{formData.unidadeCompra || 'unidade de compra'})
                  </span>
                </label>
                <input
                  type="number"
                  id="precoInicial"
                  step="0.01"
                  min="0"
                  value={formData.precoInicial}
                  onChange={(e) => handleInputChange('precoInicial', e.target.value)}
                  placeholder="Ex: 10.50"
                  className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                    errors.precoInicial ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.precoInicial && (
                  <p className="mt-1 text-sm text-red-600">{errors.precoInicial}</p>
                )}
                {formData.precoInicial && parseFloat(formData.precoInicial) > 0 && (
                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-800">
                    <strong>Preço registrado:</strong> R$ {parseFloat(formData.precoInicial).toFixed(2)}/{formData.unidadeCompra || 'un'}
                    {formData.fatorConversao && formData.unidadeUso && (
                      <span className="block text-green-700 mt-1">
                        = R$ {(parseFloat(formData.precoInicial) / parseFloat(formData.fatorConversao)).toFixed(6)}/{formData.unidadeUso}
                      </span>
                    )}
                  </div>
                )}
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
        {materiasPrimas.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unidade Compra
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unidade Uso
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fator Conversão
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Último Preço
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Variação
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {materiasPrimas.map((materia) => (
                  <tr key={materia.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{materia.nome}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {materia.unidade_codigo}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {materia.menor_unidade_codigo || materia.unidade_codigo}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div>
                        <span className="font-medium text-gray-900">1.0</span>
                        <div className="text-xs text-gray-500">
                          1 {materia.unidade_codigo} = 1.0 {materia.menor_unidade_codigo || materia.unidade_codigo}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {historicoPrecos[materia.id] ? (
                        <div>
                          <div className="font-medium text-gray-900">
                            R$ {historicoPrecos[materia.id].valorAtual.toFixed(4).replace('.', ',')}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(historicoPrecos[materia.id].vigenteSde).toLocaleDateString('pt-BR')}
                          </div>
                        </div>
                      ) : (
                        <span className="text-gray-400 italic">Aguardando registro</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {historicoPrecos[materia.id] && historicoPrecos[materia.id].variacao !== null ? (
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          historicoPrecos[materia.id].variacao > 0 
                            ? 'bg-red-100 text-red-800' 
                            : historicoPrecos[materia.id].variacao < 0 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                        }`}>
                          {historicoPrecos[materia.id].variacao > 0 ? '↑' : '↓'} {Math.abs(historicoPrecos[materia.id].variacao).toFixed(2)}%
                        </div>
                      ) : (
                        <span className="text-gray-400 italic">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(materia)}
                          className="text-blue-600 hover:text-blue-900 transition-colors"
                          title="Editar"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(materia.id, materia.nome)}
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
            <Package className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma matéria-prima cadastrada
            </h3>
            <p className="text-gray-600 mb-4">
              Comece adicionando sua primeira matéria-prima.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-all shadow-lg hover:shadow-xl"
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