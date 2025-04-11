# Batch File Renamer

Um aplicativo WYSIWYG para renomear arquivos em lote usando Python e Qt5.

## Funcionalidades

- Carrega nomes de arquivos a partir de um arquivo CSV
- Seleciona uma pasta contendo arquivos para renomear
- Filtra arquivos por extensão
- Visualização WYSIWYG dos nomes no CSV e arquivos na pasta
- Renomeia arquivos em lote

## Requisitos

- Python 3.6 ou superior
- PyQt5

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:

```
pip install -r requirements.txt
```

## Como usar

1. Execute o aplicativo:

```
python batch_renamer.py
```

2. Clique em "Botão abrir csv" para selecionar um arquivo CSV contendo os novos nomes
3. Clique em "Botão abrir pasta" para selecionar a pasta com os arquivos a serem renomeados
4. Opcionalmente, insira as extensões de arquivo a serem filtradas (separadas por vírgula)
5. Clique em "Recarregar arquivos" para atualizar a lista de arquivos com base nas extensões
6. Verifique as listas de nomes e arquivos nas tabelas WYSIWYG
7. Clique em "Renomear Arquivos" para iniciar o processo de renomeação

## Formato do CSV

O arquivo CSV deve conter uma coluna com os novos nomes para os arquivos (sem extensões).
As extensões dos arquivos originais serão preservadas durante a renomeação.

## Observações

- Os arquivos são renomeados na ordem em que aparecem na tabela (ordem alfabética)
- Os nomes do CSV são aplicados na mesma ordem
- Se houver mais arquivos do que nomes no CSV, apenas os primeiros arquivos serão renomeados
