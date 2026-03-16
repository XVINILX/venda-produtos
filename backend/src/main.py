# backend/src/main.py
from fastapi import FastAPI
from src.routes import auth_routes

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

# Incluir rotas
app.include_router(auth_routes.router)

@app.get("/")
async def root():
    return {
        "message": "Wise Sales API",
        "docs": "/docs",
        "redoc": "/redoc"
    }