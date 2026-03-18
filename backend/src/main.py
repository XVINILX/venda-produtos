# backend/src/main.py
from fastapi import FastAPI
from src.routes import cart_routes, product_routes
from src.routes import auth_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Wise Sales API",
    description="""
    API do Mini E-commerce Wise Sales
    
    ## Arquitetura
    - **Routes**: Camada HTTP
    - **Services**: Regras de negócio
    - **Repositories**: Acesso a dados
    - **Schemas**: Validação e documentação
    """,
    version="1.0.0",
    contact={
        "name": "Wise Sales",
        "email": "dev@wisesales.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # React default port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],  # Permite todos os headers
    expose_headers=["*"],
)

# Incluir rotas
app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(cart_routes.router)
@app.get("/")
async def root():
    return {
        "message": "Wise Sales API",
        "docs": "/docs",
        "redoc": "/redoc"
    }