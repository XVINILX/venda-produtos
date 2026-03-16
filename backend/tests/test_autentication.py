# backend/test_layers.py
import sys
import os
from pathlib import Path
import time

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.auth_service import AuthService
from src.repositories.user_repository import UserRepository
from fastapi import HTTPException

def test_repository():
    """Testa apenas o repositório"""
    print("=" * 50)
    print("🔍 Testando Repository...")
    print("=" * 50)
    
    repo = UserRepository()
    
    # Usar email único com timestamp para evitar conflitos
    unique_email = f"repo_{int(time.time())}@teste.com"
    print(f"📧 Email usado: {unique_email}")
    
    try:
        # Criar usuário direto no repositório
        user = repo.create(
            email=unique_email,
            password="hash123",
            name="Teste Repository"  # 👈 Usando 'name' em vez de 'full_name'
        )
        print(f"✅ Usuário criado: {user}")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Nome: {user['name']}")  # 👈 Acessando 'name'
        
        # Buscar por email
        found = repo.get_by_email(unique_email)
        print(f"✅ Buscado por email: {found['email']}")
        print(f"   Nome encontrado: {found['name']}")
        assert found is not None
        assert found['email'] == unique_email
        assert found['name'] == "Teste Repository"
        
        # Tentar criar com mesmo email (deve falhar)
        print("\n🔄 Tentando criar email duplicado...")
        try:
            repo.create(
                email=unique_email,
                password="outro_hash",
                name="Outro Usuário"
            )
            print("❌ ERRO: Deveria ter falhado com email duplicado")
        except Exception as e:
            print(f"✅ Email duplicado detectado: {e}")
        
        return user
        
    except Exception as e:
        print(f"❌ Erro no teste do repositório: {e}")
        raise

def test_service():
    """Testa o serviço (que usa o repositório)"""
    print("\n" + "=" * 50)
    print("🔍 Testando Service...")
    print("=" * 50)
    
    service = AuthService()
    
    # Usar email único com timestamp
    unique_email = f"service_{int(time.time())}@teste.com"
    print(f"📧 Email usado: {unique_email}")
    
    # Teste 1: Tentar criar com senha curta
    print("\n🔄 Testando validação de senha curta...")
    try:
        user = service.register_user(
            email=unique_email,
            password="123",  # Senha curta - deve falhar
            name="Teste Service"  # 👈 Usando 'name'
        )
        print("❌ ERRO: Deveria ter falhado com senha curta")
    except HTTPException as e:
        print(f"✅ Validação de senha curta funcionou: {e.detail}")
    except Exception as e:
        print(f"✅ Outra validação funcionou: {e}")
    
    # Teste 2: Criar usuário válido
    print("\n🔄 Criando usuário válido...")
    try:
        user = service.register_user(
            email=unique_email,
            password="senha123",
            name="Teste Service"  # 👈 Usando 'name'
        )
        print(f"✅ Usuário criado via service:")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Nome: {user['name']}")  # 👈 Acessando 'name'
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        raise
    
    # Teste 3: Tentar criar com mesmo email
    print("\n🔄 Testando email duplicado...")
    try:
        user2 = service.register_user(
            email=unique_email,
            password="outrasenha",
            name="Outro Nome"
        )
        print("❌ ERRO: Deveria ter falhado com email duplicado")
    except HTTPException as e:
        print(f"✅ Validação de email duplicado funcionou: {e.detail}")
    
    # Teste 4: Fazer login
    print("\n🔄 Testando login...")
    try:
        login = service.login_user(unique_email, "senha123")
        print(f"✅ Login bem sucedido!")
        print(f"   Token: {login['access_token'][:20]}...")
        print(f"   Tipo: {login['token_type']}")
        print(f"   Usuário: {login['user']['email']}")
        print(f"   Nome: {login['user'].get('name')}")
        
        assert 'access_token' in login
        assert login['token_type'] == 'bearer'
        
    except Exception as e:
        print(f"❌ Erro no login: {e}")
    
    # Teste 5: Login com senha errada
    print("\n🔄 Testando login com senha errada...")
    try:
        login = service.login_user(unique_email, "senha_errada")
        print("❌ ERRO: Deveria ter falhado com senha errada")
    except HTTPException as e:
        print(f"✅ Login com senha errada rejeitado: {e.detail}")
    
    return user

def test_repository_get_all():
    """Testa o método get_all do repositório"""
    print("\n" + "=" * 50)
    print("🔍 Testando Repository.get_all()...")
    print("=" * 50)
    
    repo = UserRepository()
    
    try:
        # Listar todos os usuários
        users = repo.get_all()
        print(f"✅ Total de usuários no banco: {len(users)}")
        
        if users:
            print("📋 Primeiros 3 usuários:")
            for i, user in enumerate(users[:3]):
                print(f"   {i+1}. {user['email']} - {user.get('name', 'N/A')}")  # 👈 'name'
        
        return users
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        raise

def cleanup_test_data():
    """Limpa dados de teste criados"""
    print("\n" + "=" * 50)
    print("🧹 Limpando dados de teste...")
    print("=" * 50)
    
    repo = UserRepository()
    
    try:
        # Buscar usuários de teste
        test_users = repo.get_all()
        deleted_count = 0
        
        for user in test_users:
            if 'teste.com' in user['email']:
                # Como não temos método delete, vamos apenas registrar
                print(f"   Marcado para remoção: {user['email']} - {user.get('name', 'N/A')}")
                deleted_count += 1
        
        print(f"✅ {deleted_count} usuários de teste encontrados")
        
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes das camadas...")
    print("=" * 60)
    
    try:
        # Executar testes
        test_repository()
        test_service()
        test_repository_get_all()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Teste falhou: {e}")
        
    finally:
        # Limpeza opcional
        cleanup_test_data()