# Projeto Eventos

Sistema de gerenciamento de eventos desenvolvido em Django.

## Setup do Projeto

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/gfborba/projeto-aplicado-3
cd projeto-aplicado-3
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados**
```bash
python manage.py migrate
```

5. **Crie um superusuário (opcional)**
```bash
python manage.py createsuperuser
```

6. **Execute o servidor**
```bash
python manage.py runserver
```