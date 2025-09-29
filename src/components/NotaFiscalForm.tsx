import React, { useState } from 'react';
import { Save, Upload, FileText, Loader2, Plus, Trash2, Key, Download } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { NotaFiscal, NotaFiscalItem } from '../types';
import { formatCNPJ, validateCNPJ, formatCurrency, parseCurrency } from '../utils/formatters';
import Breadcrumb from './ui/Breadcrumb';
import NotificationToast from './NotificationToast';

interface NotaFiscalFormProps {
  notaId?: string;
  onVoltar: () => void;
  onSalvar?: (nota: NotaFiscal) => void;
}

const UNIDADES_OPCOES = [
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
  { value: 'saco', label: 'Saco' },
  { value: 'tubo', label: 'Tubo' },
  { value: 'barra', label: 'Barra' },
  { value: 'lata', label: 'Lata' },
  { value: 'galão', label: 'Galão' },
  { value: 'm²', label: 'Metro quadrado (m²)' },
  { value: 'm³', label: 'Metro cúbico (m³)' },
  { value: 'outro', label: 'Outra...' },
];

const NotaFiscalForm: React.FC<NotaFiscalFormProps> = ({ notaId, onVoltar, onSalvar }) => {
  const { 
    unidadesMedida, 
    adicionarNotaFiscal, 
    atualizarNotaFiscal, 
    obterNotaFiscal,
    importarNotasFiscais,
    buscarNotaPorChaveAPI
  } = useApp();
  
  const [activeMode, setActiveMode] = useState<'manual' | 'import' | 'api'>('manual');
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [apiLoading, setApiLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [dadosExtraidos, setDadosExtraidos] = useState<any>(null);
  const [apiKey, setApiKey] = useState('');
  const [customUnidades, setCustomUnidades] = useState<{[key: number]: string}>({});

  const [formData, setFormData] = useState({
    numeroNota: '',
    fornecedorNome: '',
    cnpjFornecedor: '',
    enderecoFornecedor: '',
    dataEmissao: '',
    observacoes: '',
    itens: [{ 
      id: Date.now().toString(), 
      materiaPrimaNome: '', 
      unidadeMedida: '', 
      menorUnidadeUso: '',
      quantidade: 0, 
      valorUnitario: 0, 
      valorTotal: 0 
    }] as NotaFiscalItem[],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Carregar nota para edição
  React.useEffect(() => {
    if (notaId) {
      loadNota();
    }
  }, [notaId]);

  const loadNota = async () => {
    if (!notaId) return;
    
    setLoading(true);
    try {
      const nota = await obterNotaFiscal(notaId);
      if (nota) {
        setFormData({
          numeroNota: nota.numeroNota,
          fornecedorNome: nota.fornecedorNome,
          cnpjFornecedor: nota.cnpjFornecedor || '',
          enderecoFornecedor: nota.enderecoFornecedor || '',
          dataEmissao: nota.dataEmissao,
          observacoes: nota.observacoes || '',
          itens: nota.itens,
        });
      }
    } catch (error) {
      setNotification({
        message: 'Erro ao carregar nota fiscal.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.numeroNota.trim()) newErrors.numeroNota = 'Número da Nota é obrigatório';
    if (!formData.fornecedorNome.trim()) newErrors.fornecedorNome = 'Fornecedor é obrigatório';
    if (!formData.dataEmissao) newErrors.dataEmissao = 'Data de emissão é obrigatória';
    
    if (formData.cnpjFornecedor && !validateCNPJ(formData.cnpjFornecedor)) {
      newErrors.cnpjFornecedor = 'CNPJ inválido';
    }

    if (formData.itens.length === 0) {
      newErrors.itens = 'A nota deve ter pelo menos um item.';
    } else {
      formData.itens.forEach((item, index) => {
        if (!item.materiaPrimaNome.trim()) newErrors[`item-${index}-materiaPrimaNome`] = 'Nome da matéria-prima é obrigatório';
        if (!item.unidadeMedida.trim()) newErrors[`item-${index}-unidadeMedida`] = 'Unidade de medida é obrigatória';
        if (!item.quantidade || item.quantidade <= 0) newErrors[`item-${index}-quantidade`] = 'Quantidade deve ser maior que zero';
        if (!item.valorUnitario || item.valorUnitario <= 0) newErrors[`item-${index}-valorUnitario`] = 'Valor unitário deve ser maior que zero';
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: string, value: string) => {
    if (field === 'cnpjFornecedor') {
      value = formatCNPJ(value);
    }
    
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const handleItemChange = (index: number, field: string, value: string | number) => {
    const newItems = [...formData.itens];
    newItems[index] = { ...newItems[index], [field]: field === 'quantidade' || field === 'valorUnitario' ? Number(value) : value };

    // Calculate valorTotal for the item
    const qty = newItems[index].quantidade;
    const unitValue = newItems[index].valorUnitario;
    newItems[index].valorTotal = (qty > 0 && unitValue > 0) ? Number((qty * unitValue).toFixed(2)) : 0;

    setFormData((prev) => ({ ...prev, itens: newItems }));
    if (errors[`item-${index}-${field}`]) {
      setErrors((prev) => ({ ...prev, [`item-${index}-${field}`]: '' }));
    }
  };

  const handleAddItem = () => {
    setFormData((prev) => ({
      ...prev,
      itens: [...prev.itens, { 
        id: Date.now().toString(), 
        materiaPrimaNome: '', 
        unidadeMedida: '', 
        quantidade: 0, 
        valorUnitario: 0, 
        valorTotal: 0 
      }],
    }));
  };

  const handleRemoveItem = (index: number) => {
    const newItems = formData.itens.filter((_, i) => i !== index);
    setFormData((prev) => ({ ...prev, itens: newItems }));
    setErrors((prev) => {
      const newErrors = { ...prev };
      Object.keys(newErrors).forEach(key => {
        if (key.startsWith(`item-${index}-`)) {
          delete newErrors[key];
        }
      });
      return newErrors;
    });
  };

  const totalNota = formData.itens.reduce((acc, item) => acc + item.valorTotal, 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);

    try {
      const notaData = {
        numero: formData.numeroNota.trim(),
        serie: "1", // ou outro valor padrão/selecionado
        fornecedor_id: 1, // ID padrão para teste - ajuste conforme necessário
        emissao_date: formData.dataEmissao,
        valor_total: formData.itens.reduce((acc, item) => acc + item.valorTotal, 0),
        itens: formData.itens.map(item => ({
          nome_no_documento: item.materiaPrimaNome,
          unidade_codigo: item.unidadeMedida,
          quantidade: item.quantidade,
          valor_unitario: item.valorUnitario,
          valor_total: item.valorTotal
        }))
      };

      const result = notaId 
        ? await atualizarNotaFiscal(notaId, notaData)
        : await adicionarNotaFiscal(notaData);

      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });

      if (result.success) {
        if (onSalvar && result.data) {
          onSalvar(result.data);
        }
        if (!notaId) {
          // Reset form for new nota
          setFormData({
            numeroNota: '',
            fornecedorNome: '',
            cnpjFornecedor: '',
            enderecoFornecedor: '',
            dataEmissao: '',
            observacoes: '',
            itens: [{ 
              id: Date.now().toString(), 
              materiaPrimaNome: '', 
              unidadeMedida: '', 
              quantidade: 0, 
              valorUnitario: 0, 
              valorTotal: 0 
            }],
          });
        }
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

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/xml', 'application/xml', 'application/pdf'];
    if (!validTypes.includes(file.type) && !file.name.toLowerCase().match(/\.(csv|xlsx|xls|xml|pdf)$/)) {
      setNotification({
        message: 'Tipo de arquivo inválido. Use CSV, XLSX, XLS, XML ou PDF.',
        type: 'error',
      });
      return;
    }

    setImportLoading(true);
    try {
      const result = await importarNotasFiscais(file);
      if (result.success && result.dados) {
        // Preencher o formulário com os dados extraídos do XML
        setFormData(prev => {
          const novosItens = result.dados.itens ? result.dados.itens.map((item: any, index: number) => ({
            id: `xml-${index}`,
            materiaPrimaNome: item.descricao || '',
            unidadeMedida: item.unidade || '',
            quantidade: item.quantidade || 0,
            valorUnitario: item.valor_unitario || 0,
            valorTotal: item.valor_total || 0,
          })) : prev.itens;

          return {
            ...prev,
            numeroNota: result.dados.numero || prev.numeroNota,
            fornecedorNome: result.dados.fornecedor?.nome || prev.fornecedorNome,
            cnpjFornecedor: result.dados.fornecedor?.cnpj || prev.cnpjFornecedor,
            enderecoFornecedor: result.dados.fornecedor?.endereco || prev.enderecoFornecedor,
            dataEmissao: result.dados.emissao_date ? new Date(result.dados.emissao_date).toISOString().split('T')[0] : prev.dataEmissao,
            valorTotal: result.dados.valor_total || prev.valorTotal,
            itens: novosItens,
          };
        });
        
        setNotification({
          message: result.message,
          type: 'success',
        });
      } else {
        setNotification({
          message: result.message,
          type: 'error',
        });
      }
    } catch (error) {
      setNotification({
        message: 'Erro ao processar arquivo.',
        type: 'error',
      });
    } finally {
      setImportLoading(false);
    }
  };

  const handleApiSearch = async () => {
    if (!apiKey.trim()) {
      setNotification({
        message: 'Informe a chave de acesso.',
        type: 'error',
      });
      return;
    }

    setApiLoading(true);
    try {
      const result = await buscarNotaPorChaveAPI(apiKey);
      if (result.success && result.data) {
        setFormData(prev => ({
          ...prev,
          ...result.data,
        }));
        setNotification({
          message: result.message,
          type: 'success',
        });
      } else {
        setNotification({
          message: result.message,
          type: 'error',
        });
      }
    } catch (error) {
      setNotification({
        message: 'Erro ao buscar nota via API.',
        type: 'error',
      });
    } finally {
      setApiLoading(false);
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

      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: 'Notas', onClick: onVoltar },
          { label: notaId ? 'Editar Nota' : 'Nova Nota' },
        ]}
      />

      {/* Steps */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-center space-x-8">
          {[
            { step: 1, label: 'Dados da Nota' },
            { step: 2, label: 'Itens' },
            { step: 3, label: 'Revisão' },
          ].map(({ step, label }) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep >= step
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {step}
              </div>
              <span className={`ml-2 text-sm ${currentStep >= step ? 'text-gray-900' : 'text-gray-500'}`}>
                {label}
              </span>
              {step < 3 && <div className="w-16 h-px bg-gray-300 ml-4" />}
            </div>
          ))}
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            type="button"
            onClick={() => setActiveMode('manual')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeMode === 'manual'
                ? 'bg-red-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Cadastro Manual</span>
            </div>
          </button>
          <button
            type="button"
            onClick={() => setActiveMode('import')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeMode === 'import'
                ? 'bg-red-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Upload className="h-4 w-4" />
              <span>Importar Arquivo</span>
            </div>
          </button>
          <button
            type="button"
            onClick={() => setActiveMode('api')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeMode === 'api'
                ? 'bg-red-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Key className="h-4 w-4" />
              <span>Buscar por API</span>
            </div>
          </button>
        </div>
      </div>

      {/* Import Section */}
      {activeMode === 'import' && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Importar Nota Fiscal
          </h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="text-center">
              {importLoading ? (
                <div className="space-y-4">
                  <Loader2 className="mx-auto h-12 w-12 text-red-500 animate-spin" />
                  <p className="text-sm text-gray-600">Processando arquivo...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="mx-auto h-12 w-12 text-gray-500" />
                  <div>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-red-500 font-medium hover:text-red-400">
                        Selecione um arquivo
                      </span>
                      <span className="text-gray-300"> ou arraste e solte</span>
                    </label>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".csv,.xlsx,.xls,.xml,.pdf"
                      onChange={handleFileUpload}
                      disabled={importLoading}
                    />
                  </div>
                  <p className="text-xs text-gray-400">
                    Arquivos suportados: CSV, XLSX, XLS, XML, PDF (máx. 10MB)
                  </p>
                </div>
              )}
            </div>
          </div>
          
        </div>
      )}

      {/* API Section */}
      {activeMode === 'api' && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Buscar Nota por Chave API
          </h3>
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 mb-2">
                Chave de Acesso
              </label>
              <input
                type="text"
                id="api-key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Digite a chave de acesso da nota fiscal"
                className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <button
              onClick={handleApiSearch}
              disabled={apiLoading}
              className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all"
            >
              {apiLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Buscando...</span>
                </>
              ) : (
                <>
                  <Key className="h-4 w-4" />
                  <span>Buscar Nota</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Form Section */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          Dados da Nota Fiscal
        </h3>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Seção A - Dados da Nota */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Número da Nota */}
            <div>
              <label htmlFor="numeroNota" className="block text-sm font-medium text-gray-700 mb-2">
                Número da Nota *
              </label>
              <input
                type="text"
                id="numeroNota"
                value={formData.numeroNota}
                onChange={(e) => handleInputChange('numeroNota', e.target.value)}
                placeholder="Ex: NF-12345"
                className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                  errors.numeroNota ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.numeroNota && (
                <p className="mt-1 text-sm text-red-600">{errors.numeroNota}</p>
              )}
            </div>

            {/* Fornecedor Nome */}
            <div>
              <label htmlFor="fornecedorNome" className="block text-sm font-medium text-gray-700 mb-2">
                Fornecedor *
              </label>
              <input
                type="text"
                id="fornecedorNome"
                value={formData.fornecedorNome}
                onChange={(e) => handleInputChange('fornecedorNome', e.target.value)}
                placeholder="Ex: Metalúrgica ABC"
                className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                  errors.fornecedorNome ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.fornecedorNome && (
                <p className="mt-1 text-sm text-red-600">{errors.fornecedorNome}</p>
              )}
            </div>

            {/* CNPJ Fornecedor */}
            <div>
              <label htmlFor="cnpjFornecedor" className="block text-sm font-medium text-gray-700 mb-2">
                CNPJ do Fornecedor
              </label>
              <input
                type="text"
                id="cnpjFornecedor"
                value={formData.cnpjFornecedor}
                onChange={(e) => handleInputChange('cnpjFornecedor', e.target.value)}
                placeholder="00.000.000/0000-00"
                className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                  errors.cnpjFornecedor ? 'border-red-500' : 'border-gray-600'
                }`}
              />
              {errors.cnpjFornecedor && (
                <p className="mt-1 text-sm text-red-600">{errors.cnpjFornecedor}</p>
              )}
            </div>

            {/* Endereço Fornecedor */}
            <div>
              <label htmlFor="enderecoFornecedor" className="block text-sm font-medium text-gray-700 mb-2">
                Endereço do Fornecedor
              </label>
              <input
                type="text"
                id="enderecoFornecedor"
                value={formData.enderecoFornecedor}
                onChange={(e) => handleInputChange('enderecoFornecedor', e.target.value)}
                placeholder="Ex: Rua das Flores, 123"
                className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500 ${
                  errors.enderecoFornecedor ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.enderecoFornecedor && (
                <p className="mt-1 text-sm text-red-600">{errors.enderecoFornecedor}</p>
              )}
            </div>
            
            {/* Data de Emissão */}
            <div>
              <label htmlFor="dataEmissao" className="block text-sm font-medium text-gray-700 mb-2">
                Data de Emissão *
              </label>
              <input
                type="date"
                id="dataEmissao"
                value={formData.dataEmissao}
                onChange={(e) => handleInputChange('dataEmissao', e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className={`w-full px-3 py-2 bg-white border rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 ${
                  errors.dataEmissao ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.dataEmissao && (
                <p className="mt-1 text-sm text-red-600">{errors.dataEmissao}</p>
              )}
            </div>

            {/* Valor Total (calculado) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Valor Total
              </label>
              <div className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg text-gray-900 font-medium">
                {formatCurrency(totalNota)}
              </div>
            </div>
          </div>

          {/* Seção B - Itens da Nota */}
          <div className="mt-8">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Itens da Nota Fiscal</h4>
            {errors.itens && (
              <p className="mt-1 text-sm text-red-600 mb-4">{errors.itens}</p>
            )}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Matéria-prima *</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Unidade *</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Menor Unidade</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Quantidade *</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Valor Unitário (R$) *</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Valor Total (R$)</th>
                    <th className="px-3 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">Ações</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {formData.itens.map((item, index) => (
                    <tr key={item.id}>
                      <td className="p-2">
                        <input
                          type="text"
                          value={item.materiaPrimaNome}
                          onChange={(e) => handleItemChange(index, 'materiaPrimaNome', e.target.value)}
                          placeholder="Nome da MP"
                          className={`w-full px-2 py-1 bg-white border rounded-md shadow-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-sm text-gray-900 placeholder-gray-500 ${
                            errors[`item-${index}-materiaPrimaNome`] ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        {errors[`item-${index}-materiaPrimaNome`] && (
                          <p className="mt-1 text-xs text-red-600">{errors[`item-${index}-materiaPrimaNome`]}</p>
                        )}
                      </td>
                      <td className="p-2">
                        <select
                          value={item.unidadeMedida}
                          onChange={e => {
                            handleItemChange(index, 'unidadeMedida', e.target.value);
                            if (e.target.value !== 'outro') setCustomUnidades(prev => ({ ...prev, [index]: '' }));
                          }}
                          className={`w-full px-2 py-1 bg-white border rounded-md shadow-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-sm text-gray-900 ${errors[`item-${index}-unidadeMedida`] ? 'border-red-500' : 'border-gray-300'}`}
                        >
                          <option value="">Selecione</option>
                          {UNIDADES_OPCOES.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                        {item.unidadeMedida === 'outro' && (
                          <input
                            type="text"
                            className="mt-2 w-full px-2 py-1 bg-white border rounded-md shadow-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-sm text-gray-900"
                            placeholder="Digite a unidade personalizada"
                            value={customUnidades[index] || ''}
                            onChange={e => {
                              setCustomUnidades(prev => ({ ...prev, [index]: e.target.value }));
                              handleItemChange(index, 'unidadeMedida', e.target.value);
                            }}
                          />
                        )}
                        {errors[`item-${index}-unidadeMedida`] && (
                          <p className="mt-1 text-xs text-red-600">{errors[`item-${index}-unidadeMedida`]}</p>
                        )}
                      </td>
                      <td className="p-2">
                        {item.menorUnidadeUso ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            {item.menorUnidadeUso}
                          </span>
                        ) : (
                          <span className="text-xs text-gray-500">-</span>
                        )}
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={item.quantidade}
                          onChange={(e) => handleItemChange(index, 'quantidade', e.target.value)}
                          placeholder="0.00"
                          className={`w-full px-2 py-1 bg-white border rounded-md shadow-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-sm text-gray-900 placeholder-gray-500 ${
                            errors[`item-${index}-quantidade`] ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        {errors[`item-${index}-quantidade`] && (
                          <p className="mt-1 text-xs text-red-600">{errors[`item-${index}-quantidade`]}</p>
                        )}
                      </td>
                      <td className="p-2">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={item.valorUnitario}
                          onChange={(e) => handleItemChange(index, 'valorUnitario', e.target.value)}
                          placeholder="0.00"
                          className={`w-full px-2 py-1 bg-white border rounded-md shadow-sm focus:ring-1 focus:ring-red-500 focus:border-red-500 text-sm text-gray-900 placeholder-gray-500 ${
                            errors[`item-${index}-valorUnitario`] ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        {errors[`item-${index}-valorUnitario`] && (
                          <p className="mt-1 text-xs text-red-600">{errors[`item-${index}-valorUnitario`]}</p>
                        )}
                      </td>
                      <td className="p-2 whitespace-nowrap text-sm text-gray-700">
                        {formatCurrency(item.valorTotal)}
                      </td>
                      <td className="p-2 text-right">
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(index)}
                          className="text-red-400 hover:text-red-300 disabled:text-gray-600"
                          disabled={formData.itens.length === 1}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button
              type="button"
              onClick={handleAddItem}
              className="mt-4 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Adicionar Item</span>
            </button>
          </div>

          {/* Observações */}
          <div className="md:col-span-2">
            <label htmlFor="observacoes" className="block text-sm font-medium text-gray-700 mb-2">
              Observações
            </label>
            <textarea
              id="observacoes"
              rows={3}
              value={formData.observacoes}
              onChange={(e) => handleInputChange('observacoes', e.target.value)}
              placeholder="Informações adicionais sobre a compra..."
              className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 placeholder-gray-500"
            />
          </div>

          {/* Seção D - Revisão & Resumo */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="text-lg font-medium text-red-900 mb-4">Resumo da Nota</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-red-700 font-medium">Total de Itens:</span>
                <p className="text-red-900 text-lg font-semibold">{formData.itens.length}</p>
              </div>
              <div>
                <span className="text-red-700 font-medium">Valor Total:</span>
                <p className="text-red-900 text-lg font-semibold">{formatCurrency(totalNota)}</p>
              </div>
              <div>
                <span className="text-red-700 font-medium">Fornecedor:</span>
                <p className="text-red-900">{formData.fornecedorNome || 'Não informado'}</p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-between pt-4">
            <button
              type="button"
              onClick={onVoltar}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Cancelar
            </button>
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Salvando...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>Salvar</span>
                  </>
                )}
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Salvando...</span>
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    <span>Salvar e Baixar</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NotaFiscalForm;
