export interface MateriaPrima {
  id: string;
  nome: string;
  unidadeCompra: string;
  unidadeUso: string;
  fatorConversao: number;
  ativo: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Fornecedor {
  id: string;
  nome: string;
  cnpj?: string;
  ativo: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProdutoFinal {
  id: string;
  nome: string;
  idUnico: string;
  ativo: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface NotaFiscal {
  id: string;
  materiaPrimaId: string;
  materiaPrimaNome: string;
  quantidade: number;
  unidadeCompra: string;
  valorUnitario: number;
  valorTotal: number;
  dataCompra: string;
  fornecedorId?: string;
  fornecedorNome?: string;
  observacoes?: string;
  createdAt: string;
}

export interface HistoricoPreco {
  id: string;
  materiaPrimaId: string;
  materiaPrimaNome: string;
  valorUnitario: number;
  valorUnitarioConvertido: number; // Valor por unidade de uso
  unidadeCompra: string;
  unidadeUso: string;
  fatorConversao: number;
  dataCompra: string;
  fornecedorId?: string;
  fornecedorNome?: string;
  valorAnterior?: number;
  createdAt: string;
}

export interface UnidadeMedida {
  id: string;
  nome: string;
  sigla: string;
  tipo: 'peso' | 'volume' | 'comprimento' | 'area' | 'unidade';
}

export interface AppContextType {
  // Dados
  materiasPrimas: MateriaPrima[];
  fornecedores: Fornecedor[];
  produtosFinais: ProdutoFinal[];
  notasFiscais: NotaFiscal[];
  historicoPrecos: HistoricoPreco[];
  unidadesMedida: UnidadeMedida[];
  
  // Matérias-primas
  adicionarMateriaPrima: (materia: Omit<MateriaPrima, 'id' | 'createdAt' | 'updatedAt'>) => Promise<{ success: boolean; message: string }>;
  atualizarMateriaPrima: (id: string, materia: Partial<MateriaPrima>) => Promise<{ success: boolean; message: string }>;
  excluirMateriaPrima: (id: string) => Promise<{ success: boolean; message: string }>;
  
  // Fornecedores
  adicionarFornecedor: (fornecedor: Omit<Fornecedor, 'id' | 'createdAt' | 'updatedAt'>) => Promise<{ success: boolean; message: string }>;
  atualizarFornecedor: (id: string, fornecedor: Partial<Fornecedor>) => Promise<{ success: boolean; message: string }>;
  excluirFornecedor: (id: string) => Promise<{ success: boolean; message: string }>;
  
  // Produtos finais
  adicionarProdutoFinal: (produto: Omit<ProdutoFinal, 'id' | 'createdAt' | 'updatedAt'>) => Promise<{ success: boolean; message: string }>;
  atualizarProdutoFinal: (id: string, produto: Partial<ProdutoFinal>) => Promise<{ success: boolean; message: string }>;
  excluirProdutoFinal: (id: string) => Promise<{ success: boolean; message: string }>;
  
  // Notas fiscais
  adicionarNotaFiscal: (nota: Omit<NotaFiscal, 'id' | 'createdAt'>) => Promise<{ success: boolean; message: string }>;
  
  // Histórico
  obterHistoricoPorMateria: (materiaPrimaId: string) => HistoricoPreco[];
  limparHistoricoAntigo: () => void;
}