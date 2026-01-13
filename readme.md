# Satellite TC Generator Web

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)

[English Version](#english-version) | [Versão em Português](#versão-em-português)

---

## English Version

This module is part of the **Control Server** in the Ground Station software stack. It provides a modern web interface for operators to generate, schedule, and manage satellite telecommands (TC).

### 🚀 Key Features
- **Clean Architecture**: Separation of concerns using Models, Routes, and Templates.
- **Robust Data Modeling**: SQLAlchemy 2.0 ORM with comprehensive constraints and relationships.
- **Database Factory**: Modular support for PostgreSQL (Production/Docker) and SQLite (Local testing).
- **Modern UI**: Responsive Dashboard built with Bootstrap 5.
- **Testing**: Comprehensive test suite with `pytest` covering both Logic and Persistence layers.

### 📂 Project Structure
```plaintext
/tc_generator_web
├── app
│   ├── __init__.py          # Application Factory
│   ├── database
│   │   ├── adapters         # DB Adapters (Postgres/SQLite)
│   │   ├── factories        # DatabaseManager Factory
│   │   └── database_config.py
│   ├── models               # SQLAlchemy Models
│   │   ├── execution_log.py
│   │   ├── operator.py
│   │   ├── satellite.py
│   │   └── telecommand.py
│   ├── routes               # Web Controllers
│   │   └── web_routes.py
│   └── templates            # HTML Views (Jinja2)
│       ├── base.html
│       └── index.html
├── tests                    # Test Suite
│   └── models               # Model Tests (Behavior & Persistence)
├── run.py                   # Entry Point
├── readme.md
├── requirements.txt
└── resources
    └── database             # SQL Scripts
```

---
### Class Diagram
```mermaid
classDiagram
    class Operator {
        +int id
        +str username
        +str email
        +str full_name
        +str role
        +str status
        +verify_password()
    }

    class Satellite {
        +int id
        +str name
        +str code
        +str status
        +datetime updated_at
    }

    class Telecommand {
        +int id
        +str command_type
        +str status
        +int priority
        +datetime created_at
        +datetime sent_at
        +datetime confirmed_at
        +update_status()
    }

    class ExecutionLog {
        +int id
        +str status
        +str message
        +datetime created_at
    }

    Operator "1" -- "*" Telecommand : creates
    Operator "1" -- "*" ExecutionLog : generates
    Satellite "1" -- "*" Telecommand : receives
    Telecommand "1" -- "*" ExecutionLog : has

    note for Operator "Handles authentication and\nuser management"
    note for Satellite "Represents space assets\nwith tracking info"
    note for Telecommand "Commands sent to satellites\nwith priority and status"
    note for ExecutionLog "Audit trail for all\ncommand executions"
```

---
### 🛠️ How to Run (Local Development)

To run the project locally for development and debugging:

#### 1. Prerequisites
- Python 3.10+ (Conda recommended)
- Docker (for the PostgreSQL database)

#### 2. Setup Database Infrastructure
Start the PostgreSQL container using Docker Compose:
```bash
docker-compose up -d postgres
```
*Ensure the database schema is applied (tables created).*

#### 3. Configure Environment
Create a `.env` file in the root directory or export the variables:
```bash
# Connection String: dialect+driver://username:password@host:port/database
export PG_DATABASE_URL="postgresql+psycopg2://username:password@localhost:5432/tc_generator"
export PG_DATABASE_URL_TEST="postgresql+psycopg2://username:password@localhost:5432/tc_generator_test"
```

#### 4. Install Dependencies
```bash
conda create -n tc_generator_web python=3.11
conda activate tc_generator_web
pip install -r requirements.txt
```

#### 5. Run the Application
Execute the entry point script:
```bash
python run.py
```
Access the dashboard at: **http://localhost:5000**

#### 6. Run Tests
Execute the test suite to ensure everything is working:
```bash
pytest tests/
```

---

## Versão em Português

Este módulo é parte do **Control Server** na estrutura de software da Estação Terrestre. Ele fornece uma interface web moderna para que operadores possam gerar, agendar e gerenciar telecomandos (TC) de satélites.

### 🚀 Principais Funcionalidades
- **Arquitetura Limpa**: Separação de responsabilidades usando Models, Routes e Templates.
- **Modelagem Robusta**: ORM SQLAlchemy 2.0 com restrições e relacionamentos completos.
- **Database Factory**: Suporte modular para PostgreSQL (Produção/Docker) e SQLite (Testes locais).
- **Interface Moderna**: Dashboard responsivo construído com Bootstrap 5.
- **Testes**: Suíte de testes abrangente com `pytest` cobrindo camadas de Lógica e Persistência.

### 🛠️ Como Executar (Desenvolvimento Local)

Para executar o projeto localmente para desenvolvimento e debug:

#### 1. Pré-requisitos
- Python 3.10+ (Recomendado usar Conda)
- Docker (para o banco de dados PostgreSQL)

#### 2. Subir Infraestrutura de Banco de Dados
Inicie o container PostgreSQL usando Docker Compose:
```bash
docker-compose up -d postgres
```
*Certifique-se de que o esquema do banco de dados foi aplicado (tabelas criadas).*

#### 3. Configurar Ambiente
Crie um arquivo `.env` na raiz ou exporte as variáveis:
```bash
# String de Conexão: dialect+driver://username:password@host:port/database
export PG_DATABASE_URL="postgresql+psycopg2://username:password@localhost:5432/tc_generator"
export PG_DATABASE_URL_TEST="postgresql+psycopg2://username:password@localhost:5432/tc_generator_test"
```

#### 4. Instalar Dependências
```bash
conda create -n tc_generator_web python=3.11
conda activate tc_generator_web
pip install -r requirements.txt
```

#### 5. Executar a Aplicação
Execute o script de entrada:
```bash
python run.py
```
Acesse o dashboard em: **http://localhost:5000**

#### 6. Executar Testes
Execute a suíte de testes para garantir que tudo está funcionando:
```bash
pytest tests/
```