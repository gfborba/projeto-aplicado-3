#!/usr/bin/env python
"""
Script para debug específico do banco de dados do Render
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Simular ambiente de produção
os.environ['DATABASE_URL'] = "postgresql://eventos:HMVMhvxtdjAZvWNu3MMLH7LzAoc3kLga@dpg-d1c8unmuk2gs73ag0nl0-a.oregon-postgres.render.com/eventos_t50q"
os.environ['DEBUG'] = 'False'

django.setup()

from django.db import connection
from django.contrib.auth.models import User
from usuarios.models import Organizador

def test_database_operations():
    """Testa operações específicas que podem estar causando o erro 500"""
    print("🔍 Testando operações de banco de dados...")
    
    try:
        # 1. Testar conexão básica
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão básica OK")
        
        # 2. Verificar se as tabelas existem
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('auth_user', 'usuarios_organizador')
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tabelas encontradas: {tables}")
        
        # 3. Verificar estrutura da tabela auth_user
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'auth_user'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("📊 Estrutura da tabela auth_user:")
            for col in columns:
                print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # 4. Verificar estrutura da tabela usuarios_organizador
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'usuarios_organizador'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("📊 Estrutura da tabela usuarios_organizador:")
            for col in columns:
                print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # 5. Testar criação de usuário (simulação do cadastro)
        try:
            # Limpar usuário de teste se existir
            User.objects.filter(username='teste_cadastro').delete()
            
            # Criar usuário
            user = User.objects.create_user(
                username='teste_cadastro',
                first_name='Teste',
                last_name='Cadastro',
                email='teste@cadastro.com',
                password='teste123'
            )
            print("✅ Criação de usuário OK")
            
            # Criar organizador
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
            
            # Verificar se foi salvo corretamente
            organizador_salvo = Organizador.objects.get(user=user)
            print(f"✅ Organizador salvo: {organizador_salvo.user.username}")
            
            # Limpar dados de teste
            organizador.delete()
            user.delete()
            print("✅ Limpeza de dados de teste OK")
            
        except Exception as e:
            print(f"❌ Erro na simulação de cadastro: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_config():
    """Verifica a configuração do banco de dados"""
    print("🔧 Verificando configuração do banco...")
    
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config.get('ENGINE')}")
    print(f"Host: {db_config.get('HOST')}")
    print(f"Port: {db_config.get('PORT')}")
    print(f"Database: {db_config.get('NAME')}")
    print(f"User: {db_config.get('USER')}")
    print(f"Password: {'*' * len(db_config.get('PASSWORD', '')) if db_config.get('PASSWORD') else 'None'}")

if __name__ == "__main__":
    print("🚀 Debug do banco de dados do Render")
    print("=" * 60)
    
    check_database_config()
    print("-" * 60)
    
    success = test_database_operations()
    
    print("=" * 60)
    if success:
        print("🎉 Todos os testes passaram!")
    else:
        print("💥 Alguns testes falharam!") 