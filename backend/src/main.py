from fastapi import FastAPI
from src.database import SessionLocal
from src.auth.password import hash_password
from src.models.user import User
from src.routes import dashboard_routes
from src.routes import user_routes
from src.routes import cart_routes, product_routes
from src.routes import auth_routes
from fastapi.middleware.cors import CORSMiddleware
import os
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

@app.on_event("startup")
async def create_super_admin():
    """
    Cria um usuário super admin automaticamente se não existir.
    As credenciais podem ser configuradas via variáveis de ambiente.
    """
    db = SessionLocal()
    try:
        # Configurações do super admin (via env ou defaults)
        admin_email = os.getenv("SUPER_ADMIN_EMAIL", "admin@wisesales.com")
        admin_password = os.getenv("SUPER_ADMIN_PASSWORD", "Admin@123456")
        admin_name = os.getenv("SUPER_ADMIN_NAME", "Super Administrador")
        
        # Verificar se já existe algum admin
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        
        if existing_admin:
            print(f"✅ Admin já existe: {existing_admin.email}")
            return
        
        # Verificar se o email específico já está em uso
        existing_user = db.query(User).filter(User.email == admin_email).first()
        
        if existing_user:
            # Se o usuário existe mas não é admin, tornar admin
            if not existing_user.is_admin:
                existing_user.is_admin = True
                db.commit()
                print(f"✅ Usuário {admin_email} promovido a admin")
            return
        
        # Criar novo super admin
        hashed_password = hash_password(admin_password)
        super_admin = User(
            email=admin_email,
            password=hashed_password,
            name=admin_name,
            is_active=True,
            is_admin=True
        )
        
        db.add(super_admin)
        db.commit()
                
    except Exception as e:
        print(f"❌ Erro ao criar super admin: {e}")
        db.rollback()
    finally:
        db.close()
# Incluir rotas
app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(cart_routes.router)
app.include_router(user_routes.router)
app.include_router(dashboard_routes.router)
@app.get("/")
async def root():
    return {
        "message": "Wise Sales API",
        "docs": "/docs",
        "redoc": "/redoc"
    }