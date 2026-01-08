# Satellite TC Generator Web

- flask
- SQLalchemy
- Postgre
- SQLite

[English Version](#english-version) | [Versão em Português](#versão-em-português)

---

## English Version

This module is part of the **Control Server** in the Ground Station software stack. It provides a web interface for operators to generate and schedule satellite telecommands (TC).

### 🚀 Key Features
- **Clean Architecture**: Separation of concerns using Repository and Service patterns.
- **Database Factory**: Modular support for PostgreSQL (Production/Docker) and SQLite (Local testing).
- **Scalability**: Built with Flask's Application Factory pattern.
- **Microservices Ready**: Optimized for Docker containerization.

### 📂 Project Structure
```plaintext
/tc_generator_web
├── app
│        ├── app.py
│        ├── database
│        │        ├── __pycache__
│        │        │        └── database_config.cpython-311.pyc
│        │        ├── adapters
│        │        │        ├── __pycache__
│        │        │        │        ├── postgres_adapter.cpython-311.pyc
│        │        │        │        └── sqlite_adapter.cpython-311.pyc
│        │        │        ├── postgres_adapter.py
│        │        │        └── sqlite_adapter.py
│        │        ├── connector.py
│        │        ├── database_config.py
│        │        └── factories
│        │            ├── __pycache__
│        │            │        └── database_manager.cpython-311.pyc
│        │            └── database_manager.py
│        ├── models
│        │        ├── __init__.py
│        │        ├── execution_log.py
│        │        ├── operator.py
│        │        ├── satellite.py
│        │        └── telecommand.py
│        ├── routes
│        └── templates
├── readme.md
├── requirements.txt
├── resources
│        └── database
│            ├── README.md
│            ├── schema.sql
│            └── script_init_db.py
├── static
└── tests
    ├── __pycache__
    │        └── db_test.cpython-311.pyc
    └── db_test.py

16 directories, 22 files
```
### How to Run (Local Development)

To run the project outside Docker for debugging while keeping the database in a container:

1. Prerequisites: Python 3.10+, Conda, and Docker.

2. Setup Infrastructure:

    ```Bash
    # Start only the database container
    docker-compose up -d postgres
    ```
3. Configure Environment Variables:

    ```Bash
    # dialect+driver://username:password@host:port/database
    PG_DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/tc_generator
    # db test
    PG_DATABASE_URL_TEST=postgresql+psycopg2://username:password@localhost:5432/tc_generator_test
    # SQLite (used only if DB_TYPE=sqlite)
    SQLITE_DATABASE_URL=sqlite:///instance/tc_generator.db
    ```
4. Execute with Flask Server:

    ```Bash
    conda activate tc_generator_web
    flask run
    ```
---
## Versão em Português
Este módulo é parte do **Control Server** na estrutura de software da Estação Terrestre. Ele fornece uma interface web para que operadores possam gerar e agendar telecomandos (TC) de satélites.

###  Principais Funcionalidades

- **Arquitetura Limpa**: Separação de responsabilidades usando os padrões Repository e Service.

- **Database Factory**: Suporte modular para PostgreSQL (Produção/Docker) e SQLite (Testes locais).

- **Escalabilidade**: Construído utilizando o padrão Application Factory do Flask.

- **Pronto para Microserviços**: Otimizado para conteinerização com Docker.

### Estrutura do Projeto

- `manage.py`: Ponto de entrada da aplicação.

- `app/`: Pacote principal contendo a lógica dividida em camadas.

- `app/database/`: Implementação da Factory de banco de dados e adaptadores.

- `Dockerfile`: Instruções para criação da imagem de produção.

###  Como Executar (Desenvolvimento Local)

Para executar o projeto fora do Docker para fins de debug, mantendo apenas o banco de dados no container:

1. Pré-requisitos: Python 3.10+, Conda e Docker.

2. Subir Infraestrutura:
    
    ```Bash
    # \d - display (Inicia apenas o container do banco de dados)
    docker-compose up -d postgres
    ```

3. Configurar Variáveis de Ambiente:
    
    ```Bash
    # dialect+driver://username:password@host:port/database
    PG_DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/tc_generator
    # db test
    PG_DATABASE_URL_TEST=postgresql+psycopg2://username:password@localhost:5432/tc_generator_test
    # SQLite (usado apenas se DB_TYPE=sqlite)
    SQLITE_DATABASE_URL=sqlite:///instance/tc_generator.db
    ```
3. Executar via Flask:
    
    ```Bash
    conda activate tc_generator_web
    flask run
    ```
4. Observações / Notes

- No ambiente de produção (Docker), o servidor utilizado é o Gunicorn. / In production (Docker), the server used is Gunicorn.

- O banco de dados PostgreSQL deve estar com a tabela scheduled_telecommands devidamente criada. / PostgreSQL must have the scheduled_telecommands table correctly created.


---