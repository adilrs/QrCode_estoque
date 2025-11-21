import React, { useState, useEffect } from 'react';

const LoginPage = ({ onClose, onLoginSuccess }) => {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [validatingPassword, setValidatingPassword] = useState(false);

  useEffect(() => {
    const fetchUsuarios = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/usuarios_login', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success) {
          setUsuarios(data.usuarios);
        } else {
          setError(data.error || 'Erro ao carregar usuários');
        }
      } catch (err) {
        console.error('Erro ao buscar usuários:', err);
        setError('Erro ao conectar com o servidor');
      } finally {
        setLoading(false);
      }
    };

    fetchUsuarios();
  }, []);

  const handleUsuarioSelect = (usuario) => {
    console.log('Usuário selecionado:', usuario);
    setSelectedUser(usuario);
    setPassword('');
    setPasswordError(null);
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (!password.trim()) {
      setPasswordError('Por favor, digite a senha');
      return;
    }

    try {
      setValidatingPassword(true);
      setPasswordError(null);
      
      const response = await fetch('/api/login_auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Incluir cookies de sessão
        body: JSON.stringify({
          user_id: selectedUser.codigo,
          password: password
        })
      });

      const data = await response.json();
      
      if (response.ok && data.success && data.token) {
        console.log('Login realizado com sucesso:', selectedUser, 'Token recebido.');
        
        // Salva o token e os dados do usuário
        localStorage.setItem('token', data.token);
        const userData = {
          ...selectedUser,
          auth_code: data.auth_code
        };
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Chamar a função de callback para informar o App sobre o login bem-sucedido
        if (onLoginSuccess) {
          onLoginSuccess(userData);
        } else {
          onClose();
        }
      } else {
        // Trata especificamente o erro 401 (senha incorreta)
        if (response.status === 401) {
          setPasswordError('Senha incorreta');
        } else if (response.status === 400) {
          setPasswordError('Usuário e senha são obrigatórios');
        } else {
          setPasswordError(data.message || 'Erro ao conectar com o servidor');
        }
      }
    } catch (err) {
      console.error('Erro ao validar senha:', err);
      setPasswordError('Erro ao conectar com o servidor');
    } finally {
      setValidatingPassword(false);
    }
  };

  const handleBackToUsers = () => {
    setSelectedUser(null);
    setPassword('');
    setPasswordError(null);
  };

  console.log('🎨 RENDER: loading=', loading, 'error=', error, 'usuarios=', usuarios.length);
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-800">
              {selectedUser ? 'Digite sua Senha' : 'Selecionar Usuário'}
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl font-bold">×</button>
          </div>
          
          {!selectedUser && (
            <>
              {loading && (
                <div className="text-center py-8">
                  <p className="text-gray-600">Carregando usuários...</p>
                </div>
              )}
              
              {error && (
                <div className="text-center py-8">
                  <p className="text-red-600">{error}</p>
                  <button onClick={() => window.location.reload()} className="bg-blue-600 text-white px-4 py-2 rounded mt-4">
                    Tentar Novamente
                  </button>
                </div>
              )}
              
              {!loading && !error && (
                <div>
                  {usuarios.length === 0 ? (
                    <p className="text-center text-gray-600 py-4">Nenhum usuário encontrado</p>
                  ) : (
                    <div>
                      <p className="text-sm text-gray-600 mb-3">✅ {usuarios.length} usuário(s) encontrado(s)</p>
                      {usuarios.map((usuario) => (
                        <button
                          key={usuario.codigo}
                          onClick={() => handleUsuarioSelect(usuario)}
                          className="w-full text-left p-3 border border-gray-200 rounded hover:bg-blue-50 mb-2"
                        >
                          <div className="font-medium">{usuario.usuario}</div>
                          <div className="text-sm text-gray-500">Código: {usuario.codigo}</div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
          
          {selectedUser && (
            <div>
              <div className="mb-4 p-3 bg-gray-50 rounded">
                <div className="font-medium">{selectedUser.usuario}</div>
                <div className="text-sm text-gray-500">Código: {selectedUser.codigo}</div>
              </div>
              
              <form onSubmit={handlePasswordSubmit}>
                <div className="mb-4">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Digite sua senha"
                    className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={validatingPassword}
                    autoFocus
                  />
                  {passwordError && (
                    <p className="text-red-600 text-sm mt-2">{passwordError}</p>
                  )}
                </div>
                
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={!password.trim() || validatingPassword}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {validatingPassword ? 'Validando...' : 'Entrar'}
                  </button>
                  <button
                    type="button"
                    onClick={handleBackToUsers}
                    className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
                    disabled={validatingPassword}
                  >
                    Voltar
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;