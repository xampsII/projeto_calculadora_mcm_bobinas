import React, { createContext, useContext, useState, ReactNode } from 'react';
import { 
  AppContextType, 
  NotaFiscal, 
  HistoricoPreco, 
  MateriaPrima, 
  Fornecedor, 
  ProdutoFinal, 
  UnidadeMedida, 
  NotaFiscalItem,
  HistoricoProduto,
  NotaFiscalFilters,
  PaginatedResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const AppContext = createContext<AppContextType | null>(null);

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp deve ser usado dentro de AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [materiasPrimas, setMateriasPrimas] = useState<MateriaPrima[]>([]);
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [produtosFinais, setProdutosFinais] = useState<ProdutoFinal[]>([]);
  const [notasFiscais, setNotasFiscais] = useState<NotaFiscal[]>([]);
  const [historicoPrecos, setHistoricoPrecos] = useState<HistoricoPreco[]>([]);
  const [historicoProdutos, setHistoricoProdutos] = useState<HistoricoProduto[]>([]);
  const [unidadesMedida] = useState<UnidadeMedida[]>([]);

  // Função para limpar histórico antigo (mais de 3 meses)
  const limparHistoricoAntigo = () => {
    const tresMesesAtras = new Date();
    tresMesesAtras.setMonth(tresMesesAtras.getMonth() - 3);
    
    setHistoricoPrecos(prev => 
      prev.filter(item => new Date(item.dataCompra) >= tresMesesAtras)
    );
  };

  // Buscar notas fiscais com filtros e paginação
  const buscarNotasFiscais = async (filters: NotaFiscalFilters): Promise<PaginatedResponse<NotaFiscal>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/?page=${filters.page || 1}&page_size=${filters.limit || 25}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: PaginatedResponse<NotaFiscal> = await response.json();
      setNotasFiscais(data.data ?? []);
      return data;
    } catch (error) {
      console.error("Erro ao buscar notas fiscais:", error);
      return { data: [], total: 0, page: 1, limit: 25, totalPages: 0 };
    }
  };

  // Obter uma nota fiscal específica
  const obterNotaFiscal = async (id: string): Promise<NotaFiscal | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: NotaFiscal = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao obter nota fiscal:", error);
      return null;
    }
  };

  // CRUD Matérias-primas
  const adicionarMateriaPrima = async (materia: Omit<MateriaPrima, 'id' | 'createdAt' | 'updatedAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/materias-primas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(materia),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao adicionar matéria-prima:", error);
      return { success: false, message: 'Erro ao cadastrar matéria-prima.' };
    }
  };

  const atualizarMateriaPrima = async (id: string, materia: Partial<MateriaPrima>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/materias-primas/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(materia),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao atualizar matéria-prima:", error);
      return { success: false, message: 'Erro ao atualizar matéria-prima.' };
    }
  };

  const excluirMateriaPrima = async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/materias-primas/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao excluir matéria-prima:", error);
      return { success: false, message: 'Erro ao excluir matéria-prima.' };
    }
  };

  // CRUD Fornecedores
  const adicionarFornecedor = async (fornecedor: Omit<Fornecedor, 'id' | 'createdAt' | 'updatedAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/fornecedores`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fornecedor),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao adicionar fornecedor:", error);
      return { success: false, message: 'Erro ao cadastrar fornecedor.' };
    }
  };

  const atualizarFornecedor = async (id: string, fornecedor: Partial<Fornecedor>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/fornecedores/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fornecedor),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao atualizar fornecedor:", error);
      return { success: false, message: 'Erro ao atualizar fornecedor.' };
    }
  };

  const excluirFornecedor = async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/fornecedores/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao excluir fornecedor:", error);
      return { success: false, message: 'Erro ao excluir fornecedor.' };
    }
  };

  // CRUD Produtos Finais
  const adicionarProdutoFinal = async (produto: Omit<ProdutoFinal, 'id' | 'createdAt' | 'updatedAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/produtos-finais`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(produto),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao adicionar produto final:", error);
      return { success: false, message: 'Erro ao cadastrar produto.' };
    }
  };

  const atualizarProdutoFinal = async (id: string, produto: Partial<ProdutoFinal>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/produtos-finais/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(produto),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao atualizar produto final:", error);
      return { success: false, message: 'Erro ao atualizar produto.' };
    }
  };

  const excluirProdutoFinal = async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/produtos-finais/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao excluir produto final:", error);
      return { success: false, message: 'Erro ao excluir produto.' };
    }
  };

  // Notas Fiscais
  const adicionarNotaFiscal = async (novaNota: Omit<NotaFiscal, 'id' | 'createdAt' | 'updatedAt' | 'valorTotal'>): Promise<{ success: boolean; message: string; data?: NotaFiscal }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(novaNota),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string; data?: NotaFiscal } = await response.json();

      if (data.success && data.data) {
        const notaCompleta: NotaFiscal = data.data;
        let mensagem = 'Nota fiscal cadastrada com sucesso!';

        // Processar cada item da nota para atualizar o histórico de preços
        for (const item of notaCompleta.itens) {
          if (item.materiaPrimaId) { // Apenas se o item estiver vinculado a uma MP cadastrada
            const materiaPrima = materiasPrimas.find(m => m.id === item.materiaPrimaId);
            if (materiaPrima) {
              const ultimoPreco = historicoPrecos
                .filter(h => h.materiaPrimaId === item.materiaPrimaId)
                .sort((a, b) => new Date(b.dataCompra).getTime() - new Date(a.dataCompra).getTime())[0];

              if (!ultimoPreco || ultimoPreco.valorUnitario !== item.valorUnitario) {
                const valorUnitarioConvertido = item.valorUnitario / materiaPrima.fatorConversao;
                const novoHistorico: HistoricoPreco = {
                  id: `hist_${Date.now()}_${item.id}`, // ID único para cada registro de histórico
                  materiaPrimaId: item.materiaPrimaId,
                  materiaPrimaNome: item.materiaPrimaNome,
                  valorUnitario: item.valorUnitario,
                  valorUnitarioConvertido,
                  unidadeCompra: materiaPrima.unidadeCompra,
                  unidadeUso: materiaPrima.unidadeUso,
                  fatorConversao: materiaPrima.fatorConversao,
                  quantidade: item.quantidade,
                  valorTotal: item.valorTotal,
                  dataCompra: notaCompleta.dataEmissao,
                  fornecedorId: notaCompleta.fornecedorId,
                  fornecedorNome: notaCompleta.fornecedorNome,
                  valorAnterior: ultimoPreco?.valorUnitario,
                  createdAt: new Date().toISOString()
                };
                setHistoricoPrecos(prev => [...prev, novoHistorico]);
                if (ultimoPreco) {
                  const diferenca = ((item.valorUnitario - ultimoPreco.valorUnitario) / ultimoPreco.valorUnitario * 100).toFixed(1);
                  const sinal = item.valorUnitario > ultimoPreco.valorUnitario ? '+' : '';
                  mensagem += ` Preço de ${item.materiaPrimaNome} atualizado (${sinal}${diferenca}%).`;
                } else {
                  mensagem += ` Primeiro registro de preço para ${item.materiaPrimaNome}.`;
                }
              }
            }
          }
        }

        // Limpar histórico antigo automaticamente
        limparHistoricoAntigo();

        return { success: true, message: mensagem, data: notaCompleta };
      } else {
        return { success: false, message: 'Erro ao cadastrar nota fiscal. Tente novamente.' };
      }
    } catch (error) {
      console.error("Erro ao adicionar nota fiscal:", error);
      return { success: false, message: 'Erro ao cadastrar nota fiscal. Tente novamente.' };
    }
  };

  // Atualizar nota fiscal
  const atualizarNotaFiscal = async (id: string, dadosAtualizados: Partial<NotaFiscal>): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dadosAtualizados),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao atualizar nota fiscal:", error);
      return { success: false, message: 'Erro ao atualizar nota fiscal.' };
    }
  };

  // Duplicar nota fiscal
  const duplicarNotaFiscal = async (id: string): Promise<{ success: boolean; message: string; data?: NotaFiscal }> => {
    try {
      const notaOriginal = await obterNotaFiscal(id);
      if (!notaOriginal) {
        return { success: false, message: 'Nota fiscal não encontrada.' };
      }

      const novoId = Date.now().toString();
      const agora = new Date().toISOString();
      const numeroNota = `${notaOriginal.numeroNota}-COPIA`;

      const notaDuplicada: NotaFiscal = {
        ...notaOriginal,
        id: novoId,
        numeroNota,
        createdAt: agora,
        updatedAt: agora,
        itens: notaOriginal.itens.map(item => ({
          ...item,
          id: `${novoId}-${item.id}`,
        })),
      };

      const response = await fetch(`${API_BASE_URL}/notas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(notaDuplicada),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string; data?: NotaFiscal } = await response.json();

      if (data.success && data.data) {
        return { success: true, message: 'Nota fiscal duplicada com sucesso!', data: data.data };
      } else {
        return { success: false, message: 'Erro ao duplicar nota fiscal.' };
      }
    } catch (error) {
      console.error("Erro ao duplicar nota fiscal:", error);
      return { success: false, message: 'Erro ao duplicar nota fiscal.' };
    }
  };

  // Importar notas fiscais de arquivo
  const importarNotasFiscais = async (arquivo: File): Promise<{ success: boolean; message: string; dados?: any; preview?: any[] }> => {
    try {
      const formData = new FormData();
      formData.append('files', arquivo);
      formData.append('commit', 'true');

      const response = await fetch(`${API_BASE_URL}/notas/import`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string; resultados?: any[] } = await response.json();

      if (data.success && data.resultados && data.resultados.length > 0) {
        const resultado = data.resultados[0];
        return { 
          success: true, 
          message: resultado.mensagem, 
          dados: resultado.dados 
        };
      } else {
        return { success: false, message: data.message };
      }
    } catch (error) {
      console.error("Erro ao importar notas fiscais:", error);
      return { success: false, message: 'Erro ao processar arquivo. Verifique o formato e tente novamente.' };
    }
  };

  // Buscar nota por chave API
  const buscarNotaPorChaveAPI = async (chave: string): Promise<{ success: boolean; message: string; data?: Partial<NotaFiscal> }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/chave/${chave}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: { success: boolean; message: string; data?: Partial<NotaFiscal> } = await response.json();
      return data;
    } catch (error) {
      console.error("Erro ao buscar nota por chave API:", error);
      return { success: false, message: 'Erro de conexão com a API da Receita Federal. Tente novamente.' };
    }
  };

  const obterHistoricoPorMateria = (materiaPrimaId: string): HistoricoPreco[] => {
    return historicoPrecos
      .filter(h => h.materiaPrimaId === materiaPrimaId)
      .sort((a, b) => new Date(b.dataCompra).getTime() - new Date(a.dataCompra).getTime());
  };

  const obterHistoricoPorProduto = (nome: string): HistoricoProduto[] => {
    return historicoProdutos
      .filter(h => h.produtoNome.toLowerCase().includes(nome.toLowerCase()))
      .sort((a, b) => new Date(b.dataCalculo).getTime() - new Date(a.dataCalculo).getTime());
  };

  const value: AppContextType = {
    // Dados
    materiasPrimas: materiasPrimas.filter(m => m.ativo),
    fornecedores: fornecedores.filter(f => f.ativo),
    produtosFinais: produtosFinais.filter(p => p.ativo),
    notasFiscais,
    historicoPrecos,
    historicoProdutos,
    unidadesMedida,
    
    // Notas fiscais
    buscarNotasFiscais,
    obterNotaFiscal,
    adicionarNotaFiscal,
    atualizarNotaFiscal,
    duplicarNotaFiscal,
    importarNotasFiscais,
    buscarNotaPorChaveAPI,
    
    // Matérias-primas
    adicionarMateriaPrima,
    atualizarMateriaPrima,
    excluirMateriaPrima,
    
    // Fornecedores
    adicionarFornecedor,
    atualizarFornecedor,
    excluirFornecedor,
    
    // Produtos finais
    adicionarProdutoFinal,
    atualizarProdutoFinal,
    excluirProdutoFinal,
    
    // Histórico
    obterHistoricoPorMateria,
    obterHistoricoPorProduto,
    limparHistoricoAntigo,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};