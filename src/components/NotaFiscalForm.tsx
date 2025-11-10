import React, { useEffect, useState } from 'react';
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
    importarNotasFiscais,
    buscarNotasFiscais
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

  type FormItem = NotaFiscalItem & {
    valorUnitarioTexto?: string;
  };

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
      valorTotal: 0,
      valorUnitarioTexto: ''
    }] as FormItem[],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  type PreviewItem = {
    id: string;
    descricao: string;
    unidade: string;
    quantidade: number;
    valorUnitario: number;
    valorTotal: number;
    valorUnitarioTexto?: string;
  };

  const mapItensParaPreview = (itens: any[] = []): PreviewItem[] => {
    return itens.map((item, index) => {
      const quantidade = parseNumber(item?.quantidade ?? item?.qty ?? item?.qtd);
      const valorUnitario = parseNumber(item?.valor_unitario ?? item?.valorUnitario ?? item?.unit_price);
      const valorTotal =
        parseNumber(item?.valor_total ?? item?.valorTotal ?? item?.amount ?? item?.total) ||
        Number((quantidade * valorUnitario).toFixed(2));

      const quantidadeTexto =
        item?.quantidade_texto ||
        item?.quantidadeTexto ||
        (Number.isFinite(quantidade) && quantidade !== 0 ? quantidade.toString().replace('.', ',') : '');
      const valorUnitarioTexto =
        item?.valor_unitario_texto ||
        item?.valorUnitarioTexto ||
        (Number.isFinite(valorUnitario) && valorUnitario !== 0 ? valorUnitario.toString().replace('.', ',') : '');
      const valorTotalTexto =
        item?.valor_total_texto ||
        item?.valorTotalTexto ||
        (Number.isFinite(valorTotal) && valorTotal !== 0 ? valorTotal.toString().replace('.', ',') : '');

      return {
        id: item?.id ? String(item.id) : `ia-${Date.now()}-${index}`,
        descricao: item?.descricao || item?.materia_prima || '',
        unidade: (item?.unidade || item?.un || item?.unidadeMedida || '').toString(),
        quantidade,
        quantidadeTexto,
        valorUnitario,
        valorUnitarioTexto,
        valorTotal,
        valorTotalTexto,
      };
    });
  };

  const abrirPreviewIA = (payload: any, sessionId?: string) => {
    const itensPreview = mapItensParaPreview(payload?.itens);

    if (!itensPreview.length) {
      setNotification({
        message: 'IA não retornou itens para pré-visualização.',
        type: 'error',
      });
      return;
    }

    setIaPreviewItems(itensPreview);
    setIaPreviewSelection(
      itensPreview.reduce<Record<string, boolean>>((acc, item) => {
        acc[item.id] = true;
        return acc;
      }, {}),
    );

    setIaPreviewMeta({
      numeroNota: payload?.numero_nota,
      fornecedor: payload?.fornecedor,
      cnpj: payload?.cnpj_fornecedor,
      endereco: payload?.endereco,
      dataEmissao: payload?.data_emissao,
      valorTotal: parseNumber(payload?.valor_total),
      sessionId,
      raw: payload,
    });

    setIaPreviewOpen(true);
  };

  const fecharPreviewIA = () => {
    setIaPreviewOpen(false);
  };

  const atualizarItemPreview = (index: number, campo: keyof PreviewItem, valor: string) => {
    setIaPreviewItems((prev) => {
      const updated = [...prev];
      const item = { ...updated[index] };

      const setNumero = (texto: string) => {
        const numero = parseNumber(texto);
        return { numero, texto };
      };

      if (campo === 'descricao' || campo === 'unidade') {
        item[campo] = valor;
      } else if (campo === 'quantidade') {
        const { numero, texto } = setNumero(valor);
        item.quantidade = numero;
        item.quantidadeTexto = texto;
        item.valorTotal = Number((item.quantidade * item.valorUnitario).toFixed(2));
        item.valorTotalTexto =
          item.valorTotal !== 0 ? item.valorTotal.toString().replace('.', ',') : item.valorTotalTexto;
      } else if (campo === 'valorUnitario') {
        const { numero, texto } = setNumero(valor);
        item.valorUnitario = numero;
        item.valorUnitarioTexto = texto;
        item.valorTotal = Number((item.quantidade * item.valorUnitario).toFixed(2));
        item.valorTotalTexto =
          item.valorTotal !== 0 ? item.valorTotal.toString().replace('.', ',') : item.valorTotalTexto;
      } else if (campo === 'valorTotal') {
        const { numero, texto } = setNumero(valor);
        item.valorTotal = numero;
        item.valorTotalTexto = texto;
      }

      updated[index] = item;
      return updated;
    });
  };

  const toggleSelecaoPreview = (id: string) => {
    setIaPreviewSelection((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const selecionarTodosPreview = (valor: boolean) => {
    setIaPreviewSelection(
      iaPreviewItems.reduce<Record<string, boolean>>((acc, item) => {
        acc[item.id] = valor;
        return acc;
      }, {}),
    );
  };

  const aplicarItensSelecionados = () => {
    const selecionados = iaPreviewItems.filter((item) => iaPreviewSelection[item.id]);

    if (!selecionados.length) {
      setNotification({
        message: 'Selecione pelo menos um item para aplicar.',
        type: 'error',
      });
      return;
    }

    setFormData((prev) => ({
      ...prev,
      numeroNota: iaPreviewMeta?.numeroNota || prev.numeroNota,
      fornecedorNome: iaPreviewMeta?.fornecedor || prev.fornecedorNome,
      cnpjFornecedor: iaPreviewMeta?.cnpj || prev.cnpjFornecedor,
      enderecoFornecedor: iaPreviewMeta?.endereco || prev.enderecoFornecedor,
      dataEmissao: iaPreviewMeta?.dataEmissao || prev.dataEmissao,
      itens: selecionados.map((item, index) => ({
        id: `${item.id}-${index}`,
        materiaPrimaNome: item.descricao,
        unidadeMedida: item.unidade || '',
        menorUnidadeUso: item.unidade || '',
        quantidade: Number(item.quantidade.toFixed(4)),
        valorUnitario: Number(item.valorUnitario.toFixed(2)),
        valorUnitarioTexto:
          item.valorUnitarioTexto ??
          (item.valorUnitario !== 0 ? item.valorUnitario.toString().replace('.', ',') : ''),
        valorTotal: Number(item.valorTotal.toFixed(2)),
      })),
    }));

    setIaPreviewOpen(false);
    setNotification({
      message: 'Itens aplicados com sucesso. Revise antes de salvar.',
      type: 'success',
    });
  };
  const [iaPreviewOpen, setIaPreviewOpen] = useState(false);
  const [iaPreviewItems, setIaPreviewItems] = useState<PreviewItem[]>([]);
  const [iaPreviewSelection, setIaPreviewSelection] = useState<Record<string, boolean>>({});
  const [iaPreviewMeta, setIaPreviewMeta] = useState<{
    numeroNota?: string;
    fornecedor?: string;
    cnpj?: string;
    endereco?: string;
    dataEmissao?: string;
    valorTotal?: number;
    sessionId?: string;
    raw?: any;
  } | null>(null);

  // Carregar nota para edição
  useEffect(() => {
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
      itens: nota.itens.map(item => ({
        ...item,
        valorUnitarioTexto: item.valorUnitario !== undefined && item.valorUnitario !== null
          ? item.valorUnitario.toString().replace('.', ',')
          : ''
      })) as FormItem[],
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

  const parseNumber = (value: any): number => {
    if (typeof value === 'number' && !Number.isNaN(value)) return value;
    if (typeof value === 'string') {
      const cleaned = value.replace(/[^\d,.-]/g, '').replace(/\./g, '').replace(',', '.');
      const parsed = Number(cleaned);
      return Number.isNaN(parsed) ? 0 : parsed;
    }
    return 0;
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
      const inputStr = typeof value === 'string' ? value : value.toString();
      const numValue = parseNumber(inputStr);
      newItems[index] = { 
        ...newItems[index], 
        valorUnitario: Number(numValue.toFixed(2)),
        valorUnitarioTexto: inputStr
      };
    } else if (field === 'unidadeMedida') {
      const unidade = typeof value === 'string' ? value : String(value);
      newItems[index] = {
        ...newItems[index],
        unidadeMedida: unidade,
        menorUnidadeUso: unidade || ''
      };
    } else {
      newItems[index] = { ...newItems[index], [field]: field === 'quantidade' ? parseNumber(value) : value };
    }

    // Calculate valorTotal for the item
    const qty = parseNumber(newItems[index].quantidade);
    newItems[index].quantidade = qty;
    const unitValue = parseNumber(newItems[index].valorUnitario);
    newItems[index].valorUnitario = unitValue;
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
        valorTotal: 0,
        valorUnitarioTexto: ''
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
        
        // Recarregar lista de notas fiscais
        try {
          await buscarNotasFiscais({
            page: 1,
            limit: 25,
            busca: '',
            fornecedor: '',
            materiaPrima: '',
            dataInicio: '',
            dataFim: '',
            sortBy: 'dataEmissao',
            sortOrder: 'desc',
          });
        } catch (error) {
          console.error('Erro ao recarregar lista de notas:', error);
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
              valorTotal: 0,
              valorUnitarioTexto: ''
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
          const novosItens = result.dados_extraidos.itens ? result.dados_extraidos.itens.map((item: any, index: number) => {
            const quantidade = parseNumber(item.quantidade);
            const valorUnitario = parseNumber(item.valor_unitario);
            const valorTotal = parseNumber(item.valor_total) || Number((quantidade * valorUnitario).toFixed(2));
            return {
              id: `pdf-${index}`,
              materiaPrimaNome: item.descricao || '',
              unidadeMedida: item.un || '',
              menorUnidadeUso: item.un || '',
              quantidade,
              valorUnitario,
              valorUnitarioTexto: item.valor_unitario !== undefined ? String(item.valor_unitario).replace('.', ',') : '',
              valorTotal,
            };
          }) : prev.itens;

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
    abrirPreviewIA(data);
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
        abrirPreviewIA(result.dados_extraidos, result.session_id);
        setNotification({
          message: result.message ?? 'PDF processado com IA! Revise os dados extraídos.',
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
        abrirPreviewIA(result.dados_extraidos, result.session_id);
        setNotification({
          message: result.message ?? 'PDF processado com IA! Revise os dados extraídos.',
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
                          type="text"
                          inputMode="decimal"
                          value={
                            item.valorUnitarioTexto !== undefined
                              ? item.valorUnitarioTexto
                              : item.valorUnitario.toFixed(2).replace('.', ',')
                          }
                          onChange={(e) => handleItemChange(index, 'valorUnitario', e.target.value)}
                          placeholder="0,00"
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
      {iaPreviewOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-5xl bg-white rounded-lg shadow-xl overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Pré-visualização dos itens extraídos</h3>
                <p className="text-sm text-gray-600">
                  Revise, ajuste e selecione os itens antes de importar para a nota fiscal.
                </p>
              </div>
              <button
                onClick={fecharPreviewIA}
                className="text-gray-500 hover:text-gray-800 transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="px-6 py-4 border-b grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-gray-700">
              <div>
                <span className="font-medium text-gray-900">Número NF:</span>{' '}
                {iaPreviewMeta?.numeroNota || '—'}
              </div>
              <div>
                <span className="font-medium text-gray-900">Fornecedor:</span>{' '}
                {iaPreviewMeta?.fornecedor || '—'}
              </div>
              <div>
                <span className="font-medium text-gray-900">Data emissão:</span>{' '}
                {iaPreviewMeta?.dataEmissao || '—'}
              </div>
              <div>
                <span className="font-medium text-gray-900">CNPJ:</span>{' '}
                {iaPreviewMeta?.cnpj || '—'}
              </div>
              <div className="md:col-span-2">
                <span className="font-medium text-gray-900">Endereço:</span>{' '}
                {iaPreviewMeta?.endereco || '—'}
              </div>
            </div>

            <div className="px-6 py-4">
              <div className="flex items-center justify-between mb-3 text-sm">
                <span className="text-gray-600">
                  {Object.values(iaPreviewSelection).filter(Boolean).length} de {iaPreviewItems.length} itens selecionados
                </span>
                <div className="space-x-2">
                  <button
                    onClick={() => selecionarTodosPreview(true)}
                    className="px-3 py-1 rounded-md border border-gray-300 hover:bg-gray-100 transition-colors"
                  >
                    Selecionar todos
                  </button>
                  <button
                    onClick={() => selecionarTodosPreview(false)}
                    className="px-3 py-1 rounded-md border border-gray-300 hover:bg-gray-100 transition-colors"
                  >
                    Limpar seleção
                  </button>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2"></th>
                      <th className="px-3 py-2 text-left font-semibold text-gray-600">Descrição</th>
                      <th className="px-3 py-2 text-left font-semibold text-gray-600">Unidade</th>
                      <th className="px-3 py-2 text-right font-semibold text-gray-600">Quantidade</th>
                      <th className="px-3 py-2 text-right font-semibold text-gray-600">Valor Unitário (R$)</th>
                      <th className="px-3 py-2 text-right font-semibold text-gray-600">Valor Total (R$)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {iaPreviewItems.map((item, index) => (
                      <tr key={item.id} className={!iaPreviewSelection[item.id] ? 'bg-gray-50' : ''}>
                        <td className="px-3 py-2">
                          <input
                            type="checkbox"
                            className="h-4 w-4 text-red-600 rounded border-gray-300 focus:ring-red-500"
                            checked={Boolean(iaPreviewSelection[item.id])}
                            onChange={() => toggleSelecaoPreview(item.id)}
                          />
                        </td>
                        <td className="px-3 py-2">
                          <input
                            type="text"
                            value={item.descricao}
                            onChange={(e) => atualizarItemPreview(index, 'descricao', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-red-500 focus:border-red-500"
                          />
                        </td>
                        <td className="px-3 py-2">
                          <input
                            type="text"
                            value={item.unidade}
                            onChange={(e) => atualizarItemPreview(index, 'unidade', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-red-500 focus:border-red-500"
                          />
                        </td>
                        <td className="px-3 py-2">
                          <input
                            type="text"
                            inputMode="decimal"
                            value={
                              item.quantidadeTexto !== undefined
                                ? item.quantidadeTexto
                                : item.quantidade.toString().replace('.', ',')
                            }
                            onChange={(e) => atualizarItemPreview(index, 'quantidade', e.target.value)}
                            className="w-full text-right px-2 py-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-red-500 focus:border-red-500"
                          />
                        </td>
                        <td className="px-3 py-2">
                          <input
                            type="text"
                            inputMode="decimal"
                            value={
                              item.valorUnitarioTexto !== undefined
                                ? item.valorUnitarioTexto
                                : item.valorUnitario.toString().replace('.', ',')
                            }
                            onChange={(e) => atualizarItemPreview(index, 'valorUnitario', e.target.value)}
                            className="w-full text-right px-2 py-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-red-500 focus:border-red-500"
                          />
                        </td>
                        <td className="px-3 py-2">
                          <input
                            type="text"
                            inputMode="decimal"
                            value={
                              item.valorTotalTexto !== undefined
                                ? item.valorTotalTexto
                                : item.valorTotal.toString().replace('.', ',')
                            }
                            onChange={(e) => atualizarItemPreview(index, 'valorTotal', e.target.value)}
                            className="w-full text-right px-2 py-1 border border-gray-300 rounded-md focus:ring-1 focus:ring-red-500 focus:border-red-500"
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="px-6 py-4 border-t bg-gray-50 flex items-center justify-between">
              <button
                onClick={fecharPreviewIA}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800"
              >
                Cancelar
              </button>
              <button
                onClick={aplicarItensSelecionados}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors"
              >
                Aplicar itens selecionados
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotaFiscalForm;
