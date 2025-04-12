# Renomeador em Lote

Um aplicativo para renomear arquivos em lote usando um arquivo CSV como fonte de novos nomes.

## Funcionalidades

- Carregar arquivos de uma pasta
- Carregar nomes de um arquivo CSV
- Visualizar arquivos (imagens, PDFs e textos)
- Renomear arquivos em lote
- Desfazer renomeações
- Filtrar arquivos por extensão
- Buscar arquivos e nomes
- Mover arquivos e nomes para cima/baixo
- Abrir arquivos com aplicativo padrão
- Localizar arquivos no Explorer

## Requisitos

- Python 3.6 ou superior
- PyQt5
- PyMuPDF (para visualização de PDFs)

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o aplicativo:
```bash
python main.py
```

2. Clique em "Abrir CSV" para carregar um arquivo CSV com os novos nomes
3. Clique em "Abrir Pasta" para selecionar a pasta com os arquivos a serem renomeados
4. Opcionalmente, filtre os arquivos por extensão
5. Clique em "Renomear Arquivos" para executar a renomeação
6. Use "Desfazer Renomeação" para reverter a última operação

## Formato do CSV

O arquivo CSV deve conter um nome por linha, sem cabeçalho. Exemplo:
```
novo_nome1
novo_nome2
novo_nome3
```

## Histórico

O aplicativo mantém um histórico das operações de renomeação em um arquivo JSON, permitindo desfazer as alterações se necessário.

## Licença

Este projeto está licenciado sob a licença MIT.
