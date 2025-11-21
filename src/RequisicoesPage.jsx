import React, { useState, useEffect } from 'react';
import './App.css';

function RequisicoesPage({ onBack }) {
  const [requisicoes, setRequisicoes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdate, setLastUpdate] = useState(null);

  // Função para buscar requisições pendentes
  const fetchRequisicoes = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log('Buscando requisições pendentes...');
      
      // Implementar timeout de 10 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.log('[REQUISICOES] Timeout da requisição');
      }, 10000);
      
      // Usar o proxy do Vite para requisições (como no App.jsx)
      const response = await fetch('/api/requisicoes_pendentes', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setRequisicoes(data.requisicoes || []);
        setLastUpdate(new Date().toLocaleString('pt-BR'));
        console.log(`Carregadas ${data.total} requisições pendentes`);
      } else {
        throw new Error(data.erro || 'Erro desconhecido');
      }
      
    } catch (err) {
      console.error('Erro ao buscar requisições:', err);
      setError(`Erro ao carregar requisições: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Carregar requisições ao montar o componente
  useEffect(() => {
    fetchRequisicoes();
  }, []);



  // Função para formatar quantidade
  const formatQuantidade = (quantidade) => {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 3
    }).format(quantidade);
  };

  const transferirMaterial = async (codigo) => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Faça login primeiro!');
      return;
    }
  
    try {
      const response = await fetch('/api/transferencia_material', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`  // Adição minimalista: Envia o token JWT
        },
        body: JSON.stringify({ codigo })
      });
  
      if (!response.ok) {
        throw new Error('Erro na transferência');
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <button 
          className="back-button"
          onClick={onBack}
          title="Voltar para tela principal"
        >
          ← Voltar
        </button>
        <h1>📋 Requisições Pendentes</h1>
        <button 
          className="refresh-button"
          onClick={fetchRequisicoes}
          disabled={loading}
          title="Atualizar lista"
        >
          🔄 {loading ? 'Carregando...' : 'Atualizar'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span>❌ {error}</span>
          <button onClick={fetchRequisicoes} className="retry-button">
            Tentar novamente
          </button>
        </div>
      )}

      {lastUpdate && (
        <div className="last-update">
          Última atualização: {lastUpdate}
        </div>
      )}

      <div className="requisicoes-container">
        {loading && requisicoes.length === 0 ? (
          <div className="loading-message">
            <div className="spinner"></div>
            <span>Carregando requisições...</span>
          </div>
        ) : requisicoes.length === 0 ? (
          <div className="empty-message">
            <span>📭 Nenhuma requisição pendente encontrada</span>
          </div>
        ) : (
          <>
            <div className="requisicoes-summary">
              <span>Total de requisições: <strong>{requisicoes.length}</strong></span>
            </div>
            
            <div className="requisicoes-list">
              {requisicoes.map((req, index) => {
                return (
                  <div key={req.nrec || index} className="requisicao-card">
                    <div className="card-header-flex">
                      <button
                        className="etiqueta-button"
                        onClick={() => onBack(req.etiq)}
                        title="Consultar etiqueta automaticamente"
                      >
                        📱 {req.etiq}
                      </button>
                      <div className="numero-req-container">
                        <label>N. Req:</label>
                        <span>#{req.nrec}</span>
                      </div>
                    </div>

                    <div className="info-grid">
                      <div className="requisicao-field">
                        <label>📦 Item:</label>
                        <span>{req.cod_item}</span>
                      </div>
                      <div className="requisicao-field">
                        <label>📝 Material:</label>
                        <span>{req.material || 'N/A'}</span>
                      </div>
                      <div className="requisicao-field">
                        <label>📊 Qtd. Vol:</label>
                        <span>{formatQuantidade(req.qt_volume)}</span>
                      </div>
                      <div className="requisicao-field">
                        <label>📋 Qtd. Req:</label>
                        <span>{formatQuantidade(req.qt_requisitada)}</span>
                      </div>
                      <div className="requisicao-field">
                        <label>🏢 Origem:</label>
                        <span>
                          {req.dep_origem || 'N/A'}
                          {req.saldo !== undefined && req.saldo !== 0 && (
                            <span className="saldo-info-compact">
                              (💰 {new Intl.NumberFormat('pt-BR').format(req.saldo)})
                            </span>
                          )}
                        </span>
                      </div>
                      <div className="requisicao-field">
                        <label>🎯 Destino:</label>
                        <span>{req.dep_destino || 'N/A'}</span>
                      </div>
                      <div className="requisicao-field-full">
                        <label>📍 Localização:</label>
                        <span className="localizacao-info">
                          {req.localizacao || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default RequisicoesPage;