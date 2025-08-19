import React, { useState } from 'react';
import Layout from './components/Layout';
import NotaFiscalForm from './components/NotaFiscalForm';
import HistoricoPrecos from './components/HistoricoPrecos';
import CrudMateriasPrimas from './components/CrudMateriasPrimas';
import CrudFornecedores from './components/CrudFornecedores';
import CrudProdutos from './components/CrudProdutos';
import { AppProvider } from './context/AppContext';

function App() {
  const [activeTab, setActiveTab] = useState<'cadastro' | 'historico' | 'materias' | 'fornecedores' | 'produtos'>('materias');

  return (
    <AppProvider>
      <Layout activeTab={activeTab} onTabChange={setActiveTab}>
        {activeTab === 'cadastro' && <NotaFiscalForm />}
        {activeTab === 'historico' && <HistoricoPrecos />}
        {activeTab === 'materias' && <CrudMateriasPrimas />}
        {activeTab === 'fornecedores' && <CrudFornecedores />}
        {activeTab === 'produtos' && <CrudProdutos />}
      </Layout>
    </AppProvider>
  );
}

export default App;