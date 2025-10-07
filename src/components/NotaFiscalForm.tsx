import React, { useState } from 'react';
import { Save, Upload, Loader2, Plus, Trash2, Download, Bot } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { NotaFiscal, NotaFiscalItem } from '../types';
import { formatCNPJ, validateCNPJ, formatCurrency } from '../utils/formatters';
import Breadcrumb from './ui/Breadcrumb';
import NotificationToast from './NotificationToast';
import IAAssistant from './IAAssistant';

interface NotaFiscalFormProps {
  notaId?: string;
  onVoltar: () => void;
  onSalvar?: (nota: NotaFiscal) => void;
}

const UNIDADES_OPCOES = [
  { value: 'KG', label: 'Quilo (KG)' },
  { value: 'G', label: 'Grama (G)' },
  { value: 'L', label: 'Litro (L)' },
  { value: 'ML', label: 'Mililitro (ML)' },
  { value: 'M', label: 'Metro (M)' },
  { value: 'CM', label: 'Centímetro (CM)' },
  { value: 'UN', label: 'Unidade (UN)' },
  { value: 'CX', label: 'Caixa (CX)' },
  { value: 'PC', label: 'Peça (PC)' },
  { value: 'ROLO', label: 'Rolo (ROLO)' },
  { value: 'BOBINA', label: 'Bobina (BOBINA)' },
  { value: 'FARDO', label: 'Fardo (FARDO)' },
  { value: 'PACOTE', label: 'Pacote (PACOTE)' },
  { value: 'outro', label: 'Outra...' },
];

const NotaFiscalForm: React.FC<NotaFiscalFormProps> = ({ notaId, onVoltar, onSalvar }) => {
  const { 
    adicionarNotaFiscal, 
    atualizarNotaFiscal, 
    obterNotaFiscal,
    importarNotasFiscais
  } = useApp();
  
  const [activeMode, setActiveMode] = useState<'import'>('import');
  const [loading, setLoading] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [isProcessingIA, setIsProcessingIA] = useState(false);
  const [uploadMethod, setUploadMethod] = useState<'normal' | 'ia' | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [customUnidades, setCustomUnidades] = useState<{[key: number]: string}>({});
  const [showIA, setShowIA] = useState(false);
  const [fileForIA, setFileForIA] = useState<File | null>(null);

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
    
    // Formatar valor unitário para 2 casas decimais
    if (field === 'valorUnitario') {
      const numValue = Number(value);
      newItems[index] = { ...newItems[index], [field]: Number(numValue.toFixed(2)) };
    } else {
      newItems[index] = { ...newItems[index], [field]: field === 'quantidade' ? Number(value) : value };
    }

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
        fornecedor_id: 39, // Usar o ID real do fornecedor padrão criado
        emissao_date: formData.dataEmissao || new Date().toISOString().split('T')[0], // Data atual se não preenchida
        valor_total: formData.itens.reduce((acc, item) => acc + item.valorTotal, 0),
        itens: formData.itens.map(item => ({
          nome_no_documento: item.materiaPrimaNome,
          unidade_codigo: item.unidadeMedida.toLowerCase(), // Converter para minúsculo
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
      if (result.success && result.dados_extraidos) {
        // Preencher o formulário com os dados extraídos do XML
        setFormData(prev => {
          const novosItens = result.dados_extraidos.itens ? result.dados_extraidos.itens.map((item: any, index: number) => ({
            id: `pdf-${index}`,
            materiaPrimaNome: item.descricao || '',
            unidadeMedida: item.un || '',  // Mapear diretamente a unidade do PDF
            menorUnidadeUso: item.un || '',  // Mostrar a unidade na coluna Menor Unidade
            quantidade: item.quantidade || 0,
            valorUnitario: Number((item.valor_unitario || 0).toFixed(2)),
            valorTotal: Number((item.valor_total || 0).toFixed(2)),
          })) : prev.itens;

          return {
            ...prev,
            numeroNota: result.dados_extraidos.numero_nota || prev.numeroNota,
            fornecedorNome: result.dados_extraidos.fornecedor || prev.fornecedorNome,
            cnpjFornecedor: result.dados_extraidos.cnpj_fornecedor || prev.cnpjFornecedor,
            enderecoFornecedor: result.dados_extraidos.endereco_fornecedor || prev.enderecoFornecedor,
            dataEmissao: result.dados_extraidos.data_emissao || prev.dataEmissao,
            valorTotal: result.dados_extraidos.valor_total || prev.valorTotal,
            itens: novosItens,
          };
        });
        
        setNotification({
          message: result.message,
          type: 'success',
        });
      } else {
        // Se falhou, mostrar opção de IA
        setFileForIA(file);
        setShowIA(true);
        setNotification({
          message: 'Upload falhou. Use o assistente IA para extrair os dados.',
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

  const handleIASuccess = (data: any) => {
    console.log('=== HANDLE IA SUCCESS ===');
    console.log('Dados recebidos:', data);
    console.log('=== FIM HANDLE IA SUCCESS ===');
    
    setFormData(prev => {
      const novosItens = data.itens ? data.itens.map((item: any, index: number) => ({
        id: `ai-${index}`,
        materiaPrimaNome: item.descricao || item.materia_prima || '',
        unidadeMedida: item.unidade || item.un || '',
        menorUnidadeUso: item.unidade || item.un || '',
        quantidade: item.quantidade || 0,
        valorUnitario: Number((item.valor_unitario || item.valorUnitario || 0).toFixed(2)),
        valorTotal: Number((item.valor_total || item.valorTotal || 0).toFixed(2)),
      })) : prev.itens;

      return {
        ...prev,
        numeroNota: data.numero_nota || prev.numeroNota,
        fornecedorNome: data.fornecedor || prev.fornecedorNome,
        cnpjFornecedor: data.cnpj_fornecedor || prev.cnpjFornecedor,
        enderecoFornecedor: data.endereco || prev.enderecoFornecedor,
        dataEmissao: data.data_emissao || prev.dataEmissao,
        valorTotal: data.valor_total || prev.valorTotal,
        itens: novosItens,
      };
    });
    
    console.log('=== FORM DATA ATUALIZADO ===');
    console.log('Novos dados aplicados ao formulário');
    console.log('=== FIM FORM DATA ===');
    
    setShowIA(false);
    setFileForIA(null);
  };

  const handleUploadWithIA = async () => {
    if (!selectedFile) return;

    setIsProcessingIA(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch('http://127.0.0.1:8000/uploads-ia/processar-pdf', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success && result.dados_extraidos) {
        // Preencher os campos com os dados extraídos pela IA
        setFormData(prev => {
          const novosItens = result.dados_extraidos.itens ? result.dados_extraidos.itens.map((item: any, index: number) => ({
            id: `ai-${index}`,
            materiaPrimaNome: item.descricao || item.materia_prima || '',
            unidadeMedida: item.unidade || item.un || '',
            menorUnidadeUso: item.unidade || item.un || '',
            quantidade: item.quantidade || 0,
            valorUnitario: Number((item.valor_unitario || item.valorUnitario || 0).toFixed(2)),
            valorTotal: Number((item.valor_total || item.valorTotal || 0).toFixed(2)),
          })) : prev.itens;

          return {
            ...prev,
            numeroNota: result.dados_extraidos.numero_nota || prev.numeroNota,
            fornecedorNome: result.dados_extraidos.fornecedor || prev.fornecedorNome,
            cnpjFornecedor: result.dados_extraidos.cnpj_fornecedor || prev.cnpjFornecedor,
            enderecoFornecedor: result.dados_extraidos.endereco || prev.enderecoFornecedor,
            dataEmissao: result.dados_extraidos.data_emissao || prev.dataEmissao,
            valorTotal: result.dados_extraidos.valor_total || prev.valorTotal,
            itens: novosItens,
          };
        });
        
        setNotification({
          message: 'PDF processado com IA! Revise os dados extraídos.',
          type: 'success',
        });
        setUploadMethod(null);
        setSelectedFile(null);
      } else {
        setNotification({
          message: `Erro ao processar com IA: ${result.message}`,
          type: 'error',
        });
      }
    } catch (error) {
      setNotification({
        message: 'Erro ao conectar com o servidor IA',
        type: 'error',
      });
    } finally {
      setIsProcessingIA(false);
    }
  };

  const resetUploadMethod = () => {
    setUploadMethod(null);
    setSelectedFile(null);
  };

  const handleFileUploadWithIA = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setNotification({
        message: 'Para usar IA, selecione apenas arquivos PDF.',
        type: 'error',
      });
      return;
    }

    setIsProcessingIA(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://127.0.0.1:8000/uploads-ia/processar-pdf', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success && result.dados_extraidos) {
        // Preencher os campos com os dados extraídos pela IA
        setFormData(prev => {
          const novosItens = result.dados_extraidos.itens ? result.dados_extraidos.itens.map((item: any, index: number) => ({
            id: `ai-${index}`,
            materiaPrimaNome: item.descricao || item.materia_prima || '',
            unidadeMedida: item.unidade || item.un || '',
            menorUnidadeUso: item.unidade || item.un || '',
            quantidade: item.quantidade || 0,
            valorUnitario: Number((item.valor_unitario || item.valorUnitario || 0).toFixed(2)),
            valorTotal: Number((item.valor_total || item.valorTotal || 0).toFixed(2)),
          })) : prev.itens;

          return {
            ...prev,
            numeroNota: result.dados_extraidos.numero_nota || prev.numeroNota,
            fornecedorNome: result.dados_extraidos.fornecedor || prev.fornecedorNome,
            cnpjFornecedor: result.dados_extraidos.cnpj_fornecedor || prev.cnpjFornecedor,
            enderecoFornecedor: result.dados_extraidos.endereco || prev.enderecoFornecedor,
            dataEmissao: result.dados_extraidos.data_emissao || prev.dataEmissao,
            valorTotal: result.dados_extraidos.valor_total || prev.valorTotal,
            itens: novosItens,
          };
        });
        
        setNotification({
          message: 'PDF processado com IA! Revise os dados extraídos.',
          type: 'success',
        });
      } else {
        setNotification({
          message: `Erro ao processar com IA: ${result.message}`,
          type: 'error',
        });
      }
    } catch (error) {
      setNotification({
        message: 'Erro ao conectar com o servidor IA',
        type: 'error',
      });
    } finally {
      setIsProcessingIA(false);
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

      {/* Mode Toggle - Apenas Importar Arquivo */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
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
        </div>

        {activeMode === 'import' && (
          <div className="mt-6 space-y-4">
            {/* Upload de arquivo */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Upload Normal */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-red-400 transition-colors">
                <input
                  type="file"
                  id="file-upload"
                  onChange={handleFileUpload}
                  accept=".csv,.xlsx,.xls,.xml,.pdf"
                  className="hidden"
                  disabled={importLoading}
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center space-y-2"
                >
                  {importLoading ? (
                    <Loader2 className="h-8 w-8 text-red-600 animate-spin" />
                  ) : (
                    <Upload className="h-8 w-8 text-gray-400" />
                  )}
                  <span className="text-sm font-medium text-gray-700">
                    {importLoading ? 'Processando...' : 'Upload Normal'}
                  </span>
                  <span className="text-xs text-gray-500">
                    CSV, XLSX, XLS, XML, PDF
                  </span>
                </label>
              </div>

              {/* Upload com IA */}
              <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors bg-blue-50">
                <input
                  type="file"
                  id="file-upload-ia"
                  onChange={handleFileUploadWithIA}
                  accept=".pdf"
                  className="hidden"
                  disabled={isProcessingIA}
                />
                <label
                  htmlFor="file-upload-ia"
                  className="cursor-pointer flex flex-col items-center space-y-2"
                >
                  {isProcessingIA ? (
                    <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
                  ) : (
                    <Bot className="h-8 w-8 text-blue-500" />
                  )}
                  <span className="text-sm font-medium text-blue-700">
                    {isProcessingIA ? 'Processando com IA...' : '🤖 Upload com IA'}
                  </span>
                  <span className="text-xs text-blue-600">
                    PDFs complexos ou que falharam
                  </span>
                </label>
              </div>
            </div>

            {/* Botão IA quando upload normal falha */}
            {uploadMethod === 'normal' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-blue-900">Upload falhou</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      Tente usar IA para extrair dados de PDFs complexos
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleUploadWithIA}
                      disabled={isProcessingIA}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {isProcessingIA ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>Processando...</span>
                        </>
                      ) : (
                        <>
                          <Bot className="h-4 w-4" />
                          <span>🤖 Tentar com IA</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={resetUploadMethod}
                      className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

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
                          value={item.valorUnitario.toFixed(2)}
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
      {showIA && fileForIA && (
        <IAAssistant
          file={fileForIA}
          onSuccess={handleIASuccess}
          onClose={() => {
            setShowIA(false);
            setFileForIA(null);
          }}
        />
      )}
    </div>
  );
};

export default NotaFiscalForm;
