#!/usr/bin/env bash
# Exit on error
set -o errexit

# Set Django settings module
export DJANGO_SETTINGS_MODULE=core.settings

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
echo "Aplicando migrações..."
python manage.py migrate --verbosity=2

# Verificar status das migrações
echo "Verificando status das migrações..."
python manage.py showmigrations

# Verificar conexão com banco de dados
echo "Testando conexão com banco de dados..."
python manage.py dbshell -c "SELECT version();" || echo "Erro na conexão com banco de dados"

# Verificar se as tabelas principais existem
echo "Verificando tabelas principais..."
python manage.py dbshell -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('auth_user', 'usuarios_organizador', 'usuarios_fornecedor');" || echo "Erro ao verificar tabelas"

echo "Build concluído!"