Backend Wise Sales - Guia de Execução com Docker
📋 Pré-requisitos
Docker (versão 20.10+)

Docker Compose (versão 2.0+)

Python 3.11+ (apenas para desenvolvimento local)

Git

📦 Estrutura do Projeto
text
teste-fullstack-python-react-wisesales/
├── backend/
│ ├── src/
│ │ ├── routes/
│ │ ├── services/
│ │ ├── repositories/
│ │ ├── models/
│ │ └── main.py
│ ├── alembic/
│ ├── requirements.txt
│ └── Dockerfile
├── docker-compose.yml
├── seed.sql
└── .env.example
🚀 Passo a Passo para Executar o Backend com Docker

1. Clone o repositório
   bash
   git clone https://github.com/seu-usuario/teste-fullstack-python-react-wisesales.git
   cd teste-fullstack-python-react-wisesales
2. Configure as variáveis de ambiente
   bash

# Copie o arquivo de exemplo

cp .env.example .env

# Edite o arquivo .env com suas configurações (opcional)

nano .env
Conteúdo do .env.example:

env

# Database

DB_HOST=db
DB_PORT=5432
DB_NAME=wisesales
DB_USER=wisesales
DB_PASSWORD=wisesales123

# JWT

SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment

ENVIRONMENT=development
DEBUG=True 3. Inicie os containers com Docker Compose
bash

# Subir os containers em background

docker-compose up -d

# Verificar se os containers estão rodando

docker-compose ps
Você deve ver algo como:

text
NAME STATUS PORTS
teste-fullstack-python-react-wisesales-db-1 up 0.0.0.0:5434->5432/tcp
teste-fullstack-python-react-wisesales-backend-1 up 0.0.0.0:8000->8000/tcp 4. Verifique se o seed foi carregado corretamente
bash

# Verificar produtos no banco

docker exec -it teste-fullstack-python-react-wisesales-db-1 psql -U wisesales -d wisesales -c "SELECT id, name, stock FROM products ORDER BY id;"
Deverá mostrar 6 produtos iniciais.

5. Acesse a API
   API: http://localhost:8000

Documentação Swagger: http://localhost:8000/docs

Documentação ReDoc: http://localhost:8000/redoc

Health Check: http://localhost:8000/health
