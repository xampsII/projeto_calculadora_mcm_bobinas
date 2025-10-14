export interface MateriaPrima {
  id: string;
  nome: string;
  unidade_codigo: string;
  menor_unidade_codigo?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Fornecedor {
  id: string;
  nome: string;
  cnpj?: string;
  ativo: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ProdutoComponente {
  id: string;
  materiaPrimaNome: string;
  quantidade: number;
  unidadeMedida: string;
  ultimoValorUnitarioConhecido?: number;
  materiaPrimaId?: string;
}

export interface ProdutoFinal {
  id: string;
  nome: string;
  idUnico: string;
  componentes: ProdutoComponente[];
  ativo: boolean;
  custo_total?: number;
  createdAt: string;
  updatedAt: string;
}

export interface NotaFiscalItem {
  id: string;
  materiaPrimaNome: string;
  unidadeMedida: string;
  menorUnidadeUso?: string;
  quantidade: number;
  valorUnitario: number;
  valorTotal: number;
  materiaPrimaId?: string;
}

export interface NotaFiscal {
  id: string;
  numeroNota: string;
  fornecedorId?: string;
  fornecedorNome: string;
  cnpjFornecedor?: string;
  enderecoFornecedor?: string;
  dataEmissao: string;
  valorTotal: number;
  observacoes?: string;
  itens: NotaFiscalItem[];
  createdAt: string;
  updatedAt: string;
  is_pinned?: boolean;
}

export interface HistoricoPreco {
  id: string;
  materiaPrimaId: string;
  materiaPrimaNome: string;
  valorUnitario: number;
  valorUnitarioConvertido: number;
  unidadeCompra: string;
  unidadeUso: string;
  fatorConversao: number;
  quantidade: number;
  valorTotal: number;
  dataCompra: string;
  fornecedorId?: string;
  fornecedorNome?: string;
  valorAnterior?: number;
  createdAt: string;
}

export interface HistoricoProduto {
  id: string;
  produtoId: string;
  produtoNome: string;
  precoCalculado: number;
  dataCalculo: string;
  observacoes?: string;
  createdAt: string;
}

export interface UnidadeMedida {
  id: string;
  nome: string;
  sigla: string;
  tipo: 'peso' | 'volume' | 'comprimento' | 'area' | 'unidade';
}

export interface NotaFiscalFilters {
  busca?: string;
  fornecedor?: string;
  materiaPrima?: string;
  dataInicio?: string;
  dataFim?: string;
  page?: number;
  limit?: number;
  sortBy?: 'dataEmissao' | 'valorTotal';
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface AppContextType {
  // Dados
  materiasPrimas: MateriaPrima[];
  fornecedores: Fornecedor[];
  produtosFinais: ProdutoFinal[];
  notasFiscais: NotaFiscal[];
  historicoPrecos: HistoricoPreco[];
  historicoProdutos: HistoricoProduto[];
  unidadesMedida: UnidadeMedida[];
  
  // Notas Fiscais
  buscarNotasFiscais: (filters: NotaFiscalFilters) => Promise<PaginatedResponse<NotaFiscal>>;
  obterNotaFiscal: (id: string) => Promise<NotaFiscal | null>;
  adicionarNotaFiscal: (nota: Omit<NotaFiscal, 'id' | 'createdAt' | 'updatedAt' | 'valorTotal'>) => Promise<{ success: boolean; message: string; data?: NotaFiscal }>;
  atualizarNotaFiscal: (id: string, nota: Partial<NotaFiscal>) => Promise<{ success: boolean; message: string }>;
  duplicarNotaFiscal: (id: string) => Promise<{ success: boolean; message: string; data?: NotaFiscal }>;
  importarNotasFiscais: (arquivo: File) => Promise<{ success: boolean; message: string; preview?: any[] }>;
  buscarNotaPorChaveAPI: (chave: string) => Promise<{ success: boolean; message: string; data?: Partial<NotaFiscal> }>;
  
  // Matérias-primas
  carregarMateriasPrimas: () => Promise<void>;
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
  carregarProdutosFinais: () => Promise<void>;
  
  // Histórico
  obterHistoricoPorMateria: (nome: string) => HistoricoPreco[];
  obterHistoricoPorProduto: (nome: string) => HistoricoProduto[];
  limparHistoricoAntigo: () => void;
  buscarHistoricoPrecos: () => Promise<any>;
  
  // API Base URL
  API_BASE_URL: string;
}