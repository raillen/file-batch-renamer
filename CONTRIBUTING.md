# Como Contribuir

Obrigado pelo seu interesse em contribuir para o BatchRenamer! Aqui estão algumas diretrizes para ajudar você a começar.

## Reportando Problemas

- Use o sistema de issues do GitHub para reportar problemas
- Inclua o máximo de detalhes possível:
  - Versão do Python
  - Sistema operacional
  - Passos para reproduzir o problema
  - Mensagens de erro (se houver)
  - Screenshots (se relevante)

## Sugerindo Melhorias

- Use o sistema de issues do GitHub para sugerir melhorias
- Descreva claramente a funcionalidade que você gostaria de ver
- Explique por que essa melhoria seria útil
- Se possível, inclua exemplos de como a funcionalidade seria usada

## Enviando Pull Requests

1. Faça um fork do repositório
2. Crie uma branch para sua feature/fix:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. Faça commit das suas alterações:
   ```bash
   git commit -m "Adiciona nova funcionalidade"
   ```
4. Push para a branch:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
5. Abra um Pull Request

## Padrões de Código

- Siga o estilo de código PEP 8
- Use docstrings para documentar funções e classes
- Mantenha os comentários em português
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário

## Estrutura do Projeto

- `core/`: Contém a lógica de negócios
- `ui/`: Contém a interface do usuário
- `tests/`: Contém os testes unitários
- `docs/`: Contém a documentação

## Ambiente de Desenvolvimento

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Instale as dependências de desenvolvimento:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Testes

- Execute os testes antes de enviar um PR:
  ```bash
  python -m pytest
  ```
- Mantenha a cobertura de testes acima de 80%

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto. 