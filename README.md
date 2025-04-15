# BatchRenamer

Um aplicativo para renomear arquivos em lote usando um arquivo CSV.

## Funcionalidades

- Renomear múltiplos arquivos de uma vez usando um arquivo CSV
- Visualização prévia de arquivos (imagens, PDFs e textos)
- Suporte a diferentes tipos de arquivo
- Filtro por extensões
- Histórico de renomeações com opção de desfazer
- Interface em português, inglês e espanhol
- Busca em tempo real nos arquivos e no CSV

## Requisitos

- Python 3.8 ou superior
- PyQt5
- PyMuPDF (para visualização de PDFs)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/batch-renamer.git
cd batch-renamer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o programa:
```bash
python main.py
```

## Como Usar

1. Clique em "Abrir CSV" para carregar um arquivo CSV com os novos nomes
2. Clique em "Abrir Pasta" para selecionar a pasta com os arquivos a serem renomeados
3. Opcionalmente, filtre as extensões dos arquivos
4. Clique em "Renomear Arquivos" para executar a renomeação
5. Use "Desfazer Renomeação" para reverter a última operação

## Estrutura do Projeto

```
batch-renamer/
├── core/               # Lógica de negócios
│   ├── file_manager.py
│   ├── csv_manager.py
│   ├── history_manager.py
│   ├── preview_manager.py
│   └── language_manager.py
├── ui/                 # Interface do usuário
│   ├── main_window.py
│   └── components/
│       ├── file_table.py
│       ├── csv_table.py
│       └── preview_panel.py
├── main.py            # Ponto de entrada
├── requirements.txt   # Dependências
└── README.md         # Documentação
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contribuição

Contribuições são bem-vindas! Por favor, leia as [diretrizes de contribuição](CONTRIBUTING.md) antes de enviar um pull request.
