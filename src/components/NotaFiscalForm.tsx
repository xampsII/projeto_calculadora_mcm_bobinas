import React, { useState } from 'react';
import { Save, Upload, FileText, Loader2 } from 'lucide-react';
import { useApp } from '../context/AppContext';
import NotificationToast from './NotificationToast';

const NotaFiscalForm: React.FC = () => {
  const { materiasPrimas, fornecedores, adicionarNotaFiscal } = useApp();
  const [activeMode, setActiveMode] = useState<'manual' | 'import'>('manual');
  const [loading, setLoading] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [formData, setFormData] = useState({
    materiaPrimaId: '',
    quantidade: '',
    valorUnitario: '',
    dataCompra: '',
    fornecedorId: '',
    observacoes: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.materiaPrimaId) newErrors.materiaPrimaId = 'Matéria-prima é obrigatória';
    if (!formData.quantidade) newErrors.quantidade = 'Quantidade é obrigatória';
    else if (parseFloat(formData.quantidade) <= 0) newErrors.quantidade = 'Quantidade deve ser maior que zero';
    if (!formData.valorUnitario) newErrors.valorUnitario = 'Valor unitário é obrigatório';
    else if (parseFloat(formData.valorUnitario) <= 0) newErrors.valorUnitario = 'Valor deve ser maior que zero';
    if (!formData.dataCompra) newErrors.dataCompra = 'Data da compra é obrigatória';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      const materiaPrima = materiasPrimas.find(m => m.id === formData.materiaPrimaId);
      const fornecedor = fornecedores.find(f => f.id === formData.fornecedorId);
      
      if (!materiaPrima) {
        setNotification({
          message: 'Matéria-prima não encontrada.',
          type: 'error',
        });
        return;
      }

      const result = await adicionarNotaFiscal({
        materiaPrimaId: formData.materiaPrimaId,
        materiaPrimaNome: materiaPrima.nome,
        quantidade: parseFloat(formData.quantidade),
        unidadeCompra: materiaPrima.unidadeCompra,
        valorUnitario: parseFloat(formData.valorUnitario),
        valorTotal: parseFloat(formData.quantidade) * parseFloat(formData.valorUnitario),
        dataCompra: formData.dataCompra,
        fornecedorId: formData.fornecedorId || undefined,
        fornecedorNome: fornecedor?.nome,
        observacoes: formData.observacoes.trim() || undefined,
      });

      setNotification({
        message: result.message,
        type: result.success ? 'success' : 'error',
      });

      if (result.success) {
        setFormData({
          materiaPrimaId: '',
          quantidade: '',
          valorUnitario: '',
          dataCompra: '',
          fornecedorId: '',
          observacoes: '',
        });
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

  const simulateFileImport = async (file: File) => {
    setImportLoading(true);
    
    // Simular leitura de arquivo
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simular dados extraídos do arquivo
    const mockData = {
      materiaPrimaId: '1', // Aço Carbono 1020
      quantidade: '750',
      valorUnitario: '2.75',
      dataCompra: '2024-01-25',
      fornecedorId: '1', // Metalúrgica Santos Ltda
      observacoes: 'Importado automaticamente do arquivo',
    };

    setFormData(mockData);
    setImportLoading(false);
    
    setNotification({
      message: `Arquivo "${file.name}" processado com sucesso! Verifique os dados e confirme.`,
      type: 'success',
    });
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['application/pdf', 'application/xml', 'text/xml', 'application/json'];
      if (!validTypes.some(type => file.type === type || file.name.toLowerCase().endsWith('.pdf') || file.name.toLowerCase().endsWith('.xml') || file.name.toLowerCase().endsWith('.json'))) {
        setNotification({
          message: 'Tipo de arquivo inválido. Use PDF, XML ou JSON.',
          type: 'error',
        });
        return;
      }
      simulateFileImport(file);
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

      {/* Mode Toggle */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            type="button"
            onClick={() => setActiveMode('manual')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeMode === 'manual'
                ? 'bg-white text-gray-900 shadow-sm'
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
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Upload className="h-4 w-4" />
              <span>Importar Arquivo</span>
            </div>
          </button>
        </div>
      </div>

      {/* Import Section */}
      {activeMode === 'import' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Importar Nota Fiscal
          </h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <div className="text-center">
              {importLoading ? (
                <div className="space-y-4">
                  <Loader2 className="mx-auto h-12 w-12 text-orange-600 animate-spin" />
                  <p className="text-sm text-gray-600">Processando arquivo...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="text-orange-600 font-medium hover:text-orange-700">
                        Selecione um arquivo
                      </span>
                      <span className="text-gray-600"> ou arraste e solte</span>
                    </label>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept=".pdf,.xml,.json"
                      onChange={handleFileUpload}
                      disabled={importLoading}
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    Arquivos suportados: PDF, XML, JSON (máx. 10MB)
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Form Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          {activeMode === 'manual' ? 'Dados da Nota Fiscal' : 'Confirmar Dados Importados'}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matéria-prima */}
            <div>
              <label htmlFor="materiaPrimaId" className="block text-sm font-medium text-gray-700 mb-2">
                Matéria-prima *
              </label>
              <select
                id="materiaPrimaId"
                value={formData.materiaPrimaId}
                onChange={(e) => handleInputChange('materiaPrimaId', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.materiaPrimaId ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Selecione uma matéria-prima</option>
                {materiasPrimas.map((materia) => (
                  <option key={materia.id} value={materia.id}>
                    {materia.nome} ({materia.unidadeCompra})
                  </option>
                ))}
              </select>
              {errors.materiaPrimaId && (
                <p className="mt-1 text-sm text-red-600">{errors.materiaPrimaId}</p>
              )}
            </div>

            {/* Fornecedor */}
            <div>
              <label htmlFor="fornecedorId" className="block text-sm font-medium text-gray-700 mb-2">
                Fornecedor
              </label>
              <select
                id="fornecedorId"
                value={formData.fornecedorId}
                onChange={(e) => handleInputChange('fornecedorId', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.fornecedorId ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Selecione um fornecedor (opcional)</option>
                {fornecedores.map((fornecedor) => (
                  <option key={fornecedor.id} value={fornecedor.id}>
                    {fornecedor.nome}
                  </option>
                ))}
              </select>
              {errors.fornecedorId && (
                <p className="mt-1 text-sm text-red-600">{errors.fornecedorId}</p>
              )}
            </div>

            {/* Quantidade */}
            <div>
              <label htmlFor="quantidade" className="block text-sm font-medium text-gray-700 mb-2">
                Quantidade * 
                {formData.materiaPrimaId && (
                  <span className="text-gray-500 font-normal">
                    ({materiasPrimas.find(m => m.id === formData.materiaPrimaId)?.unidadeCompra})
                  </span>
                )}
              </label>
              <input
                type="number"
                id="quantidade"
                step="0.01"
                min="0"
                value={formData.quantidade}
                onChange={(e) => handleInputChange('quantidade', e.target.value)}
                placeholder="0.00"
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.quantidade ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.quantidade && (
                <p className="mt-1 text-sm text-red-600">{errors.quantidade}</p>
              )}
            </div>

            {/* Valor Unitário */}
            <div>
              <label htmlFor="valorUnitario" className="block text-sm font-medium text-gray-700 mb-2">
                Valor Unitário (R$) *
              </label>
              <input
                type="number"
                id="valorUnitario"
                step="0.01"
                min="0"
                value={formData.valorUnitario}
                onChange={(e) => handleInputChange('valorUnitario', e.target.value)}
                placeholder="0.00"
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.valorUnitario ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.valorUnitario && (
                <p className="mt-1 text-sm text-red-600">{errors.valorUnitario}</p>
              )}
            </div>

            {/* Data da Compra */}
            <div>
              <label htmlFor="dataCompra" className="block text-sm font-medium text-gray-700 mb-2">
                Data da Compra *
              </label>
              <input
                type="date"
                id="dataCompra"
                value={formData.dataCompra}
                onChange={(e) => handleInputChange('dataCompra', e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className={`w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.dataCompra ? 'border-red-300' : 'border-gray-300'
                }`}
              />
              {errors.dataCompra && (
                <p className="mt-1 text-sm text-red-600">{errors.dataCompra}</p>
              )}
            </div>

            {/* Valor Total (calculado) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Valor Total
              </label>
              <div className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg">
                R$ {formData.quantidade && formData.valorUnitario 
                  ? (parseFloat(formData.quantidade) * parseFloat(formData.valorUnitario)).toFixed(2).replace('.', ',')
                  : '0,00'
                }
              </div>
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>

          {/* Informações de Conversão */}
          {formData.materiaPrimaId && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              {(() => {
                const materia = materiasPrimas.find(m => m.id === formData.materiaPrimaId);
                if (!materia) return null;
                
                const valorConvertido = formData.valorUnitario ? 
                  (parseFloat(formData.valorUnitario) / materia.fatorConversao).toFixed(4) : '0,0000';
                
                return (
                  <div>
                    <h4 className="text-sm font-medium text-orange-900 mb-2">
                      Informações de Conversão
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-orange-700 font-medium">Unidade de Compra:</span>
                        <p className="text-orange-900">{materia.unidadeCompra}</p>
                      </div>
                      <div>
                        <span className="text-orange-700 font-medium">Unidade de Uso:</span>
                        <p className="text-orange-900">{materia.unidadeUso}</p>
                      </div>
                      <div>
                        <span className="text-orange-700 font-medium">Fator de Conversão:</span>
                        <p className="text-orange-900">1 {materia.unidadeCompra} = {materia.fatorConversao} {materia.unidadeUso}</p>
                      </div>
                      {formData.valorUnitario && (
                        <div className="md:col-span-3">
                          <span className="text-orange-700 font-medium">Custo por {materia.unidadeUso}:</span>
                          <p className="text-orange-900 font-semibold">R$ {valorConvertido.replace('.', ',')}</p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 disabled:from-gray-400 disabled:to-gray-400 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 transition-all shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Salvando...</span>
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  <span>
                    {activeMode === 'manual' ? 'Salvar Nota Fiscal' : 'Confirmar Atualização'}
                  </span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NotaFiscalForm;