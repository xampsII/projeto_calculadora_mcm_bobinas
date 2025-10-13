import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, TrendingDown, Minus, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

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
  variacao_percentual: number | null;
  origem: string;
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

interface MateriaPrimaHistorico {
  materia_prima: {
    id: number;
    nome: string;
    unidade: string;
  };
  historico: HistoricoPreco[];
  total_precos: number;
}

interface HistoricoResponse {
  materias_primas: MateriaPrimaHistorico[];
  total_materias_com_historico: number;
}

const HistoricoPrecos: React.FC = () => {
  const [historicoCompleto, setHistoricoCompleto] = useState<HistoricoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [materiasExpandidas, setMateriasExpandidas] = useState<Set<number>>(new Set());
  const [filtroNome, setFiltroNome] = useState('');

  // Carregar histórico completo de todas as matérias-primas
  const carregarHistoricoCompleto = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/materias-primas/historico-precos/todos`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setHistoricoCompleto(data);
      // Expandir todas por padrão
      const todasIds = new Set(data.materias_primas.map((mp: MateriaPrimaHistorico) => mp.materia_prima.id));
      setMateriasExpandidas(todasIds);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
      setHistoricoCompleto(null);
    } finally {
      setLoading(false);
    }
  };

  // Carregar ao montar o componente
  useEffect(() => {
    carregarHistoricoCompleto();
  }, []);

  const toggleMateria = (id: number) => {
    const novoSet = new Set(materiasExpandidas);
    if (novoSet.has(id)) {
      novoSet.delete(id);
    } else {
      novoSet.add(id);
    }
    setMateriasExpandidas(novoSet);
  };

  const expandirTodas = () => {
    if (historicoCompleto) {
      const todasIds = new Set(historicoCompleto.materias_primas.map(mp => mp.materia_prima.id));
      setMateriasExpandidas(todasIds);
    }
  };

  const recolherTodas = () => {
    setMateriasExpandidas(new Set());
  };

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

  // Filtrar matérias-primas
  const materiasFiltradas = historicoCompleto?.materias_primas.filter(mp =>
    mp.materia_prima.nome.toLowerCase().includes(filtroNome.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Search className="h-6 w-6 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Histórico de Preços de Matérias-Primas
            </h2>
          </div>
          {historicoCompleto && (
            <div className="flex space-x-2">
              <button
                onClick={expandirTodas}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              >
                Expandir Todas
              </button>
              <button
                onClick={recolherTodas}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              >
                Recolher Todas
              </button>
              <button
                onClick={carregarHistoricoCompleto}
                className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Atualizar
              </button>
            </div>
          )}
        </div>

        {/* Filtro por nome */}
        {historicoCompleto && historicoCompleto.materias_primas.length > 0 && (
          <div className="mb-6">
            <label htmlFor="filtro-nome" className="block text-sm font-medium text-gray-700 mb-2">
              Buscar matéria-prima
            </label>
            <input
              id="filtro-nome"
              type="text"
              value={filtroNome}
              onChange={(e) => setFiltroNome(e.target.value)}
              placeholder="Digite o nome da matéria-prima..."
              className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="px-6 py-8 text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-red-600 mb-4" />
            <p className="text-gray-600">Carregando histórico...</p>
          </div>
        )}

        {/* Lista de matérias-primas com histórico */}
        {!loading && historicoCompleto && materiasFiltradas.length > 0 && (
          <div className="space-y-4">
            <div className="text-sm text-gray-600 mb-4">
              Exibindo {materiasFiltradas.length} de {historicoCompleto.total_materias_com_historico} matérias-primas com histórico de preços
            </div>

            {materiasFiltradas.map((mpHistorico) => {
              const isExpandida = materiasExpandidas.has(mpHistorico.materia_prima.id);
              const precoAtual = mpHistorico.historico.find(h => h.vigente_ate === null);

              return (
                <div key={mpHistorico.materia_prima.id} className="border border-gray-200 rounded-lg overflow-hidden">
                  {/* Header da matéria-prima */}
                  <button
                    onClick={() => toggleMateria(mpHistorico.materia_prima.id)}
                    className="w-full bg-gray-50 hover:bg-gray-100 px-6 py-4 flex items-center justify-between transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      {isExpandida ? (
                        <ChevronUp className="h-5 w-5 text-gray-500" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-gray-500" />
                      )}
                      <div className="text-left">
                        <h3 className="text-lg font-medium text-gray-900">
                          {mpHistorico.materia_prima.nome}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Unidade: {mpHistorico.materia_prima.unidade} • {mpHistorico.total_precos} registro{mpHistorico.total_precos !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    {precoAtual && (
                      <div className="text-right">
                        <div className="text-sm text-gray-600">Preço Atual</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {formatarMoeda(precoAtual.valor_unitario)}
                        </div>
                      </div>
                    )}
                  </button>

                  {/* Tabela de histórico (expandida) */}
                  {isExpandida && (
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
                          {mpHistorico.historico.map((item, index) => {
                            const valorAnterior = index < mpHistorico.historico.length - 1 
                              ? mpHistorico.historico[index + 1].valor_unitario 
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
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Estado vazio - sem histórico */}
        {!loading && historicoCompleto && materiasFiltradas.length === 0 && filtroNome && (
          <div className="text-center py-12">
            <Search className="mx-auto h-16 w-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhuma matéria-prima encontrada
            </h3>
            <p className="text-gray-600">
              Nenhuma matéria-prima corresponde ao filtro "{filtroNome}"
            </p>
          </div>
        )}

        {/* Estado vazio - sem dados */}
        {!loading && historicoCompleto && historicoCompleto.materias_primas.length === 0 && (
          <div className="text-center py-12">
            <Search className="mx-auto h-16 w-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum histórico disponível
            </h3>
            <p className="text-gray-600">
              Ainda não há histórico de preços cadastrado para as matérias-primas.
            </p>
          </div>
        )}

        {/* Estado de erro */}
        {!loading && !historicoCompleto && (
          <div className="text-center py-12">
            <div className="text-red-600 mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Erro ao carregar histórico
            </h3>
            <p className="text-gray-600 mb-4">
              Não foi possível carregar o histórico de preços.
            </p>
            <button
              onClick={carregarHistoricoCompleto}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Tentar Novamente
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoricoPrecos;
