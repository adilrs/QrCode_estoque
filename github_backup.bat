@echo off
echo Adicionando todos os arquivos ao Git...
git add .

echo Criando commit...
git commit -m "Backup automatico" 

echo Enviando para o GitHub...
git push

echo Backup para o GitHub concluido.
pause