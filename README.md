# Teste Técnico — Desenvolvedor Fullstack Python + React (Júnior/Pleno)

Empresa: Wise Sales
Nível: Júnior / Pleno (mesmo teste, avaliação pela qualidade da entrega)
Tempo estimado: 3 a 4 horas
Prazo de entrega: 7 dias corridos
Entrega: repositório público no GitHub

---

## Sobre a Wise Sales

A Wise Sales trabalha com vendas inteligentes. A stack do dia a dia é Python serverless no backend e React no frontend. Este teste simula um cenário próximo dessa rotina, cobrindo backend e frontend em partes iguais.

Júnior e pleno fazem o mesmo teste. A diferença está na entrega: esperamos que pleno entregue mais funcionalidades, código melhor organizado, tratamento de erros mais completo e alguns diferenciais. Júnior deve focar em entregar o que é obrigatório, com clareza e código funcional.

### Sobre o uso de IA

O uso de ferramentas de IA (Copilot, ChatGPT, Claude, etc.) é permitido. Porém, na entrevista técnica, o time da Wise Sales vai perguntar sobre o que você fez e por que fez de determinada forma. Saber explicar cada decisão é parte da avaliação. Usar IA sem entender o resultado é pior do que não usar.

---

## Setup inicial

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+
- Node.js 18+

### Subindo o banco de dados

```bash
cp .env.example .env
docker compose up -d
```

O PostgreSQL sobe na porta 5432 com os dados de seed já carregados. O script `seed.sql` cria as tabelas (`products`, `coupons`, `cart_items`) e insere os dados iniciais automaticamente.

### Verificando se o seed funcionou

```bash
docker compose exec db psql -U wisesales -c "SELECT name, stock FROM products ORDER BY id;"
```

Você deve ver 6 produtos. Se não ver, verifique os logs com `docker compose logs db`.

### Variáveis de ambiente

O `.env.example` tem as credenciais do banco:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wisesales
DB_USER=wisesales
DB_PASSWORD=wisesales123
```

### O que já vem pronto

| Arquivo              | O que faz                               |
| -------------------- | --------------------------------------- |
| `docker-compose.yml` | Sobe PostgreSQL 16 com seed automático  |
| `seed.sql`           | Cria tabelas e insere produtos + cupons |
| `.env.example`       | Credenciais do banco                    |

### O que você precisa criar

Todo o código backend e frontend. A estrutura é livre, mas sugerimos:

```
/
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── services/
│   │   └── repositories/
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docker-compose.yml
├── seed.sql
└── .env
```

---

## Projeto: Mini E-commerce — Catálogo + Carrinho de Compras

Desenvolva um mini e-commerce fullstack com catálogo de produtos e carrinho de compras. O backend é a API em Python, o frontend é a interface em React.

### Parte 1: Backend Python (50%)

Arquitetura N-layered (service/repository). Python 3.11, psycopg2 com raw SQL queries (sem ORM). Migrações com Alembic.

#### 1. API de Produtos

- `GET /products` — Lista produtos. Aceita query param `?category=` para filtrar por categoria
- `GET /products/:id` — Retorna um produto específico com dados completos (incluindo estoque)

#### 2. API de Carrinho

- `GET /cart` — Retorna o carrinho atual com itens, quantidades, preço unitário, subtotal por item e total geral. Se houver cupom aplicado, mostra o desconto e o total final
- `POST /cart/items` — Adiciona produto ao carrinho. Body: `{ "product_id": int, "quantity": int }`
  - Regra: validar que o produto existe e que há estoque suficiente. Se o produto já estiver no carrinho, somar a quantidade (respeitando o estoque)
- `PATCH /cart/items/:id` — Atualiza a quantidade de um item do carrinho. Body: `{ "quantity": int }`
  - Regra: validar estoque. Se `quantity` = 0, remover o item
- `DELETE /cart/items/:id` — Remove um item do carrinho

#### 3. Cupom de desconto

- `POST /cart/coupon` — Aplica um cupom ao carrinho. Body: `{ "code": string }`
  - Regra: validar que o cupom existe, está ativo e não expirou
  - Cupons podem ser percentuais (ex: 10% de desconto) ou de valor fixo (ex: R$15 de desconto)
  - O desconto nunca pode resultar em total negativo (mínimo R$0)

#### Regras gerais do backend

- Validação de dados na entrada de cada endpoint
- Mensagens de erro claras e status HTTP corretos (400 para validação, 404 para não encontrado, 409 para conflitos)
- Separação em camadas: routes → services → repositories
- Connection pooling com psycopg2

### Parte 2: Frontend React (50%)

React + Vite, SPA, JavaScript (sem TypeScript), Tailwind CSS.

#### 1. Página de Catálogo

- Listagem de produtos com nome, preço e imagem placeholder
- Filtro por categoria (dropdown ou botões)
- Indicação visual de "fora de estoque" para produtos com estoque 0
- Botão "Adicionar ao carrinho" (desabilitado se estoque 0)

#### 2. Página de Carrinho

- Lista de itens no carrinho com nome, preço unitário, quantidade e subtotal
- Controle de quantidade (+ / -) com validação de estoque
- Botão de remover item
- Campo para digitar código de cupom e botão para aplicar
- Exibição do subtotal, desconto (se houver) e total final
- Mensagem quando o carrinho está vazio

#### 3. Estado global

- Context API para gerenciar o estado do carrinho
- O estado do carrinho deve persistir entre navegações (não precisa persistir no refresh)

#### Regras gerais do frontend

- Feedback visual nas ações (loading ao adicionar item, mensagem de erro/sucesso)
- Layout que funcione em desktop e mobile
- Navegação entre catálogo e carrinho (React Router ou equivalente)

### Requisitos técnicos

- **Backend**: Python 3.11, psycopg2 (raw queries, sem ORM), arquitetura N-layered
- **Migrações**: Alembic
- **Frontend**: React + Vite, JavaScript, Tailwind CSS, Context API
- **Testes backend**: pytest com cobertura mínima de 80%
- **Testes frontend**: Vitest
- **Linting**: Ruff (backend), ESLint + Prettier (frontend)
- **Git**: commits atômicos com mensagens descritivas

### Diferenciais (não obrigatórios)

- Implementar arquitetura container + bundle dinâmico: um container em Vanilla JS que carrega o bundle React via tag `<script>` dinâmica. Isso simula o modelo real da Wise Sales, onde um container leve orquestra o carregamento de bundles hospedados em CDN
- Testes de integração (além dos unitários)
- Documentação da API (Swagger, Postman collection, ou seção no README)
- Docker Compose para subir o projeto completo (backend + frontend + banco)
- GitHub Actions para rodar testes e linting

---

## Critérios de avaliação

| Critério                                  | Peso |
| ----------------------------------------- | ---- |
| Funcionamento end-to-end (API + Frontend) | 25%  |
| Qualidade do código (backend e frontend)  | 25%  |
| Modelagem de dados e lógica de negócio    | 15%  |
| Experiência do usuário (usabilidade)      | 15%  |
| Testes (pytest + Vitest)                  | 10%  |
| README e documentação                     | 10%  |

---

## Fluxo do processo

1. Teste take-home: você recebe este repositório, desenvolve a solução e envia o link do seu repositório GitHub em até 7 dias
2. Avaliação técnica: o código entregue é avaliado com base nos critérios deste documento
3. Entrevista técnica com a Wise Sales: baseada no projeto entregue, o time avalia raciocínio, entendimento da solução e decisões técnicas

---

## Instruções de entrega

Crie um repositório público no GitHub com um `README.md` que contenha: descrição do projeto e funcionalidades implementadas, tecnologias utilizadas e por que as escolheu, instruções de instalação e execução (o projeto precisa rodar seguindo o README), decisões técnicas relevantes e o que faria diferente com mais tempo.

### Prazo

7 dias corridos a partir do recebimento do teste.

### O que valorizamos

Código limpo e organizado importa mais do que quantidade de features. Commits bem escritos mostram como você pensa. README bem feito mostra que você sabe se comunicar tecnicamente. Tratamento de erros, validações e separação de responsabilidades contam bastante. Raw SQL bem escrito e legível conta pontos. O projeto precisa rodar seguindo o README, sem ajustes.

### O que não valorizamos

Over-engineering para o escopo proposto. Código sem tratamento de erros. Repositório com um commit gigante. README genérico ou vazio. Projeto que não roda. Usar ORM quando o requisito é raw SQL.

---

## Rubrica de avaliação

| Nota | Classificação | Descrição                                                              |
| ---- | ------------- | ---------------------------------------------------------------------- |
| 9-10 | Excelente     | Atende todos os requisitos, implementa diferenciais, código exemplar   |
| 7-8  | Bom           | Atende os requisitos principais, código organizado, poucas falhas      |
| 5-6  | Satisfatório  | Funciona parcialmente, organização básica, precisa de melhorias        |
| 3-4  | Insuficiente  | Muitas falhas, código desorganizado, requisitos principais incompletos |
| 0-2  | Eliminatório  | Não funciona, plágio evidente, ou entrega vazia                        |

Nota mínima para aprovação: 6.0

### Diferenciação Júnior vs Pleno

| Aspecto         | Júnior (esperado)          | Pleno (esperado)                                                |
| --------------- | -------------------------- | --------------------------------------------------------------- |
| Funcionalidades | Obrigatórias funcionando   | Obrigatórias + diferenciais                                     |
| Código          | Organizado e legível       | Bem estruturado, com patterns claros (service/repository)       |
| SQL             | Queries funcionais         | Queries otimizadas, parametrizadas, sem SQL injection           |
| Erros           | Tratamento básico          | Tratamento completo com mensagens claras e status HTTP corretos |
| Testes          | Unitários básicos (pytest) | Unitários + integração, mocks, fixtures                         |
| Carrinho        | Funciona pro caso comum    | Lida com edge cases (estoque, cupom expirado, quantidade 0)     |
| Frontend        | Funcional, visual básico   | Polido, loading states, feedback visual, responsivo             |

## Rodando localmente, modo DEV:

uvicorn src.main:app --host 0.0.0.0 --port 8000
