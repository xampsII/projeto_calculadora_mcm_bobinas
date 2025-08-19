import React, { useState } from 'react';
import { Search, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useApp } from '../context/AppContext';

const HistoricoPrecos: React.FC = () => {
  const { materiasPrimas, obterHistoricoPorMateria } = useApp();
  const [materiaSelecionada, setMateriaSelecionada] = useState('');

  const historico = materiaSelecionada ? obterHistoricoPorMateria(materiaSelecionada) : [];

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  };

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString('pt-BR');
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
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Search className="h-6 w-6 text-orange-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            Histórico de Preços por Matéria-Prima
          </h2>
        </div>

        {/* Filtro por matéria-prima */}
        <div className="mb-6">
          <label htmlFor="materia-select" className="block text-sm font-medium text-gray-700 mb-2">
            Selecione a matéria-prima
          </label>
          <select
            id="materia-select"
            value={materiaSelecionada}
            onChange={(e) => setMateriaSelecionada(e.target.value)}
            className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
          >
            <option value="">Escolha uma matéria-prima</option>
            {materiasPrimas.map((materia) => (
              <option key={materia.id} value={materia.id}>
                {materia.nome}
              </option>
            ))}
          </select>
        </div>

        {/* Tabela de histórico */}
        {materiaSelecionada && (
          <div className="overflow-hidden border border-gray-200 rounded-lg">
            {historico.length > 0 ? (
              <>
                {/* Header da tabela */}
                <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">
                    Histórico de Preços - {historico[0]?.materiaPrimaNome}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {historico.length} registro{historico.length !== 1 ? 's' : ''} encontrado{historico.length !== 1 ? 's' : ''}
                  </p>
                </div>

                {/* Tabela */}
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Data da Compra
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Valor Unitário (Compra)
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Valor por Unidade de Uso
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Variação
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Fornecedor
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {historico.map((item) => {
                        const variacao = calcularVariacao(item.valorUnitario, item.valorAnterior);
                        
                        return (
                          <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatarData(item.dataCompra)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {formatarMoeda(item.valorUnitario)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              <div>
                                <span className="font-medium">{formatarMoeda(item.valorUnitarioConvertido)}</span>
                                <div className="text-xs text-gray-500">
                                  por {item.unidadeUso}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <div className="flex items-center space-x-2">
                                {renderTrendIcon(item.valorUnitario, item.valorAnterior)}
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
                              {item.valorAnterior && (
                                <div className="text-xs text-gray-500 mt-1">
                                  Anterior: {formatarMoeda(item.valorAnterior)}
                                </div>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {item.fornecedor}
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