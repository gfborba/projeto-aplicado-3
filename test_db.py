#!/usr/bin/env python
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from usuarios.models import Organizador

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        # Testar conexão básica
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão com banco de dados OK")
        
        # Testar se as tabelas existem
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('auth_user', 'usuarios_organizador')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tabelas encontradas: {tables}")
        
        # Testar criação de usuário
        try:
            # Verificar se já existe um usuário de teste
            test_user = User.objects.filter(username='test_user_123').first()
            if test_user:
                test_user.delete()
            
            # Criar usuário de teste
            user = User.objects.create_user(
                username='test_user_123',
                first_name='Teste',
                last_name='Usuário',
                email='teste@teste.com',
                password='teste123'
            )
            print("✅ Criação de usuário OK")
            
            # Criar organizador de teste
            organizador = Organizador.objects.create(
                user=user,
                cep='88060-258',
                estado='SC',
                cidade='Florianópolis',
                bairro='Centro',
                logradouro='Rua Teste',
                numero='123',
                telefone='(48) 99999-9999'
            )
            print("✅ Criação de organizador OK")
            
            # Limpar dados de teste
            organizador.delete()
            user.delete()
            print("✅ Limpeza de dados de teste OK")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário/organizador: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False

def check_environment():
    """Verifica as variáveis de ambiente"""
    print("🔍 Verificando variáveis de ambiente:")
    
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL configurada: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL não configurada")
    
    debug = os.getenv('DEBUG', 'True')
    print(f"📝 DEBUG: {debug}")
    
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        print("✅ SECRET_KEY configurada")
    else:
        print("❌ SECRET_KEY não configurada")

if __name__ == "__main__":
    print("🚀 Iniciando testes de banco de dados...")
    print("=" * 50)
    
    check_environment()
    print("-" * 50)
    
    success = test_database_connection()
    
    print("=" * 50)
    if success:
        print("🎉 Todos os testes passaram!")
    else:
        print("💥 Alguns testes falharam!") 