#!/usr/bin/env python
"""
Script para verificar a configuração do banco de dados do Render
"""
import os

# URL do banco de dados fornecida pelo usuário
DATABASE_URL = "postgresql://eventos:HMVMhvxtdjAZvWNu3MMLH7LzAoc3kLga@dpg-d1c8unmuk2gs73ag0nl0-a.oregon-postgres.render.com/eventos_t50q"

print("🔍 Verificando configuração do banco de dados do Render")
print("=" * 60)

# Simular as configurações que o Django usaria
import dj_database_url

# Configurar a URL do banco
os.environ['DATABASE_URL'] = DATABASE_URL

# Parsear a URL
db_config = dj_database_url.parse(DATABASE_URL)

print("📋 Configuração do banco de dados:")
print(f"   Engine: {db_config.get('ENGINE', 'N/A')}")
print(f"   Host: {db_config.get('HOST', 'N/A')}")
print(f"   Port: {db_config.get('PORT', 'N/A')}")
print(f"   Database: {db_config.get('NAME', 'N/A')}")
print(f"   User: {db_config.get('USER', 'N/A')}")
print(f"   Password: {'*' * len(db_config.get('PASSWORD', '')) if db_config.get('PASSWORD') else 'N/A'}")

print("\n🔧 Configurações recomendadas para o Render:")
print("=" * 60)

print("1. Variáveis de ambiente que devem estar configuradas no Render:")
print("   DATABASE_URL=postgresql://eventos:HMVMhvxtdjAZvWNu3MMLH7LzAoc3kLga@dpg-d1c8unmuk2gs73ag0nl0-a.oregon-postgres.render.com/eventos_t50q")
print("   DEBUG=False")
print("   SECRET_KEY=<sua-chave-secreta>")
print("   ALLOWED_HOSTS=seu-app.onrender.com")

print("\n2. Verificar se o banco está acessível:")
print("   - O banco deve estar no status 'available'")
print("   - A URL externa deve estar funcionando")
print("   - As credenciais devem estar corretas")

print("\n3. Possíveis problemas:")
print("   - DATABASE_URL não configurada no Render")
print("   - Banco de dados não inicializado")
print("   - Migrações não aplicadas")
print("   - Problemas de conectividade")

print("\n4. Para testar a conexão no Render:")
print("   - Verificar os logs do aplicativo")
print("   - Executar python manage.py migrate no build")
print("   - Verificar se as tabelas foram criadas") 