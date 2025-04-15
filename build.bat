@echo off
echo Instalando dependencias...
pip install -r requirements.txt

echo Compilando o projeto...
pyinstaller --clean --noconfirm main.spec

echo Criando instalador...
if not exist "installer" mkdir installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

echo Processo concluido!
echo O instalador esta na pasta installer/BatchRenamer-Setup.exe
pause 