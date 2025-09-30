import React, { useState } from 'react';
import Layout from './components/Layout';
import NotaFiscalList from './components/NotaFiscalList';
import NotaFiscalForm from './components/NotaFiscalForm';
import HistoricoPrecos from './components/HistoricoPrecos';
import CrudMateriasPrimas from './components/CrudMateriasPrimas';
// import CrudFornecedores from './components/CrudFornecedores'; // Oculto temporariamente
import CrudProdutos from './components/CrudProdutos';
import { AppProvider } from './context/AppContext';

function App() {
  const [activeTab, setActiveTab] = useState<'produtos' | 'cadastro' | 'historico' | 'notas' | 'materias'>('produtos');
  const [notaEditandoId, setNotaEditandoId] = useState<string | undefined>();

  const handleNovaNotaClick = () => {
    setNotaEditandoId(undefined);
    setActiveTab('cadastro');
  };

  const handleEditarNota = (id: string) => {
    setNotaEditandoId(id);
    setActiveTab('cadastro');
  };

  const handleVerNota = (id: string) => {
    // TODO: Implementar tela de detalhes
    console.log('Ver nota:', id);
  };

  const handleVoltarParaLista = () => {
    setNotaEditandoId(undefined);
    setActiveTab('notas');
  };
  return (
    <AppProvider>
      <Layout activeTab={activeTab} onTabChange={setActiveTab}>
        {activeTab === 'notas' && (
          <NotaFiscalList 
            onNovaNota={handleNovaNotaClick}
            onEditarNota={handleEditarNota}
            onVerNota={handleVerNota}
          />
        )}
        {activeTab === 'cadastro' && (
          <NotaFiscalForm 
            notaId={notaEditandoId}
            onVoltar={handleVoltarParaLista}
          />
        )}
                {activeTab === 'historico' && <HistoricoPrecos />}
                {activeTab === 'materias' && <CrudMateriasPrimas />}
                {/* {activeTab === 'fornecedores' && <CrudFornecedores />} */}
                {activeTab === 'produtos' && <CrudProdutos />}
      </Layout>
    </AppProvider>
  );
}

export default App;