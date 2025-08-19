import React, { createContext, useContext, useState, ReactNode } from 'react';
import { AppContextType, NotaFiscal, HistoricoPreco, MateriaPrima, Fornecedor, ProdutoFinal, UnidadeMedida } from '../types';
import { 
  materiasPrimasData, 
  fornecedoresData, 
  produtosFinaisData, 
  notasFiscaisData, 
  historicoPrecosData,
  unidadesMedidaData 
} from '../data/mockData';

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
  const [materiasPrimas, setMateriasPrimas] = useState<MateriaPrima[]>(materiasPrimasData);
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>(fornecedoresData);
  const [produtosFinais, setProdutosFinais] = useState<ProdutoFinal[]>(produtosFinaisData);
  const [notasFiscais, setNotasFiscais] = useState<NotaFiscal[]>(notasFiscaisData);
  const [historicoPrecos, setHistoricoPrecos] = useState<HistoricoPreco[]>(historicoPrecosData);
  const [unidadesMedida] = useState<UnidadeMedida[]>(unidadesMedidaData);

  // Função para limpar histórico antigo (mais de 3 meses)
  const limparHistoricoAntigo = () => {
    const tresMesesAtras = new Date();
    tresMesesAtras.setMonth(tresMesesAtras.getMonth() - 3);
    
    setHistoricoPrecos(prev => 
      prev.filter(item => new Date(item.dataCompra) >= tresMesesAtras)
    );
  };

  // CRUD Matérias-primas
  const adicionarMateriaPrima = async (materia: Omit<MateriaPrima, 'id' | 'createdAt' | 'updatedAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      // Verificar se já existe
      const existe = materiasPrimas.some(m => 
        m.nome.toLowerCase() === materia.nome.toLowerCase() && m.ativo
      );

      if (existe) {
        return { success: false, message: 'Já existe uma matéria-prima com este nome.' };
      }

      const id = Date.now().toString();
      const agora = new Date().toISOString();

      const novaMateria: MateriaPrima = {
        ...materia,
        id,
        createdAt: agora,
        updatedAt: agora
      };

      setMateriasPrimas(prev => [...prev, novaMateria]);
      return { success: true, message: 'Matéria-prima cadastrada com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao cadastrar matéria-prima.' };
    }
  };

  const atualizarMateriaPrima = async (id: string, materia: Partial<MateriaPrima>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      setMateriasPrimas(prev => prev.map(m => 
        m.id === id ? { ...m, ...materia, updatedAt: new Date().toISOString() } : m
      ));

      return { success: true, message: 'Matéria-prima atualizada com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao atualizar matéria-prima.' };
    }
  };

  const excluirMateriaPrima = async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      // Verificar se está sendo usada em notas fiscais
      const emUso = notasFiscais.some(nf => nf.materiaPrimaId === id);
      
      if (emUso) {
        // Desativar ao invés de excluir
        setMateriasPrimas(prev => prev.map(m => 
          m.id === id ? { ...m, ativo: false, updatedAt: new Date().toISOString() } : m
        ));
        return { success: true, message: 'Matéria-prima desativada (estava sendo usada em notas fiscais).' };
      } else {
        setMateriasPrimas(prev => prev.filter(m => m.id !== id));
        return { success: true, message: 'Matéria-prima excluída com sucesso!' };
      }
    } catch (error) {
      return { success: false, message: 'Erro ao excluir matéria-prima.' };
    }
  };

  // CRUD Fornecedores
  const adicionarFornecedor = async (fornecedor: Omit<Fornecedor, 'id' | 'createdAt' | 'updatedAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      // Verificar se já existe
      const existe = fornecedores.some(f => 
        (f.nome.toLowerCase() === fornecedor.nome.toLowerCase() || 
         (fornecedor.cnpj && f.cnpj === fornecedor.cnpj)) && f.ativo
      );

      if (existe) {
        return { success: false, message: 'Já existe um fornecedor com este nome ou CNPJ.' };
      }

      const id = Date.now().toString();
      const agora = new Date().toISOString();

      const novoFornecedor: Fornecedor = {
        ...fornecedor,
        id,
        createdAt: agora,
        updatedAt: agora
      };

      setFornecedores(prev => [...prev, novoFornecedor]);
      return { success: true, message: 'Fornecedor cadastrado com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao cadastrar fornecedor.' };
    }
  };

  const atualizarFornecedor = async (id: string, fornecedor: Partial<Fornecedor>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      setFornecedores(prev => prev.map(f => 
        f.id === id ? { ...f, ...fornecedor, updatedAt: new Date().toISOString() } : f
      ));

      return { success: true, message: 'Fornecedor atualizado com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao atualizar fornecedor.' };
    }
  };

  const excluirFornecedor = async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      // Verificar se está sendo usado em notas fiscais
      const emUso = notasFiscais.some(nf => nf.fornecedorId === id);
      
      if (emUso) {
        // Desativar ao invés de excluir
        setFornecedores(prev => prev.map(f => 
          f.id === id ? { ...f, ativo: false, updatedAt: new Date().toISOString() } : f
        ));
        return { success: true, message: 'Fornecedor desativado (estava sendo usado em notas fiscais).' };
      } else {
        setFornecedores(prev => prev.filter(f => f.id !== id));
        return { success: true, message: 'Fornecedor excluído com sucesso!' };
      }
    } catch (error) {
      return { success: false, message: 'Erro ao excluir fornecedor.' };
    }
  };

  // CRUD Produtos Finais
  const adicionarProdutoFinal = async (produto: Omit<ProdutoFinal, 'id' | 'createdAt' | 'updatedAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      // Verificar se já existe
      const existe = produtosFinais.some(p => 
        (p.nome.toLowerCase() === produto.nome.toLowerCase() || 
         p.idUnico.toLowerCase() === produto.idUnico.toLowerCase()) && p.ativo
      );

      if (existe) {
        return { success: false, message: 'Já existe um produto com este nome ou ID único.' };
      }

      const id = Date.now().toString();
      const agora = new Date().toISOString();

      const novoProduto: ProdutoFinal = {
        ...produto,
        id,
        createdAt: agora,
        updatedAt: agora
      };

      setProdutosFinais(prev => [...prev, novoProduto]);
      return { success: true, message: 'Produto cadastrado com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao cadastrar produto.' };
    }
  };

  const atualizarProdutoFinal = async (id: string, produto: Partial<ProdutoFinal>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      setProdutosFinais(prev => prev.map(p => 
        p.id === id ? { ...p, ...produto, updatedAt: new Date().toISOString() } : p
      ));

      return { success: true, message: 'Produto atualizado com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao atualizar produto.' };
    }
  };

  const excluirProdutoFinal = async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));

      setProdutosFinais(prev => prev.filter(p => p.id !== id));
      return { success: true, message: 'Produto excluído com sucesso!' };
    } catch (error) {
      return { success: false, message: 'Erro ao excluir produto.' };
    }
  };

  // Notas Fiscais
  const adicionarNotaFiscal = async (novaNota: Omit<NotaFiscal, 'id' | 'createdAt'>): Promise<{ success: boolean; message: string }> => {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

      const id = Date.now().toString();
      const createdAt = new Date().toISOString();

      const notaCompleta: NotaFiscal = {
        ...novaNota,
        id,
        createdAt
      };

      // Buscar dados da matéria-prima para conversão
      const materiaPrima = materiasPrimas.find(m => m.id === novaNota.materiaPrimaId);
      if (!materiaPrima) {
        return { success: false, message: 'Matéria-prima não encontrada.' };
      }

      // Verificar se houve mudança de preço
      const ultimoPreco = historicoPrecos
        .filter(h => h.materiaPrimaId === novaNota.materiaPrimaId)
        .sort((a, b) => new Date(b.dataCompra).getTime() - new Date(a.dataCompra).getTime())[0];

      let mensagem = 'Nota fiscal cadastrada com sucesso!';

      if (!ultimoPreco || ultimoPreco.valorUnitario !== novaNota.valorUnitario) {
        // Calcular valor convertido para unidade de uso
        const valorUnitarioConvertido = novaNota.valorUnitario / materiaPrima.fatorConversao;

        // Adicionar ao histórico de preços
        const novoHistorico: HistoricoPreco = {
          id: `hist_${id}`,
          materiaPrimaId: novaNota.materiaPrimaId,
          materiaPrimaNome: novaNota.materiaPrimaNome,
          valorUnitario: novaNota.valorUnitario,
          valorUnitarioConvertido,
          unidadeCompra: materiaPrima.unidadeCompra,
          unidadeUso: materiaPrima.unidadeUso,
          fatorConversao: materiaPrima.fatorConversao,
          dataCompra: novaNota.dataCompra,
          fornecedorId: novaNota.fornecedorId,
          fornecedorNome: novaNota.fornecedorNome,
          valorAnterior: ultimoPreco?.valorUnitario,
          createdAt
        };

        setHistoricoPrecos(prev => [...prev, novoHistorico]);
        
        if (ultimoPreco) {
          const diferenca = ((novaNota.valorUnitario - ultimoPreco.valorUnitario) / ultimoPreco.valorUnitario * 100).toFixed(1);
          const sinal = novaNota.valorUnitario > ultimoPreco.valorUnitario ? '+' : '';
          mensagem += ` Preço atualizado (${sinal}${diferenca}%).`;
        } else {
          mensagem += ' Primeiro registro de preço para esta matéria-prima.';
        }
      }

      // Adicionar nota fiscal
      setNotasFiscais(prev => [...prev, notaCompleta]);

      // Limpar histórico antigo automaticamente
      limparHistoricoAntigo();

      return { success: true, message: mensagem };
    } catch (error) {
      return { success: false, message: 'Erro ao cadastrar nota fiscal. Tente novamente.' };
    }
  };

  const obterHistoricoPorMateria = (materiaPrimaId: string): HistoricoPreco[] => {
    return historicoPrecos
      .filter(h => h.materiaPrimaId === materiaPrimaId)
      .sort((a, b) => new Date(b.dataCompra).getTime() - new Date(a.dataCompra).getTime());
  };

  const value: AppContextType = {
    // Dados
    materiasPrimas: materiasPrimas.filter(m => m.ativo),
    fornecedores: fornecedores.filter(f => f.ativo),
    produtosFinais: produtosFinais.filter(p => p.ativo),
    notasFiscais,
    historicoPrecos,
    unidadesMedida,
    
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
    
    // Notas fiscais
    adicionarNotaFiscal,
    
    // Histórico
    obterHistoricoPorMateria,
    limparHistoricoAntigo,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};