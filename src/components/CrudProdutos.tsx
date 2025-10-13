import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Save, X, ShoppingCart, Package, Calculator, DollarSign, TrendingUp } from 'lucide-react';
import { useApp } from '../context/AppContext';
import NotificationToast from './NotificationToast';

const CrudProdutos: React.FC = () => {
  const {
    produtosFinais,
    adicionarProdutoFinal,
    atualizarProdutoFinal,
    excluirProdutoFinal,
    carregarProdutosFinais,
    API_BASE_URL
  } = useApp();
  
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [produtoEditando, setProdutoEditando] = useState<string | null>(null); // ID do produto sendo editado

  // Estados da calculadora de matéria-prima
  const [calculatorData, setCalculatorData] = useState({
    produtoNome: '',
    materiasPrimas: [] as Array<{
      id: string;
      nome: string;
      quantidade: number;
      unidade: string;
      valorUnitario: number;
      valorTotal: number;
    }>,
    margemLucro: 0,
    custoTotal: 0,
    precoVenda: 0,
  });
  
  const [inputValues, setInputValues] = useState<{[key: string]: string}>({});

  // Lista de produtos disponíveis para seleção (simulando banco de dados)
  // Estado para busca de matérias-primas (removido - não utilizado)

  // Lista de matérias-primas disponíveis - carregada da API
  const [materiasPrimasDisponiveis, setMateriasPrimasDisponiveis] = useState<Array<{
    id: string;
    nome: string;
    unidade: string;
    valorUnitario: number;
  }>>([]);

  // Filtrar matérias-primas baseado na busca (removido - não utilizado)

  // Carregar matérias-primas da API
  const carregarMateriasPrimas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/produtos-finais/materias-primas-disponiveis`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const materiasFormatadas = await response.json();
      
      console.log('Matérias-primas carregadas:', materiasFormatadas);
      console.log('Primeira matéria-prima:', materiasFormatadas[0]);
      
      setMateriasPrimasDisponiveis(materiasFormatadas);
      
      if (materiasFormatadas.length === 0) {
        setNotification({
          message: 'Nenhuma matéria-prima encontrada no banco de dados.',
          type: 'error',
        });
      } else {
        setNotification({
          message: `${materiasFormatadas.length} matérias-primas carregadas com sucesso!`,
          type: 'success',
        });
      }
    } catch (error) {
      console.error('Erro ao carregar matérias-primas:', error);
      setNotification({
        message: 'Erro ao carregar matérias-primas. Usando lista padrão.',
        type: 'error',
      });
      
      // Fallback para lista padrão
      setMateriasPrimasDisponiveis([
        { id: '1', nome: 'Aço Inox 316L', unidade: 'kg', valorUnitario: 15.50 },
        { id: '2', nome: 'Aço Carbono', unidade: 'kg', valorUnitario: 8.20 },
        { id: '3', nome: 'Borracha NBR', unidade: 'kg', valorUnitario: 12.00 },
        { id: '4', nome: 'Parafuso M8x20', unidade: 'un', valorUnitario: 0.45 },
        { id: '5', nome: 'Solda Eletrodo', unidade: 'kg', valorUnitario: 25.00 },
      ]);
    }
  };

  // Carregar produtos quando o componente montar
  useEffect(() => {
    carregarProdutosFinais();
    carregarMateriasPrimas();
    criarProdutoPresetado(); // Criar produto presetado automaticamente
  }, []);

  // Função para criar o produto presetado automaticamente
  const criarProdutoPresetado = async () => {
    try {
      // Verificar se já existe um produto com nome "MCM58-Teste"
      const response = await fetch(`${API_BASE_URL}/produtos-finais/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const produtos = await response.json();
      
      // Verificar se produtos é um array
      if (!Array.isArray(produtos)) {
        console.error('Resposta da API não é um array:', produtos);
        return;
      }
      
      const produtoExiste = produtos.find((p: any) => p.nome === 'MCM58-Teste');
      
      if (!produtoExiste) {
        // Criar o produto presetado
        const produtoPresetado = {
          nome: 'MCM58-Teste',
          idUnico: `CALC_${Date.now()}`,
          componentes: [
            {
              id: '1',
              materiaPrimaNome: 'FIO 2.0X7.0 (CANTO QUADRADO)',
              quantidade: 0.7,
              unidadeMedida: 'KG',
              valorUnitario: 72.50,
            },
            {
              id: '2',
              materiaPrimaNome: 'CADARÇO ALGODÃO/POLIESTER 19MM',
              quantidade: 6,
              unidadeMedida: 'MT',
              valorUnitario: 0.20,
            },
            {
              id: '3',
              materiaPrimaNome: 'ADESIVO PVA DAS 403 BAR',
              quantidade: 0.17,
              unidadeMedida: 'KG',
              valorUnitario: 0.23,
            },
            {
              id: '4',
              materiaPrimaNome: 'VERNIZ ASA 952 AMARELO -',
              quantidade: 0.06,
              unidadeMedida: 'L',
              valorUnitario: 43.33,
            },
            {
              id: '5',
              materiaPrimaNome: 'CORDOALHA RED. NUA EXTRA FLEXIVEL 8,0 MM',
              quantidade: 0.06,
              unidadeMedida: 'MT',
              valorUnitario: 25.30,
            },
            {
              id: '6',
              materiaPrimaNome: 'BORRACHA ISOLAÇAO JF',
              quantidade: 1,
              unidadeMedida: 'PC',
              valorUnitario: 0.51,
            },
            {
              id: '7',
              materiaPrimaNome: 'ESPAGUETE 180° - 8,00 MM',
              quantidade: 0.05,
              unidadeMedida: 'MT',
              valorUnitario: 11.45,
            },
            {
              id: '8',
              materiaPrimaNome: 'EMBALAGEM JF NOVA',
              quantidade: 1,
              unidadeMedida: 'UN',
              valorUnitario: 2.83,
            },
          ],
          ativo: true,
        };

        const createResponse = await fetch(`${API_BASE_URL}/produtos-finais/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(produtoPresetado),
        });

        if (createResponse.ok) {
          console.log('Produto presetado criado com sucesso!');
          // Recarregar a lista de produtos
          carregarProdutosFinais();
        } else {
          const errorData = await createResponse.json();
          console.error('Erro ao criar produto:', errorData);
          throw new Error(`Erro ao criar produto: ${errorData.detail || createResponse.statusText}`);
        }
      }
    } catch (error) {
      console.error('Erro ao criar produto presetado:', error);
    }
  };

  const resetCalculator = () => {
    setCalculatorData({
      produtoNome: '',
      materiasPrimas: [
        {
          id: Date.now().toString(),
          nome: '',
          quantidade: 0,
          unidade: '',
          valorUnitario: 0,
          valorTotal: 0,
        },
      ],
      margemLucro: 0,
      custoTotal: 0,
      precoVenda: 0,
    });
    setInputValues({}); // Limpar valores dos inputs
    setProdutoEditando(null); // Limpar estado de edição
    // Removido setShowForm(false); - não deve fechar o formulário quando abrindo
  };

  // Criar uma função separada para cancelar
  const cancelForm = () => {
    resetCalculator();
    setShowForm(false);
  };

  const addMateriaPrima = () => {
    const newMateriaPrima = {
      id: Date.now().toString(),
      nome: '',
      quantidade: 0,
      unidade: '',
      valorUnitario: 0,
      valorTotal: 0,
    };
    setCalculatorData(prev => ({
      ...prev,
      materiasPrimas: [...prev.materiasPrimas, newMateriaPrima]
    }));
  };

  const handleProdutoSelect = (id: string, produtoNome: string) => {
    console.log('=== SELECIONANDO PRODUTO ===');
    console.log('ID:', id);
    console.log('Nome selecionado:', produtoNome);
    console.log('Matérias disponíveis:', materiasPrimasDisponiveis.length);
    
    const produtoSelecionado = materiasPrimasDisponiveis.find(p => p.nome === produtoNome);
    
    console.log('Produto encontrado:', produtoSelecionado);
    
    if (produtoSelecionado) {
      const valorUnitario = produtoSelecionado.valorUnitario || 0;
      console.log('Valor unitário definido:', valorUnitario);
      
      setCalculatorData(prev => {
        const updatedMateriasPrimas = prev.materiasPrimas.map(mp => {
          if (mp.id === id) {
            const quantidade = mp.quantidade || 0;
            const novoValorTotal = quantidade * valorUnitario;
            
            console.log('Atualizando matéria-prima:', {
              id: mp.id,
              nome: produtoSelecionado.nome,
              quantidade,
              valorUnitario,
              valorTotal: novoValorTotal
            });
            
            return {
              ...mp,
              nome: produtoSelecionado.nome,
              unidade: produtoSelecionado.unidade,
              valorUnitario: valorUnitario,
              valorTotal: novoValorTotal,
            };
          }
          return mp;
        });

        const custoTotal = updatedMateriasPrimas.reduce((total, mp) => total + mp.valorTotal, 0);
        const margemLucro = prev.margemLucro / 100;
        const precoVenda = custoTotal * (1 + margemLucro);

        console.log('Novo custo total:', custoTotal);

        return {
          ...prev,
          materiasPrimas: updatedMateriasPrimas,
          custoTotal,
          precoVenda
        };
      });
    } else {
      console.log('Produto não encontrado!');
    }
  };

  const removeMateriaPrima = (id: string) => {
    setCalculatorData(prev => {
      const updatedMateriasPrimas = prev.materiasPrimas.filter(mp => mp.id !== id);
      const custoTotal = updatedMateriasPrimas.reduce((total, mp) => total + mp.valorTotal, 0);
      const margemLucro = prev.margemLucro / 100;
      const precoVenda = custoTotal * (1 + margemLucro);

      return {
        ...prev,
        materiasPrimas: updatedMateriasPrimas,
        custoTotal,
        precoVenda
      };
    });
  };

  const updateMateriaPrima = (id: string, field: string, value: string | number) => {
    setCalculatorData(prev => {
      const updatedMateriasPrimas = prev.materiasPrimas.map(mp => {
        if (mp.id === id) {
          const updated = { ...mp };
          
          // Só permite alterar quantidade (nome e unidade são definidos pela seleção)
          if (field === 'quantidade') {
            updated.quantidade = Number(value) || 0;
            updated.valorTotal = updated.quantidade * updated.valorUnitario;
          }
          // nome, unidade e valorUnitario são definidos pela seleção do produto
          
          return updated;
        }
        return mp;
      });

      const custoTotal = updatedMateriasPrimas.reduce((total, mp) => total + mp.valorTotal, 0);
      const margemLucro = prev.margemLucro / 100;
      const precoVenda = custoTotal * (1 + margemLucro);

      // Debug: verificar valores
      console.log('=== CÁLCULO DE CUSTO TOTAL ===');
      console.log('Matérias-primas:', updatedMateriasPrimas.map(mp => ({
        nome: mp.nome,
        quantidade: mp.quantidade,
        valorUnitario: mp.valorUnitario,
        valorTotal: mp.valorTotal
      })));
      console.log('Custo total calculado:', custoTotal);

      return {
        ...prev,
        materiasPrimas: updatedMateriasPrimas,
        custoTotal,
        precoVenda
      };
    });
  };

  const updateMargemLucro = (margem: number) => {
    setCalculatorData(prev => {
      const custoTotal = prev.materiasPrimas.reduce((total, mp) => total + mp.valorTotal, 0);
      const margemLucro = margem / 100;
      const precoVenda = custoTotal * (1 + margemLucro);
      
      return {
        ...prev,
        margemLucro: margem,
        custoTotal,
        precoVenda
      };
    });
  };

  const loadPredefinedMaterials = () => {
    const listaPadrao = [
      { nome: 'Aço Inox 316L', unidade: 'kg', valorUnitario: 15.50 },
      { nome: 'Aço Carbono', unidade: 'kg', valorUnitario: 8.20 },
      { nome: 'Borracha NBR', unidade: 'kg', valorUnitario: 12.00 },
      { nome: 'Parafuso M8x20', unidade: 'un', valorUnitario: 0.45 },
      { nome: 'Solda Eletrodo', unidade: 'kg', valorUnitario: 25.00 },
    ];
    
    const materialsWithIds = listaPadrao.map((material, index) => ({
      id: `predefined-${index}`,
      nome: material.nome,
      quantidade: 0,
      unidade: material.unidade,
      valorUnitario: material.valorUnitario,
      valorTotal: 0,
    }));
    setCalculatorData(prev => ({
      ...prev,
      materiasPrimas: materialsWithIds
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Usar dados da calculadora
    if (!calculatorData.produtoNome.trim()) {
      setNotification({
        message: 'Digite o nome do produto antes de salvar.',
        type: 'error',
      });
      return;
    }

    if (calculatorData.materiasPrimas.length === 0) {
      setNotification({
        message: 'Adicione pelo menos uma matéria-prima.',
        type: 'error',
      });
      return;
    }

    // Converter matérias-primas para formato de componentes
    const componentes = calculatorData.materiasPrimas
      .filter(mp => mp.nome && mp.quantidade > 0)
      .map(mp => {
        // Buscar o valor unitário atual das matérias-primas disponíveis
        const materiaPrimaDisponivel = materiasPrimasDisponiveis.find(
          disp => disp.nome === mp.nome
        );
        
        const valorUnitario = materiaPrimaDisponivel?.valorUnitario || mp.valorUnitario || 0;
        
        // Garantir que sempre tenha um valor válido (mínimo 0.01)
        const valorFinal = valorUnitario > 0 ? valorUnitario : 0.01;
        
        console.log('Mapeando componente:', {
          nome: mp.nome,
          valorUnitario: valorFinal,
          materiaPrimaDisponivel: materiaPrimaDisponivel?.valorUnitario,
          mpValorUnitario: mp.valorUnitario
        });
        
        return {
          id: mp.id,
          materiaPrimaNome: mp.nome,
          quantidade: mp.quantidade,
          unidadeMedida: mp.unidade,
          valorUnitario: valorFinal,
        };
      });

    if (componentes.length === 0) {
      setNotification({
        message: 'Adicione quantidades válidas para as matérias-primas.',
        type: 'error',
      });
      return;
    }

    setLoading(true);
    try {
      const data = {
        nome: calculatorData.produtoNome.trim(),
        idUnico: `CALC_${Date.now()}`,
        componentes: componentes,
        ativo: true,
      };

      console.log('=== DADOS PARA SALVAR ===');
      console.log('Produto editando:', produtoEditando);
      console.log('Dados:', data);

      const result = produtoEditando 
        ? await atualizarProdutoFinal(produtoEditando, data)
        : await adicionarProdutoFinal(data);

      console.log('=== RESULTADO ===');
      console.log('Result:', result);

      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });

      if (result.success) {
        resetCalculator();
        setShowForm(false); // Fechar formulário após sucesso
        await carregarProdutosFinais(); // Recarregar lista de produtos
      }
    } catch (error) {
      console.error('=== ERRO CAPTURADO ===');
      console.error('Erro:', error);
      console.error('Tipo do erro:', typeof error);
      console.error('Mensagem:', error instanceof Error ? error.message : 'Erro desconhecido');
      
      setNotification({
        message: `Erro ao salvar produto: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este produto?')) return;

    setLoading(true);
    try {
      const result = await excluirProdutoFinal(id);
      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });
      
      if (result.success) {
        await carregarProdutosFinais(); // Recarregar lista após exclusão
      }
    } catch (error) {
      setNotification({
        message: 'Erro ao excluir produto.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (produto: any) => {
    console.log('=== EDITANDO PRODUTO ===');
    console.log('Produto:', produto);
    console.log('Componentes:', produto.componentes);
    
    // Verificar se o produto tem componentes
    if (!produto.componentes || produto.componentes.length === 0) {
      setNotification({
        message: 'Este produto não possui componentes para editar.',
        type: 'error',
      });
      return;
    }
    
    // Preencher o formulário com os dados do produto
    const materiasPrimasEditadas = produto.componentes?.map((comp: any, index: number) => {
      // Buscar a matéria-prima nas disponíveis para pegar o valor atual
      const materiaPrimaDisponivel = materiasPrimasDisponiveis.find(
        mp => mp.nome === (comp.materiaPrimaNome || comp.nome)
      );
      
      // SEMPRE usar o valor das matérias-primas disponíveis, nunca o salvo no componente
      // Se não encontrar, usar o valor salvo no componente ou um valor mínimo
      const valorUnitario = materiaPrimaDisponivel?.valorUnitario || comp.valorUnitario || 0.01;
      const quantidade = comp.quantidade || 0;
      
      console.log('Mapeando componente:', {
        nome: comp.materiaPrimaNome || comp.nome,
        materiaPrimaDisponivel,
        valorUnitario,
        quantidade,
        valorUnitarioSalvo: comp.valorUnitario
      });
      
      return {
        id: comp.id || `edit-${index}`,
        nome: comp.materiaPrimaNome || comp.nome || '',
        quantidade: quantidade,
        unidade: comp.unidadeMedida || comp.unidade || '',
        valorUnitario: valorUnitario, // SEMPRE usar o valor atual do banco
        valorTotal: quantidade * valorUnitario,
      };
    }) || [];
    
    console.log('Matérias-primas editadas:', materiasPrimasEditadas);
    
    // Calcular custo total das matérias-primas editadas
    const custoTotalCalculado = materiasPrimasEditadas.reduce((total: number, mp: any) => total + mp.valorTotal, 0);
    console.log('Custo total calculado das matérias-primas:', custoTotalCalculado);
    console.log('Custo total do produto (banco):', produto.custo_total);
    
    setCalculatorData({
      produtoNome: produto.nome,
      materiasPrimas: materiasPrimasEditadas,
      margemLucro: 0,
      custoTotal: custoTotalCalculado, // Usar o valor calculado, não o do banco
      precoVenda: custoTotalCalculado,
    });
    setProdutoEditando(produto.id); // Definir que está editando este produto
    setShowForm(true);
  };

  return (
    <div className="space-y-6">
      {/* Notification */}
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
          <div className="flex space-x-3">
            <button
              onClick={() => {
                setShowForm(true);
                resetCalculator(); // Agora só limpa os dados, não fecha o formulário
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
            >
              <Calculator className="h-4 w-4" />
              <span>Novo Produto</span>
            </button>
          </div>
        </div>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Calculator className="h-5 w-5 text-blue-600" />
              <span>{produtoEditando ? 'Editar Produto' : 'Novo Produto'}</span>
            </h3>
            <button
              onClick={cancelForm} // Usar cancelForm em vez de resetCalculator
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
                  value={calculatorData.produtoNome}
                  onChange={(e) => setCalculatorData(prev => ({ ...prev, produtoNome: e.target.value }))}
                  placeholder="Ex: Válvula Esfera 1/2"
                  className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500"
                />
              </div>

              {/* ID Único */}
              <div>
                <label htmlFor="idUnico" className="block text-sm font-medium text-gray-700 mb-2">
                  ID Único
                </label>
                <input
                  type="text"
                  id="idUnico"
                  value={`CALC_${Date.now()}`}
                  readOnly
                  className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-600"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Código interno usado pela sua empresa para identificar este produto
                </p>
              </div>
            </div>

            {/* Composição do Produto */}
            <div className="border-t border-gray-200 pt-6">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 flex items-center space-x-2">
                      <Package className="h-5 w-5 text-blue-600" />
                      <span>Matérias-Primas</span>
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      💡 <strong>Calcule o custo do seu produto</strong> selecionando matérias-primas e definindo quantidades.
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={loadPredefinedMaterials}
                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-md text-sm flex items-center space-x-1 transition-colors"
                    >
                      <Package className="h-4 w-4" />
                      <span>Lista Padrão</span>
                    </button>
                    <button
                      type="button"
                      onClick={addMateriaPrima}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm flex items-center space-x-1 transition-colors"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Adicionar</span>
                    </button>
                  </div>
                </div>
                

                {calculatorData.materiasPrimas.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Matéria-Prima
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Quantidade
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Unidade
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Valor Unitário (R$) *
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Valor Total (R$)
                          </th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                            Ações
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {calculatorData.materiasPrimas.map((mp) => (
                          <tr key={mp.id}>
                            <td className="px-4 py-2">
                              <select
                                value={mp.nome}
                                onChange={(e) => handleProdutoSelect(mp.id, e.target.value)}
                                className="w-full px-2 py-1 bg-white border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                              >
                                <option value="">Selecione uma matéria-prima</option>
                                {materiasPrimasDisponiveis.map((produto) => (
                                  <option key={produto.id} value={produto.nome}>
                                    {produto.nome}
                                  </option>
                                ))}
                              </select>
                              <div className="text-xs text-gray-500 mt-1">
                                {materiasPrimasDisponiveis.length} matérias-primas disponíveis
                              </div>
                            </td>
                            <td className="px-4 py-2">
                              <input
                                type="text"
                                value={inputValues[mp.id] !== undefined ? inputValues[mp.id] : (mp.quantidade === 0 ? '' : mp.quantidade.toString().replace('.', ','))}
                                onChange={(e) => {
                                  let value = e.target.value;
                                  
                                  // Permitir apenas números, vírgula e ponto
                                  if (!/^[\d,.]*$/.test(value)) {
                                    return;
                                  }
                                  
                                  // Atualizar o valor do input imediatamente
                                  setInputValues(prev => ({
                                    ...prev,
                                    [mp.id]: value
                                  }));
                                  
                                  // Converter vírgula para ponto internamente
                                  let numericValue = value.replace(',', '.');
                                  
                                  // Se estiver vazio, definir como 0
                                  if (numericValue === '') {
                                    updateMateriaPrima(mp.id, 'quantidade', 0);
                                    return;
                                  }
                                  
                                  // Se terminar com ponto, permitir (para digitação de decimais)
                                  if (numericValue.endsWith('.')) {
                                    return;
                                  }
                                  
                                  // Converter para número e atualizar
                                  const numValue = parseFloat(numericValue);
                                  if (!isNaN(numValue)) {
                                    updateMateriaPrima(mp.id, 'quantidade', numValue);
                                  }
                                }}
                                onBlur={() => {
                                  // Quando sair do campo, limpar o estado local
                                  setInputValues(prev => {
                                    const newValues = { ...prev };
                                    delete newValues[mp.id];
                                    return newValues;
                                  });
                                }}
                                placeholder="0,00"
                                className="w-full px-2 py-1 bg-white border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500"
                                style={{ MozAppearance: 'textfield' }}
                              />
                            </td>
                            <td className="px-4 py-2">
                              <div className="flex items-center space-x-2">
                                <input
                                  type="text"
                                  value={mp.unidade}
                                  readOnly
                                  className="w-full px-2 py-1 bg-gray-100 border border-gray-300 rounded-md text-sm text-gray-600 font-medium"
                                  title="Unidade definida automaticamente pela seleção do produto"
                                />
                                <div className="text-xs text-gray-500 bg-green-100 px-2 py-1 rounded">
                                  Auto
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-2">
                              <div className="flex items-center space-x-2">
                                <input
                                  type="text"
                                  value={mp.valorUnitario > 0 ? `R$ ${mp.valorUnitario.toFixed(2).replace('.', ',')}` : 'R$ 0,00'}
                                  readOnly
                                  className="w-full px-2 py-1 bg-green-50 border border-green-300 rounded-md text-sm text-green-700 font-bold"
                                  title="Valor unitário do banco de dados"
                                />
                                <div className="text-xs text-gray-500 bg-blue-100 px-2 py-1 rounded">
                                  Fixo
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-2">
                              <div className="text-sm font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-200">
                                R$ {mp.valorTotal.toFixed(2).replace('.', ',')}
                              </div>
                            </td>
                            <td className="px-4 py-2 text-right">
                              <button
                                type="button"
                                onClick={() => removeMateriaPrima(mp.id)}
                                className="text-red-600 hover:text-red-800 transition-colors"
                                title="Remover matéria-prima"
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
                    <p className="text-gray-600">Nenhuma matéria-prima adicionada</p>
                    <p className="text-sm text-gray-500">Clique em "Adicionar" para começar</p>
                  </div>
                )}

                {/* Margem de Lucro */}
                {calculatorData.materiasPrimas.length > 0 && (
                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-4">
                      <TrendingUp className="h-5 w-5 text-blue-600" />
                      <h5 className="font-medium text-blue-800">Margem de Lucro</h5>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="margemLucro" className="block text-sm font-medium text-blue-700 mb-2">
                          Margem de Lucro (%)
                        </label>
                        <input
                          type="number"
                          id="margemLucro"
                          step="0.1"
                          min="0"
                          max="1000"
                          value={calculatorData.margemLucro}
                          onChange={(e) => updateMargemLucro(parseFloat(e.target.value) || 0)}
                          placeholder="0.0"
                          className="w-full px-3 py-2 bg-white border border-blue-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500"
                        />
                      </div>
                      <div className="flex items-end">
                        <div className="text-sm text-blue-700">
                          <span className="font-medium">Margem:</span> R$ {(calculatorData.precoVenda - calculatorData.custoTotal).toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Resumo Final */}
                {calculatorData.materiasPrimas.length > 0 && (
                  <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
                    <div className="flex items-center space-x-2 mb-4">
                      <DollarSign className="h-5 w-5 text-green-600" />
                      <h5 className="font-medium text-green-800">Resumo Financeiro</h5>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-900">
                          R$ {calculatorData.custoTotal.toFixed(2)}
                        </div>
                        <div className="text-sm text-green-700 font-medium">Custo Total</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-900">
                          {calculatorData.margemLucro.toFixed(1)}%
                        </div>
                        <div className="text-sm text-green-700 font-medium">Margem de Lucro</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-green-900">
                          R$ {calculatorData.precoVenda.toFixed(2)}
                        </div>
                        <div className="text-sm text-green-700 font-medium">Preço de Venda</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={cancelForm} // Usar cancelForm em vez de resetCalculator
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Salvando...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>{produtoEditando ? 'Salvar Alteração' : 'Criar Produto'}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Produtos Cadastrados</h3>
        </div>
        
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
                    Custo Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {produtosFinais.map((produto) => (
                  <tr key={produto.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{produto.nome}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{produto.idUnico}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{produto.componentes?.length || 0} componentes</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-green-600">
                        R$ {produto.custo_total?.toFixed(2) || '0,00'}
                      </div>
                      <div className="text-xs text-gray-500">
                        Preço atual
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        produto.ativo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {produto.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(produto)}
                          className="text-blue-600 hover:text-blue-900 transition-colors"
                          title="Editar produto"
                        >
                          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(produto.id)}
                          className="text-red-600 hover:text-red-900 transition-colors"
                          title="Excluir produto"
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
          <div className="text-center py-12">
            <ShoppingCart className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum produto cadastrado</h3>
            <p className="text-gray-500">Comece criando seu primeiro produto usando a calculadora.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CrudProdutos;