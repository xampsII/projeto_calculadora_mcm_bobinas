import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, TrendingDown, Minus, Loader2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

interface MateriaPrima {
  id: number;
  nome: string;
  unidade_codigo: string;
}

interface HistoricoPreco {
  id: number;
  valor_unitario: number;
  vigente_desde: string;
  vigente_ate: string | null;
  nota_id: number | null;
  fornecedor: {
    id: number;
    nome: string;
  } | null;
  nota: {
    id: number;
    numero: string;
    serie: string;
  } | null;
  created_at: string;
}

interface HistoricoResponse {
  materia_prima: {
    id: number;
    nome: string;
    unidade: string;
  };
  historico: HistoricoPreco[];
  total_precos: number;
}

const HistoricoPrecos: React.FC = () => {
  const [materiasPrimas, setMateriasPrimas] = useState<MateriaPrima[]>([]);
  const [materiaSelecionada, setMateriaSelecionada] = useState<string>('');
  const [historico, setHistorico] = useState<HistoricoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingHistorico, setLoadingHistorico] = useState(false);

  // Carregar matérias-primas
  const carregarMateriasPrimas = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/produtos-finais/materias-primas-disponiveis`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Converter formato para compatibilidade
      const materiasFormatadas = data.map((item: any) => ({
        id: item.id,
        nome: item.nome,
        unidade_codigo: item.unidade || 'kg'
      }));
      setMateriasPrimas(materiasFormatadas);
    } catch (error) {
      console.error('Erro ao carregar matérias-primas:', error);
    } finally {
      setLoading(false);
    }
  };

  // Carregar histórico de preços
  const carregarHistorico = async (materiaPrimaId: string) => {
    setLoadingHistorico(true);
    try {
      const response = await fetch(`${API_BASE_URL}/notas/materia-prima/${materiaPrimaId}/historico-precos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setHistorico(data);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
      setHistorico(null);
    } finally {
      setLoadingHistorico(false);
    }
  };

  // Carregar matérias-primas ao montar o componente
  useEffect(() => {
    carregarMateriasPrimas();
  }, []);

  // Carregar histórico quando matéria-prima for selecionada
  useEffect(() => {
    if (materiaSelecionada) {
      carregarHistorico(materiaSelecionada);
    } else {
      setHistorico(null);
    }
  }, [materiaSelecionada]);

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  };

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calcularVariacao = (valorAtual: number, valorAnterior?: number) => {
    if (!valorAnterior) return null;
    
    const variacao = ((valorAtual - valorAnterior) / valorAnterior) * 100;
    return variacao;
  };

  const renderTrendIcon = (valorAtual: number, valorAnterior?: number) => {
    const variacao = calcularVariacao(valorAtual, valorAnterior);
    
    if (variacao === null) return <Minus className="h-4 w-4 text-gray-400" />;
    if (variacao > 0) return <TrendingUp className="h-4 w-4 text-red-500" />;
    if (variacao < 0) return <TrendingDown className="h-4 w-4 text-green-500" />;
    return <Minus className="h-4 w-4 text-gray-400" />;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center space-x-3 mb-6">
          <Search className="h-6 w-6 text-red-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            Histórico de Preços por Matéria-Prima
          </h2>
        </div>

        {/* Filtro por matéria-prima */}
        <div className="mb-6">
          <label htmlFor="materia-select" className="block text-sm font-medium text-gray-700 mb-2">
            Selecione a matéria-prima
          </label>
          <div className="relative">
            <select
              id="materia-select"
              value={materiaSelecionada}
              onChange={(e) => setMateriaSelecionada(e.target.value)}
              className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
              disabled={loading}
            >
              <option value="">Escolha uma matéria-prima</option>
              {materiasPrimas.map((materia) => (
                <option key={materia.id} value={materia.id.toString()}>
                  {materia.nome} ({materia.unidade_codigo})
                </option>
              ))}
            </select>
            {loading && (
              <div className="absolute right-3 top-2.5">
                <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
              </div>
            )}
          </div>
        </div>

        {/* Tabela de histórico */}
        {materiaSelecionada && (
          <div className="overflow-hidden border border-gray-200 rounded-lg">
            {loadingHistorico ? (
              <div className="px-6 py-8 text-center">
                <Loader2 className="mx-auto h-8 w-8 animate-spin text-red-600 mb-4" />
                <p className="text-gray-600">Carregando histórico...</p>
              </div>
            ) : historico && historico.historico.length > 0 ? (
              <>
                {/* Header da tabela */}
                <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">
                    Histórico de Preços - {historico.materia_prima.nome}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {historico.total_precos} registro{historico.total_precos !== 1 ? 's' : ''} encontrado{historico.total_precos !== 1 ? 's' : ''}
                  </p>
                </div>

                {/* Tabela */}
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Data de Vigência
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Valor Unitário
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Variação
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Fornecedor
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Nota Fiscal
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {historico.historico.map((item, index) => {
                        const valorAnterior = index < historico.historico.length - 1 
                          ? historico.historico[index + 1].valor_unitario 
                          : undefined;
                        const variacao = calcularVariacao(item.valor_unitario, valorAnterior);
                        
                        return (
                          <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatarData(item.vigente_desde)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {formatarMoeda(item.valor_unitario)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                item.vigente_ate === null 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-gray-100 text-gray-800'
                              }`}>
                                {item.vigente_ate === null ? 'ATUAL' : 'HISTÓRICO'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <div className="flex items-center space-x-2">
                                {renderTrendIcon(item.valor_unitario, valorAnterior)}
                                <span className={`font-medium ${
                                  variacao === null ? 'text-gray-500' :
                                  variacao > 0 ? 'text-red-600' :
                                  variacao < 0 ? 'text-green-600' :
                                  'text-gray-500'
                                }`}>
                                  {variacao === null ? 'Primeiro registro' :
                                   variacao === 0 ? 'Sem alteração' :
                                   `${variacao > 0 ? '+' : ''}${variacao.toFixed(1)}%`
                                  }
                                </span>
                              </div>
                              {valorAnterior && (
                                <div className="text-xs text-gray-500 mt-1">
                                  Anterior: {formatarMoeda(valorAnterior)}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {item.fornecedor?.nome || 'N/A'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {item.nota ? `${item.nota.numero}/${item.nota.serie}` : 'N/A'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <div className="px-6 py-8 text-center">
                <Search className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Nenhum histórico encontrado
                </h3>
                <p className="text-gray-600">
                  Não há registros de preços para esta matéria-prima.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Estado inicial */}
        {!materiaSelecionada && (
          <div className="text-center py-12">
            <Search className="mx-auto h-16 w-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Consulte o histórico de preços
            </h3>
            <p className="text-gray-600 max-w-sm mx-auto">
              Selecione uma matéria-prima no filtro acima para visualizar o histórico de alterações de preço.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoricoPrecos;