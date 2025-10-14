import React, { useState } from 'react';
import { Bot, Loader2, X } from 'lucide-react';

interface IAAssistantProps {
  file: File;
  onSuccess: (data: any) => void;
  onClose: () => void;
}

const IAAssistant: React.FC<IAAssistantProps> = ({ file, onSuccess, onClose }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const handleProcessWithIA = async () => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://127.0.0.1:8000/uploads-ia/processar-pdf', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      console.log('=== RESULTADO DA IA ===');
      console.log('Response status:', response.status);
      console.log('Result completo:', result);
      console.log('Success:', result.success);
      console.log('Dados extraídos:', result.dados_extraidos);
      console.log('=== FIM RESULTADO ===');
      
      if (result.success && result.dados_extraidos) {
        console.log('Chamando onSuccess com:', result.dados_extraidos);
        onSuccess(result.dados_extraidos);
        setNotification({
          message: 'PDF processado com IA! Revise os dados extraídos.',
          type: 'success',
        });
      } else {
        console.log('Erro no processamento:', result.message);
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
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center space-x-2">
            <Bot className="h-5 w-5 text-blue-600" />
            <span>Assistente IA</span>
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            Arquivo: <span className="font-medium">{file.name}</span>
          </p>
          <p className="text-sm text-gray-600">
            Use IA para extrair dados de PDFs que não foram lidos automaticamente.
          </p>
        </div>


        {notification && (
          <div className={`p-3 rounded-md mb-4 ${
            notification.type === 'success' 
              ? 'bg-green-50 text-green-700 border border-green-200' 
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {notification.message}
          </div>
        )}

        <div className="flex space-x-3">
          <button
            onClick={handleProcessWithIA}
            disabled={isProcessing}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Processando...</span>
              </>
            ) : (
              <>
                <Bot className="h-4 w-4" />
                <span>Processar com IA</span>
              </>
            )}
          </button>
          <button
            onClick={onClose}
            className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default IAAssistant;
