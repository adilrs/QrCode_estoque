@echo off
echo ========================================
echo  Sistema de Transferencia de Material
echo           Instalador v1.0
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ de: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar se Node.js esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo Por favor, instale Node.js 16+ de: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Verificacoes de pre-requisitos concluidas!
echo.

REM Criar ambiente virtual Python
echo [1/5] Criando ambiente virtual Python...
REM Remover ambiente virtual existente se houver
if exist ".venv" (
    echo [INFO] Removendo ambiente virtual existente...
    rmdir /s /q ".venv"
)
REM Criar novo ambiente virtual
python -m venv .venv --without-pip
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar ambiente virtual!
    echo [INFO] Tentando metodo alternativo...
    python -c "import venv; venv.create('.venv', with_pip=True)"
    if %errorlevel% neq 0 (
        echo [ERRO] Falha no metodo alternativo!
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual e instalar dependencias Python
echo [2/5] Instalando dependencias Python...
call .venv\Scripts\activate.bat
REM Verificar se pip existe, se nao, instalar
if not exist ".venv\Scripts\pip.exe" (
    echo [INFO] Instalando pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo [INFO] Tentando download direto do pip...
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python get-pip.py
        del get-pip.py
    )
)
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [AVISO] Falha ao atualizar pip, continuando...
)
echo [INFO] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias Python!
    echo [INFO] Tentando com --user...
    pip install --user -r requirements.txt
    if %errorlevel% neq 0 (
        echo [INFO] Tentando instalar individualmente...
        pip install flask==3.0.3
        pip install fdb==2.0.4
        if %errorlevel% neq 0 (
            echo [ERRO] Falha definitiva na instalacao!
            pause
            exit /b 1
        )
    )
)

REM Instalar dependencias Node.js
echo [3/5] Instalando dependencias Node.js...
npm install
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias Node.js!
    pause
    exit /b 1
)

REM Gerar certificados SSL
echo [4/5] Gerando certificados SSL...
python generate_ssl.py
if %errorlevel% neq 0 (
    echo [AVISO] Falha ao gerar certificados SSL. Usando certificados existentes.
)

REM Criar script de inicializacao
echo [5/5] Criando script de inicializacao...
echo @echo off > start_system.bat
echo echo ======================================== >> start_system.bat
echo echo  Sistema de Transferencia de Material >> start_system.bat
echo echo           Iniciando v1.0 >> start_system.bat
echo echo ======================================== >> start_system.bat
echo echo. >> start_system.bat
echo echo [INFO] Iniciando Backend... >> start_system.bat
echo start "Backend - Flask" cmd /k "call .venv\Scripts\activate.bat ^&^& python fdbacc.py" >> start_system.bat
echo timeout /t 3 /nobreak ^> nul >> start_system.bat
echo echo [INFO] Iniciando Frontend... >> start_system.bat
echo start "Frontend - React" cmd /k "npm run dev" >> start_system.bat
echo echo. >> start_system.bat
echo echo [SUCCESS] Sistema iniciado com sucesso! >> start_system.bat
echo echo. >> start_system.bat
echo echo Acesse: https://localhost:5173 >> start_system.bat
echo echo. >> start_system.bat
echo echo Pressione qualquer tecla para fechar... >> start_system.bat
echo pause ^> nul >> start_system.bat

echo.
echo ========================================
echo           INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para iniciar o sistema:
echo   1. Execute: start_system.bat
echo   2. Acesse: https://localhost:5173
echo.
echo Arquivos importantes:
echo   - start_system.bat (iniciar sistema)
echo   - DEPLOYMENT_GUIDE.md (guia completo)
echo.
echo ========================================
echo.
pause