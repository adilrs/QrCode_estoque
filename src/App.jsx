import React, { useState, useEffect, useRef } from 'react';
import { Html5QrcodeScanner, Html5QrcodeScanType } from 'html5-qrcode';
import { playSuccessSound, playErrorSound, playScanSound, requestAudioPermission } from './audioUtils';
import RequisicoesPage from './RequisicoesPage';
import LoginPage from './LoginPage';
import './App.css';

function App() {
  // Log global para capturar erros
  useEffect(() => {
    const handleError = (event) => {
      console.error('[DEBUG] ERRO GLOBAL CAPTURADO:', event.error);
      console.error('[DEBUG] Stack trace:', event.error?.stack);
    };
    
    const handleUnhandledRejection = (event) => {
      console.error('[DEBUG] PROMISE REJEITADA:', event.reason);
    };
    
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);
  
  const [isScanning, setIsScanning] = useState(false);
  const [materialData, setMaterialData] = useState(null);
  const [status, setStatus] = useState('');
  const [feedback, setFeedback] = useState({ type: '', message: '' });
  const [manualCode, setManualCode] = useState('');
  const [showManualMode, setShowManualMode] = useState(false);
  const [cameraInitialized, setCameraInitialized] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [currentPage, setCurrentPage] = useState('home'); // 'home' ou 'requisicoes'
  const [showLoginPage, setShowLoginPage] = useState(false);
  const [loggedUser, setLoggedUser] = useState(null); // Armazenar dados do usuário logado
  const [isTransferring, setIsTransferring] = useState(false); // Estado para controlar transferência em andamento
  const scannerRef = useRef(null);
  const qrScannerRef = useRef(null);

  useEffect(() => {
    console.log('[STATE] Feedback updated:', feedback);
  }, [feedback]);

  useEffect(() => {
    console.log('[STATE] Current page changed to:', currentPage);
  }, [currentPage]);

  useEffect(() => {
    console.log('[STATE] Status updated to:', status);
  }, [status]);

  useEffect(() => {
    console.log('[STATE] Material data:', materialData ? 'present' : 'null');
  }, [materialData]);


  // Verificar se há usuário logado no localStorage ao inicializar
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setLoggedUser(userData);
        console.log('Usuário logado restaurado:', userData);
      } catch (error) {
        console.error('Erro ao restaurar usuário logado:', error);
        localStorage.removeItem('user');
      }
    }else {
      // Se não houver usuário salvo, mostrar a tela de login
      setShowLoginPage(true);
    }
  }, []);

  // Função para navegar entre páginas
  const navigateToPage = (page) => {
    console.log('🚀 Navegando para página:', page);
    console.log('🚀 Estado atual antes:', currentPage);
    setCurrentPage(page);
    console.log('🚀 setCurrentPage executado com:', page);
    // Limpar dados quando sair da página principal
    if (page !== 'home') {
      setMaterialData(null);
      setIsScanning(false);
      setStatus('');
      setFeedback({ type: '', message: '' });
    }
  };

  // Função para lidar com clique na etiqueta
  const handleEtiquetaClick = async (etiqueta) => {
    if (!etiqueta) {
      // Se não há etiqueta, apenas volta para home
      navigateToPage('home');
      return;
    }

    console.log('🏷️ Clique na etiqueta:', etiqueta);
    
    // Navegar para a página principal primeiro
    navigateToPage('home');
    
    // Aguardar um pouco para a navegação completar
    setTimeout(async () => {
      // Fazer a consulta automática da etiqueta
      await fetchMaterialData(etiqueta);
    }, 100);
  };

  // Função para mostrar feedback temporário
  // Corrected showFeedback with debug logs
  const showFeedback = (type, message, duration = 3000) => {
    console.log(`[FEEDBACK] ${type.toUpperCase()}: ${message}`);
    console.log('[SHOW_FEEDBACK] Setting feedback to:', {type, message});
    setFeedback({ type, message });
    setTimeout(() => {
      console.log('[SHOW_FEEDBACK] Clearing feedback');
      setFeedback({ type: '', message: '' });
    }, duration);
  };

  const handleTransfer = async (codigo) => {
    console.log('[DEBUG] handleTransfer iniciada');
    console.log('[DEBUG] Código recebido:', codigo);
    console.log('[DEBUG] Tipo do código:', typeof codigo);
    console.log('[DEBUG] loggedUser atual:', loggedUser);
    
    // Verificar se o usuário está logado
    if (!loggedUser) {
      console.log('[TRANSFER] Usuário não logado, exibindo tela de login');
      setShowLoginPage(true);
      return;
    }
    
    setIsTransferring(true); // Desabilitar botão
    setStatus('Transferindo...');
  
    try {
      const response = await fetch('/api/transferencia_material', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          codigo, 
          usuario: loggedUser.usuario, 
          codigo_usuario: loggedUser.codigo 
        }),
      });
  
      console.log('[TRANSFER] Response status:', response.status);
  
      const data = await response.json();
  
      console.log('[TRANSFER] Resultado da transferência:', data);
      console.log('[FRONTEND] Resposta da transferência:', data);
  
      if (data.sucesso) {
        playSuccessSound();
        console.log('[FRONTEND] Transferência bem-sucedida:', data.mensagem);
  
        showFeedback('success', 'Transferência realizada com sucesso!', 2000);
        setStatus('Transferência concluída!');
  
        setTimeout(() => {
          console.log('[FRONTEND] Executando navegação após sucesso...');
          setMaterialData(null);
          setIsTransferring(false); // Reabilitar botão
          navigateToPage('requisicoes');
          console.log('[FRONTEND] Navegação para requisições executada!');
        }, 2000);
      } else {
        console.error('[FRONTEND] Falha na transferência:', data.erro);
        showFeedback('error', `Falha na transferência: ${data.erro || 'Erro desconhecido'}`, 3000);
  
        setTimeout(() => {
          console.log('[FRONTEND] Executando navegação após erro...');
          setMaterialData(null);
          setIsTransferring(false); // Reabilitar botão
          navigateToPage('requisicoes');
        }, 3000);
      }
    } catch (error) {
      console.error('[FRONTEND] Erro ao conectar com o backend:', error);
      showFeedback('error', 'Erro de conexão com o servidor', 3000);
  
      setTimeout(() => {
        setMaterialData(null);
        setIsTransferring(false); // Reabilitar botão
        navigateToPage('requisicoes');
      }, 3000);
    }
  };

  const testDatabaseConnection = async () => {
     setStatus('Testando conexão com banco de dados...');
     
     try {
       const response = await fetch('/api/test_db', {
         method: 'GET',
         headers: {
           'Content-Type': 'application/json',
         },
       });
 
       const data = await response.json();
 
       if (response.ok && data.status === 'success') {
         showFeedback('success', data.message || 'Conexão com banco de dados OK!');
         setStatus(`✅ ${data.message}`);
       } else {
         showFeedback('error', data.message || 'Erro na conexão com banco');
         setStatus(`❌ ${data.message || 'Erro na conexão com banco'}`);
       }
     } catch (error) {
       console.error('Erro ao testar conexão:', error);
       showFeedback('error', 'Erro de comunicação com o servidor');
       setStatus('❌ Erro de comunicação com o servidor');
     }
   };

   const handleManualSearch = async () => {
     if (!manualCode.trim()) {
       setStatus('Digite um código para consultar');
       return;
     }

     setStatus('Consultando material...');
     await fetchMaterialData(manualCode.trim());
   };

  // Função para iniciar novo scan
  const startNewScan = () => {
    setMaterialData(null);
    setStatus('');
    setFeedback({ type: '', message: '' });
    setIsScanning(true);
  };

  // Função para parar o scanner
  const stopScanner = () => {
    if (qrScannerRef.current) {
      qrScannerRef.current.clear().then(() => {
        setIsScanning(false);
        qrScannerRef.current = null;
      }).catch(err => {
        console.error('Erro ao parar scanner:', err);
        setIsScanning(false);
        qrScannerRef.current = null;
      });
    }
  };

  // Função para buscar dados do material com timeout e retry
  const fetchMaterialData = async (codigo, tentativa = 1) => {
    console.log(`[FRONTEND] Iniciando consulta para código: '${codigo}' (tentativa: ${tentativa})`);
    setStatus(`Consultando material... (tentativa ${tentativa})`);
    showFeedback('info', 'Processando código escaneado...', 1500);
    
    // Validação adicional do código
    if (!codigo || codigo.trim() === '') {
      console.log('[FRONTEND] ERRO: Código vazio ou inválido');
      showFeedback('error', 'Código QR inválido ou vazio');
      setStatus('Código inválido');
      return;
    }
    
    const codigoLimpo = codigo.trim();
    console.log(`[FRONTEND] Código limpo para envio: '${codigoLimpo}'`);
    
    try {
      // Implementar timeout de 10 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        console.log('[FRONTEND] Timeout da requisição');
      }, 10000);
      
      const response = await fetch('/api/consulta_material', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ codigo: codigoLimpo }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      console.log(`[FRONTEND] Status da resposta: ${response.status}`);
      const data = await response.json();
      console.log('[FRONTEND] Dados recebidos da API:', data);
      
      if (response.ok) {
        try {
          // Mapear os dados do backend para o formato esperado pelo frontend
          const materialFormatted = {
            codigoOriginal: codigoLimpo, // Código original da etiqueta para transferência
            codigo: data.codigomoldes || 'N/A',
            descricao: data.descricao || 'N/A',
            quantidade: data.qt_etiq || 0,
            quantidadeRecebida: data.qt_rec || 0,
            unidade: data.unidade ? data.unidade.trim() : 'UN',
            valor: 'N/A', // Não disponível na API atual
            valorTotal: 'N/A', // Não disponível na API atual
            requisicao: data.nreq || null,
            status: (data.mensagem && data.mensagem.trim() && data.mensagem.includes('ja Baixada')) ? 'Transferido' : (data.qt_rec > 0 ? 'Pendente' : 'Disponível'),
            solicitante: data.dep_destino || 'N/A',
            tipo: data.tipo || 'N/A',
            procedencia: data.proced || 'N/A',
            localizacao: data.localizacao || 'N/A',
            mensagem: data.mensagem ? data.mensagem.trim() : '',
            depOrigem: data.dep_origem || 'N/A',
            depDestino: data.dep_destino || 'N/A',
            saldo: data.saldo || 0
          };
          
          console.log('[FRONTEND] Material formatado:', materialFormatted);
          console.log('[FRONTEND] Definindo materialData...');
          
          // Log específico para AA162042
          if (codigo === 'AA162042') {
            console.log('[FRONTEND] ⚠️ DEFININDO MATERIAL DATA PARA AA162042');
            console.log('[FRONTEND] ⚠️ Material formatado para AA162042:', JSON.stringify(materialFormatted, null, 2));
          }
          
          setMaterialData(materialFormatted);
          console.log('[FRONTEND] materialData definido com sucesso');
          
          // Log específico após setMaterialData para AA162042
          if (codigo === 'AA162042') {
            console.log('[FRONTEND] ⚠️ MATERIAL DATA DEFINIDO PARA AA162042 - VERIFICANDO ESTADO');
            setTimeout(() => {
              console.log('[FRONTEND] ⚠️ Estado materialData após timeout:', materialData);
            }, 100);
          }
          setStatus('Material encontrado!');
          showFeedback('success', 'Material carregado com sucesso!');
          
          // Reproduzir som de sucesso
          if (audioEnabled) {
            playSuccessSound();
          }
        } catch (formatError) {
          console.error('[FRONTEND] Erro ao formatar dados do material:', formatError);
          showFeedback('error', 'Erro ao processar dados do material');
          setStatus('Erro ao processar dados');
        }
      } else {
        console.log(`[FRONTEND] Erro na consulta: ${data.erro}`);
        setStatus('Material não encontrado');
        showFeedback('error', data.erro || 'Material não encontrado');
        
        // Reproduzir som de erro
        if (audioEnabled) {
          playErrorSound();
        }
        
        // Limpar dados anteriores
        setMaterialData(null);
        
        // Reiniciar scanner automaticamente após 3 segundos quando material não encontrado
        setTimeout(() => {
          if (!materialData && cameraInitialized) {
            console.log('[FRONTEND] Reiniciando scanner automaticamente após material não encontrado');
            setIsScanning(true);
            showFeedback('info', 'Scanner reiniciado. Escaneie outro código.', 2000);
          }
        }, 3000);
      }
    } catch (error) {
      console.error(`[FRONTEND] Erro ao buscar material (tentativa ${tentativa}):`, error);
      
      // Se for timeout ou erro de rede e ainda há tentativas disponíveis
      if ((error.name === 'AbortError' || error.message.includes('fetch')) && tentativa < 3) {
        console.log(`[FRONTEND] Tentando novamente em 2 segundos... (tentativa ${tentativa + 1}/3)`);
        showFeedback('warning', `Erro de conexão. Tentando novamente... (${tentativa + 1}/3)`, 2000);
        setTimeout(() => {
          fetchMaterialData(codigo, tentativa + 1);
        }, 2000);
        return;
      }
      
      // Erro final após todas as tentativas
      if (error.name === 'AbortError') {
        setStatus('Timeout na consulta');
        showFeedback('error', 'Timeout: Servidor demorou para responder');
      } else {
        setStatus('Erro de conexão');
        showFeedback('error', 'Erro de conexão com o servidor');
      }
      
      // Limpar dados anteriores
      setMaterialData(null);
      
      // Reiniciar scanner automaticamente após 4 segundos em caso de erro
      setTimeout(() => {
        if (!materialData && cameraInitialized) {
          console.log('[FRONTEND] Reiniciando scanner automaticamente após erro de conexão');
          setIsScanning(true);
          showFeedback('info', 'Scanner reiniciado. Tente escanear novamente.', 2000);
        }
      }, 4000);
    }
  };

  // Função chamada quando QR code é lido com sucesso
  const onScanSuccess = (decodedText, decodedResult) => {
    console.log('[FRONTEND] QR Code detectado:', decodedText);
    console.log('[FRONTEND] Resultado completo:', decodedResult);
    
    // Log específico para AA162042 - apenas em ambiente de desenvolvimento
    if (decodedText === 'AA162042' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
      console.log('[FRONTEND] ⚠️ CÓDIGO AA162042 DETECTADO - INICIANDO DEBUG');
      console.log('[FRONTEND] Estado atual - isScanning:', isScanning);
      console.log('[FRONTEND] Estado atual - materialData:', materialData);
      console.log('[FRONTEND] Estado atual - cameraInitialized:', cameraInitialized);
    }
    
    // Reproduzir som de escaneamento
    if (audioEnabled) {
      playScanSound();
    }
    
    // Feedback imediato de detecção
    showFeedback('info', `QR Code detectado: ${decodedText}`, 2000);
    
    // Validação adicional do código detectado
    if (!decodedText || decodedText.trim() === '') {
      console.log('[FRONTEND] AVISO: QR Code detectado mas texto está vazio');
      showFeedback('warning', 'QR Code detectado mas sem conteúdo válido');
      return;
    }
    
    stopScanner();
    
    // Log específico antes de chamar fetchMaterialData
    if (decodedText === 'AA162042') {
      console.log('[FRONTEND] ⚠️ CHAMANDO fetchMaterialData para AA162042');
    }
    
    fetchMaterialData(decodedText);
  };

  // Função chamada quando há erro na leitura
  const onScanFailure = (error) => {
    // Não fazer nada para erros de scan (muito verboso)
  };

  // Inicializar áudio
  useEffect(() => {
    const initAudio = async () => {
      const audioPermission = await requestAudioPermission();
      setAudioEnabled(audioPermission);
      if (audioPermission) {
        console.log('[AUDIO] Sistema de áudio inicializado');
      } else {
        console.log('[AUDIO] Sistema de áudio não disponível');
      }
    };
    
    initAudio();
  }, []);

  // Tentar inicializar câmera automaticamente ao carregar
  useEffect(() => {
    if (!cameraInitialized) {
      const tryAutoStartCamera = async () => {
        try {
          // Verificar se há suporte a câmera
          const devices = await navigator.mediaDevices.enumerateDevices();
          const hasCamera = devices.some(device => device.kind === 'videoinput');
          
          if (hasCamera) {
            // Configurações específicas para mobile
            const constraints = {
              video: {
                facingMode: { ideal: 'environment' }, // Câmera traseira preferencial
                width: { ideal: 1280, max: 1920 },
                height: { ideal: 720, max: 1080 }
              }
            };
            
            // Tentar obter permissão da câmera com configurações mobile
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Parar o stream imediatamente (só testamos permissão)
            stream.getTracks().forEach(track => track.stop());
            
            setStatus('Câmera detectada! Iniciando scanner...');
            showFeedback('success', 'Câmera ativada automaticamente!', 2000);
            setIsScanning(true);
          } else {
            throw new Error('Nenhuma câmera detectada');
          }
        } catch (error) {
          console.log('Falha ao inicializar câmera automaticamente:', error);
          setStatus('Câmera não disponível. Use a consulta manual.');
          showFeedback('warning', 'Câmera não disponível. Modo manual ativado.', 3000);
          setShowManualMode(true);
        }
        setCameraInitialized(true);
      };
      
      // Delay pequeno para evitar problemas de renderização
      setTimeout(tryAutoStartCamera, 500);
    }
  }, [cameraInitialized]);

  // Inicializar scanner quando isScanning muda para true
  useEffect(() => {
    if (isScanning && scannerRef.current && !qrScannerRef.current) {
      try {
        // Configurações otimizadas para mobile
        const config = {
          fps: 15, // Aumentado para melhor responsividade
          qrbox: function(viewfinderWidth, viewfinderHeight) {
            // Caixa responsiva baseada no tamanho da tela
            const minEdgePercentage = 0.7; // 70% da menor dimensão
            const minEdgeSize = Math.min(viewfinderWidth, viewfinderHeight);
            const qrboxSize = Math.floor(minEdgeSize * minEdgePercentage);
            return {
              width: Math.min(qrboxSize, 300),
              height: Math.min(qrboxSize, 300)
            };
          },
          aspectRatio: 1.0,
          showTorchButtonIfSupported: true,
          showZoomSliderIfSupported: true,
          defaultZoomValueIfSupported: 2,
          // Configurações específicas para mobile
          videoConstraints: {
            facingMode: { ideal: 'environment' },
            width: { ideal: 1280, max: 1920 },
            height: { ideal: 720, max: 1080 }
          },
          // Melhor suporte para diferentes formatos
          supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
        };

        qrScannerRef.current = new Html5QrcodeScanner(
          'qr-reader',
          config,
          false
        );

        qrScannerRef.current.render(onScanSuccess, onScanFailure);
      } catch (error) {
        console.error('Erro ao inicializar scanner:', error);
        
        // Mensagens mais específicas baseadas no tipo de erro
        if (error.name === 'NotAllowedError') {
          setStatus('Permissão de câmera negada.');
          showFeedback('error', 'Permissão de câmera negada. Ative nas configurações do navegador.');
        } else if (error.name === 'NotFoundError') {
          setStatus('Câmera não encontrada.');
          showFeedback('error', 'Nenhuma câmera encontrada no dispositivo.');
        } else if (error.name === 'NotSupportedError') {
          setStatus('Câmera não suportada.');
          showFeedback('error', 'Câmera não suportada neste navegador.');
        } else {
          setStatus('Erro ao inicializar câmera.');
          showFeedback('error', 'Erro ao acessar a câmera. Modo manual disponível.');
        }
        
        setIsScanning(false);
        setShowManualMode(true);
      }
    }

    console.log('[RENDER] Current page:', currentPage);
  console.log('[RENDER] Feedback:', feedback);
  console.log('[RENDER] Status:', status);
  console.log('[RENDER] MaterialData:', materialData);

  return () => {
      if (qrScannerRef.current) {
        qrScannerRef.current.clear().catch(err => {
          console.error('Erro ao limpar scanner:', err);
        });
        qrScannerRef.current = null;
      }
    };
  }, [isScanning]);

  // Renderização condicional baseada na página atual
  // Debug logs apenas em ambiente de desenvolvimento
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔍 DEBUG - Página atual:', currentPage);
    console.log('🔍 DEBUG - Tipo de currentPage:', typeof currentPage);
    console.log('🔍 DEBUG - Comparação:', currentPage === 'requisicoes');
  }
  
  if (currentPage === 'requisicoes') {
    console.log('✅ Renderizando RequisicoesPage');
    return <RequisicoesPage onBack={(etiqueta) => handleEtiquetaClick(etiqueta)} />;
  }
  
  console.log('❌ Renderizando página inicial (home)');

  return (
    <div className="bg-gray-100 app-container w-full max-w-full">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold flex-1 text-center">Completar Transferência por Requisição</h1>
          <button
            onClick={() => {
              if (loggedUser) {
                // Se há usuário logado, mostrar opção de logout
                const confirmLogout = window.confirm(`Deseja fazer logout do usuário ${loggedUser.codigo} - ${loggedUser.usuario}?`);
                if (confirmLogout) {
                  setLoggedUser(null);
                  localStorage.removeItem('user');
                  console.log('Logout realizado');
                }
              } else {
                // Se não há usuário logado, abrir tela de login
                setShowLoginPage(true);
              }
            }}
            className="bg-blue-700 hover:bg-blue-800 text-white p-2 rounded-lg transition-colors duration-200 flex items-center justify-center min-w-[120px]"
            title={loggedUser ? `Clique para logout: ${loggedUser.codigo} - ${loggedUser.usuario}` : "Acessar Login"}
          >
            {loggedUser ? (
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span className="text-sm font-medium">{loggedUser.codigo} - {loggedUser.usuario}</span>
              </div>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Botão Requisições Pendentes - Topo da Página */}
      {(window.location.hostname === 'localhost' || 
        window.location.hostname === '127.0.0.1' || 
        window.location.hostname === '192.168.2.96') && (
        <div className="p-4 bg-white border-b border-gray-200">
          <button
            onClick={() => navigateToPage('requisicoes')}
            className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-4 rounded-lg shadow-md transition-colors duration-200 flex items-center justify-center gap-2"
          >
            📋 Requisições Pendentes
          </button>
        </div>
      )}

      {/* Feedback Messages */}
      {feedback.message && (
        <div className={`p-3 m-4 rounded ${
          feedback.type === 'success' ? 'bg-green-100 border border-green-300 text-green-800' :
          feedback.type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' :
          'bg-blue-100 border border-blue-300 text-blue-800'
        }`}>
          <p>{feedback.message}</p>
        </div>
      )}

      {/* QR Scanner */}
      {isScanning && (
        <div className="p-4 mobile-padding w-full max-w-full">
          <div className="bg-white rounded-lg shadow-md p-4 w-full max-w-full">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Escaneie o QR Code</h2>
              <button
                onClick={stopScanner}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
              >
                Parar
              </button>
            </div>
            <div id="qr-reader" ref={scannerRef} className="w-full"></div>
          </div>
          

        </div>
      )}

      {/* Status */}
      {status && (
        <div className="p-4">
          <div className="bg-blue-100 border border-blue-300 rounded p-3">
            <p className="text-blue-800 text-center">{status}</p>
          </div>
        </div>
      )}

      {/* Material Data - Sempre exibir quando materialData existir */}
      {materialData && (
        <div className="p-4 mobile-padding w-full max-w-full">
          <div className="bg-white rounded-lg shadow-md p-4 w-full max-w-full">
            <h2 className="text-lg font-semibold mb-4">Dados do Material</h2>
            
            <div className="space-y-4 mb-4 max-w-full overflow-x-hidden">
               {/* Código e Descrição em uma linha */}
               <div className="codigo-descricao-grid">
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Código:</label>
                   <p className="text-lg font-mono bg-gray-50 p-2 rounded whitespace-nowrap">{materialData.codigo}</p>
                 </div>
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Descrição:</label>
                   <p className="text-lg bg-gray-50 p-2 rounded">{materialData.descricao}</p>
                 </div>
               </div>
               
               {/* Grid 2 colunas para campos menores */}
               <div className="material-grid">
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Tipo:</label>
                   <p className="text-lg bg-blue-50 p-2 rounded border border-blue-200">{materialData.tipo}</p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Localização:</label>
                   <p className="text-lg bg-purple-50 p-2 rounded border border-purple-200">{materialData.localizacao}</p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Qtd. Etiqueta:</label>
                   <p className="text-lg font-semibold bg-green-50 p-2 rounded border border-green-200">{materialData.quantidade} {materialData.unidade}</p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Qtd. Requerida:</label>
                   <p className="text-lg font-semibold bg-blue-50 p-2 rounded border border-blue-200">{materialData.quantidadeRecebida} {materialData.unidade}</p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Requisição Nº:</label>
                   <p className="text-lg font-mono bg-yellow-50 p-2 rounded border border-yellow-200">{materialData.requisicao || 'N/A'}</p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Status:</label>
                   <p className={`text-lg font-semibold p-2 rounded border ${
                     materialData.status === 'Transferido' ? 'bg-green-100 text-green-800 border-green-300' :
                     materialData.status === 'Pendente' ? 'bg-yellow-100 text-yellow-800 border-yellow-300' :
                     'bg-gray-50 text-gray-800 border-gray-300'
                   }`}>
                     {materialData.status}
                   </p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Dep. Origem:</label>
                   <p className="text-lg bg-orange-50 p-2 rounded border border-orange-200">
                     {materialData.depOrigem} 
                     {materialData.saldo !== undefined && materialData.saldo !== 0 && (
                       <span className="text-blue-600 font-semibold ml-2">
                         (Saldo: {new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(materialData.saldo)})
                       </span>
                     )}
                   </p>
                 </div>
                 
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Dep. Destino:</label>
                   <p className="text-lg bg-orange-50 p-2 rounded border border-orange-200">{materialData.depDestino}</p>
                 </div>
               </div>
               

               
               {/* Mensagem - largura total se existir */}
               {materialData.mensagem && (
                 <div>
                   <label className="block text-sm font-medium text-gray-700 mb-1">Mensagem:</label>
                   <p className="text-lg bg-red-50 p-3 rounded border border-red-200 text-red-800">{materialData.mensagem}</p>
                 </div>
               )}
             </div>
            
            {/* Mensagem de saldo insuficiente - só aparece quando há requisição válida */}
            {materialData.requisicao && 
             materialData.requisicao !== 'N/A' && 
             (typeof materialData.requisicao !== 'string' || materialData.requisicao.trim() !== '') &&
             materialData.saldo !== undefined && 
             materialData.quantidadeRecebida && 
             materialData.saldo < parseFloat(materialData.quantidadeRecebida) && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <strong>Saldo Insuficiente!</strong> O saldo disponível ({new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(materialData.saldo)}) é menor que a quantidade requerida ({materialData.quantidadeRecebida}).
              </div>
            )}
            
            <div className="flex flex-col gap-3 mt-6 pb-6">
              <button
                id="transfer-btn"
                onClick={(event) => {
                   console.log('[DEBUG] ===== CLIQUE DO BOTÃO =====');
                   console.log('[DEBUG] Event:', event);
                   console.log('[DEBUG] Event.target:', event.target);
                   console.log('[DEBUG] Event.currentTarget:', event.currentTarget);
                   console.log('[DEBUG] materialData completo:', materialData);
                   console.log('[DEBUG] codigoOriginal:', materialData?.codigoOriginal);
                   console.log('[DEBUG] Botão desabilitado?:', event.target.disabled);
                   
                   // Prevenir comportamento padrão
                   event.preventDefault();
                   event.stopPropagation();
                   
                   console.log('[DEBUG] Chamando handleTransfer...');
                   try {
                     handleTransfer(materialData?.codigoOriginal);
                   } catch (error) {
                     console.error('[DEBUG] ERRO ao chamar handleTransfer:', error);
                   }
                 }}
                disabled={(() => {
                   const cond1 = isTransferring;
                   const cond2 = materialData.status === 'Transferido';
                   const cond3 = !materialData.requisicao;
                   const cond4 = materialData.requisicao === 'N/A';
                   const cond5 = (typeof materialData.requisicao === 'string' && materialData.requisicao.trim() === '');
                   const cond6 = (materialData.requisicao && materialData.requisicao !== 'N/A' && (typeof materialData.requisicao !== 'string' || materialData.requisicao.trim() !== '') && materialData.saldo !== undefined && materialData.quantidadeRecebida && materialData.saldo < parseFloat(materialData.quantidadeRecebida));
                   
                   const isDisabled = cond1 || cond2 || cond3 || cond4 || cond5 || cond6;
                   
                   console.log('[DEBUG] === CONDIÇÕES DO BOTÃO ===');
                   console.log('[DEBUG] isTransferring:', cond1);
                   console.log('[DEBUG] status === Transferido:', cond2);
                   console.log('[DEBUG] !requisicao:', cond3);
                   console.log('[DEBUG] requisicao === N/A:', cond4);
                   console.log('[DEBUG] requisicao vazia:', cond5);
                   console.log('[DEBUG] saldo insuficiente:', cond6);
                   console.log('[DEBUG] BOTÃO DESABILITADO:', isDisabled);
                   console.log('[DEBUG] materialData.requisicao:', materialData.requisicao);
                   console.log('[DEBUG] materialData.saldo:', materialData.saldo);
                   console.log('[DEBUG] materialData.quantidadeRecebida:', materialData.quantidadeRecebida);
                   
                   return isDisabled;
                 })()}
                className={`flex-1 font-bold py-3 px-4 rounded transition-colors ${
                  isTransferring
                    ? 'bg-yellow-400 text-yellow-800 cursor-not-allowed'
                    : materialData.status === 'Transferido'
                    ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    : (!materialData.requisicao || materialData.requisicao === 'N/A' || (typeof materialData.requisicao === 'string' && materialData.requisicao.trim() === ''))
                    ? 'bg-red-400 text-red-100 cursor-not-allowed'
                    : (materialData.requisicao && materialData.requisicao !== 'N/A' && (typeof materialData.requisicao !== 'string' || materialData.requisicao.trim() !== '') && materialData.saldo !== undefined && materialData.quantidadeRecebida && materialData.saldo < parseFloat(materialData.quantidadeRecebida))
                    ? 'bg-red-400 text-red-100 cursor-not-allowed'
                    : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {isTransferring
                  ? 'Transferindo...'
                  : materialData.status === 'Transferido' 
                  ? 'Já Transferido' 
                  : (!materialData.requisicao || materialData.requisicao === 'N/A' || (typeof materialData.requisicao === 'string' && materialData.requisicao.trim() === ''))
                  ? 'Sem Requisição'
                  : (materialData.requisicao && materialData.requisicao !== 'N/A' && (typeof materialData.requisicao !== 'string' || materialData.requisicao.trim() !== '') && materialData.saldo !== undefined && materialData.quantidadeRecebida && materialData.saldo < parseFloat(materialData.quantidadeRecebida))
                  ? 'Saldo Insuficiente'
                  : 'Transferir'
                }
              </button>
              
              <button
                onClick={startNewScan}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded transition-colors"
              >
                Novo Scan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Controls when not scanning and no material data */}
      {!isScanning && !materialData && cameraInitialized && (
        <div className="p-4 mobile-padding space-y-3 pb-8 w-full max-w-full">
          {!showManualMode && (
            <button
              onClick={startNewScan}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-4 px-4 rounded-lg text-lg transition-colors"
            >
              Iniciar Scanner
            </button>
          )}
          
          {showManualMode && (
            <button
              onClick={() => {
                setShowManualMode(false);
                startNewScan();
              }}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-4 px-4 rounded-lg text-lg transition-colors"
            >
              Tentar Ativar Câmera
            </button>
          )}
          
          {/* Botão Testar Conexão BD - apenas em ambiente de desenvolvimento/homologação */}
          {(window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && (
            <button
               onClick={testDatabaseConnection}
               className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg transition-colors"
             >
               Testar Conexão BD (Debug)
             </button>
          )}
           
           <button
             onClick={() => setAudioEnabled(!audioEnabled)}
             className={`w-full font-bold py-3 px-4 rounded-lg transition-colors ${
               audioEnabled 
                 ? 'bg-orange-500 hover:bg-orange-600 text-white' 
                 : 'bg-gray-500 hover:bg-gray-600 text-white'
             }`}
           >
             {audioEnabled ? '🔊 Som Ativado' : '🔇 Som Desativado'}
           </button>
           

           
           {/* Manual Code Input - sempre visível quando não há material */}
           <div className="mt-4 p-4 bg-gray-50 rounded-lg w-full max-w-full">
             <h3 className="text-lg font-semibold mb-3 text-gray-700">
               {showManualMode ? 'Consulta Manual (Modo Principal)' : 'Consulta Manual (Alternativa)'}
             </h3>
             <div className="flex gap-2 w-full max-w-full">
               <input
                 type="text"
                 value={manualCode}
                 onChange={(e) => setManualCode(e.target.value)}
                 placeholder="Digite o código (ex: AA162026)"
                 className="flex-1 px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[48px] font-mono"
                 style={{minWidth: '200px', fontSize: '16px'}}
                 onKeyPress={(e) => e.key === 'Enter' && handleManualSearch()}
                 autoFocus={showManualMode}
               />
               <button
                 onClick={handleManualSearch}
                 className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
               >
                 Consultar
               </button>
             </div>
           </div>
          </div>
        )}
        
      {/* Loading state during camera initialization - Só exibir se não houver materialData */}
      {!cameraInitialized && !materialData && (
        <div className="p-4 mobile-padding w-full max-w-full">
          <div className="bg-blue-100 border border-blue-300 rounded p-4 text-center">
            <p className="text-blue-800 text-lg">Verificando disponibilidade da câmera...</p>
            <div className="mt-2">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          </div>
        </div>
      )}
      
      {/* Rodapé com link para o manual */}
      <footer className="mt-8 p-4 bg-gray-100 border-t border-gray-200 text-center">
        <div className="text-sm text-gray-600">
          <a 
            href="./MANUAL_USUARIO_SIMPLIFICADO.html" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline font-medium"
          >
            📖 Manual do Usuário
          </a>
        </div>
      </footer>
      
      {/* Modal de Login */}
      {showLoginPage && (
        <LoginPage 
          onClose={() => setShowLoginPage(false)} 
          onLoginSuccess={(userData) => {
            setLoggedUser(userData);
            setShowLoginPage(false);
          }}
        />
      )}
    </div>
  );
}

export default App;