# Satellite TC Generator Web

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)

[English Version](#english-version) | [Versão em Português](#versão-em-português)

---

## English Version

This module is part of the **Control Server** in the Ground Station software stack. It provides a modern web interface for operators to generate, schedule, and manage satellite telecommands (TC).

### 🚀 Key Features
- **Professional MVC Architecture**: Separation of concerns with Models, Routes (Controllers), Services, and Templates (Views).
- **Service Layer**: Dedicated business logic layer (`TelecommandService`, `SatelliteService`) for clean separation from HTTP concerns.
- **Structured Logging**: Comprehensive logging throughout the application for traceability and debugging.
- **Robust Data Modeling**: SQLAlchemy 2.0 ORM with comprehensive constraints, relationships, and eager-loading optimization.
- **Database Factory**: Modular support for PostgreSQL (Production/Docker) and SQLite (Local testing).
- **Modern UI**: Responsive "Mission Control" Dashboard built with Bootstrap 5.
- **Dockerized**: Fully automated setup with Docker Compose.
- **Signal Detection**: Real-time UDP packet monitoring with configurable thresholds and hysteresis-based false positive reduction.

### 📂 Project Structure
```plaintext
/tc_generator_web
├── app
│   ├── __init__.py                    # Application Factory
│   ├── database                       # DB Adapters & Factory
│   │   └── factories
│   │       └── database_manager.py    # Session Management
│   ├── models                         # SQLAlchemy ORM Models
│   │   ├── operator.py
│   │   ├── satellite.py
│   │   ├── telecommand.py
│   │   └── execution_log.py
│   ├── routes                         # Web Controllers (HTTP Handlers)
│   │   └── web_routes.py              # Thin route layer delegating to services
│   ├── services                       # Business Logic Layer (NEW)
│   │   ├── __init__.py
│   │   ├── telecommand_service.py     # Telecommand CRUD & Dashboard Logic
│   │   └── satellite_service.py       # Satellite CRUD & Management
│   └── templates                      # HTML Views (Jinja2)
│       ├── index.html                 # Dashboard
│       └── spectrum-monitor.html      # RF Signal Monitoring
├── tests                              # Test Suite
├── resources
│   └── database                       # SQL Scripts (Schema)
├── docker-compose.yml                 # Container Orchestration
├── Dockerfile                         # App Container Definition
├── run.py                             # Entry Point (UDP Worker + Flask Server)
└── requirements.txt                   # Python Dependencies
```

### 🏗️ Architecture Overview

The tc-generator follows a **professional MVC + Service Layer** architecture:

```
HTTP Request
    ↓
  Routes (Controllers) ← thin layer, handles HTTP concerns
    ↓
  Services (Business Logic) ← encapsulates telecommand/satellite operations
    ↓
  Models (Domain Objects) ← SQLAlchemy ORM entities with eager-loading
    ↓
Database (PostgreSQL) ← persistent data store
```

**Key Design Decisions:**
- **Services are stateless**: Each service method opens and closes its own session, ensuring proper resource cleanup and avoiding detached-instance errors.
- **Eager Loading**: Related entities (satellite, operator) are eager-loaded within service queries before the session closes, so Jinja2 templates can safely access relationships.
- **Logging**: Every operation is logged for operational visibility and debugging (INFO for successful actions, WARNING for validation issues, ERROR for exceptions).
- **Structured Error Handling**: Services raise domain-specific exceptions (ValueError, LookupError) that routes convert to appropriate HTTP responses.

---
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

### � Service Layer Implementation

The application follows a **professional service-oriented architecture** with the following services:

#### **TelecommandService**
Encapsulates all telecommand business logic:
- `get_dashboard_data()`: Retrieves grouped telecommands (pending, sent, history) with eager-loaded relationships
- `create(data)`: Validates and persists new telecommands
- `update(tc_id, data)`: Applies updates to existing telecommands
- `delete(tc_id)`: Removes telecommands

**Key features:**
- Eager-loads `satellite` and `operator` relationships to prevent detached-instance errors in templates
- Structured error handling with specific exception types
- Comprehensive logging for audit trails

#### **SatelliteService**
Manages satellite CRUD operations and validation:
- `list_all()`: Retrieves all satellites
- `create(data)`: Creates new satellite records
- `update(sat_id, data)`: Updates satellite details
- `delete(sat_id)`: Removes satellites

---

### 📝 Logging Standards

All operations are logged using Python's `logging` module:

- **INFO**: Successful operations (e.g., "Telecommand created: SYSTEM_REBOOT")
- **WARNING**: Validation failures or recoverable issues (e.g., "Invalid telecommand payload")
- **ERROR**: Exceptions and unrecoverable failures (with full traceback)

Example log output:
```
2026-08-30 15:19:09 INFO Loading dashboard page
2026-08-30 15:19:09 INFO Creating telecommand via web form
2026-08-30 15:19:09 INFO Telecommand created: SYSTEM_REBOOT for satellite 1
2026-08-30 15:19:09 INFO Updating satellite 3
2026-08-30 15:19:09 INFO Satellite updated: Catarina-A1 (SAT-OBS-001)
```

---

### �🛠️ How to Run (Quick Start with Docker)

The easiest way to run the project is using Docker Compose. This will set up the Database, Web App, and PGAdmin automatically.

#### 1. Prerequisites
- Docker & Docker Compose installed.

#### 2. Run the Application
Execute the following command in the project root:
```bash
    docker-compose up --build
```
*This will build the Python image, start PostgreSQL, initialize the database schema, and launch the web server.*

#### 3. Access the Services
- **Web Dashboard:** [http://localhost:5000](http://localhost:5000)
- **PGAdmin (Database UI):** [http://localhost:5050](http://localhost:5050)
  - **Email:** `admin@spacelab.com`
  - **Password:** `admin`
---
#### 4. Examples of Telecommands (JSON)

These examples demonstrate how parameters should be structured when sending commands via a web interface or API.

1. Shutdown (Subsystem Shutdown)

Used to cut power to a specific bus (e.g., Payload) to save battery power.

```json
    {
          "command_type": "SHUTDOWN_SUBSYSTEM",
          "parameters": {
                "subsystem": "PAYLOAD_LORA",
                "delay_seconds": 0,
                "confirmation_key": "0xDEADBEEF"
          }
    }

```
2. Reboot (System Restart)

Command to reset the onboard computer (OBDH).
```json
    {
          "command_type": "SYSTEM_REBOOT",
          "parameters": {
                "target": "OBDH",
                "type": "cold_start",
                "clear_volatile_memory": true
          }
    }

```
3. Battery (Heater Setting)

Adjusts the heater's duty cycle to maintain the battery at operating temperature.

```json
    {
          "command_type": "SET_HEATER_DC",
          "parameters": {
                "heater_id": 1,
                "duty_cycle_percent": 85,
                "mode": "manual"
          }
    }

```
4. Return Reading (Request Telemetry)

Requests that the satellite send an immediate packet of specific telemetry (e.g., radio temperature).

```json
    {
          "command_type": "REQUEST_TELEMETRY",
          "parameters": {
                "variable_name": "ttc_radio1_temp",
                "samples": 5,
                "interval_ms": 100
          }
    }

```
> Note: The parameters field is a JSONB object. Its structure varies depending on the command_type. Always refer to the satellite's technical manual for the required keys for each command.
---

### 🔧 How to Run (Manual / Local Development)

If you prefer to run the Python application locally (outside Docker) for debugging:

#### 1. Prerequisites
- Python 3.11+ (Conda recommended)
- PostgreSQL Database running (you can use `docker-compose up -d postgres`)

#### 2. Configure Environment
Create a `.env` file in the root directory:
```bash
    # Connection String: dialect+driver://username:password@host:port/database
    export PG_DATABASE_URL="postgresql+psycopg2://admin:admin@localhost:5432/telecommand_db"
```

#### 3. Install Dependencies
```bash
    conda create -n tc_generator_web python=3.11
    conda activate tc_generator_web
    pip install -r requirements.txt
```

#### 4. Run the Application
```bash
  python run.py
```

---

## Versão em Português

Este módulo é parte do **Control Server** na estrutura de software da Estação Terrestre. Ele fornece uma interface web moderna para que operadores possam gerar, agendar e gerenciar telecomandos (TC) de satélites.

### 🚀 Principais Funcionalidades
- **Arquitetura MVC Profissional**: Separação de responsabilidades com Models, Routes (Controllers), Services e Templates (Views).
- **Camada de Serviços**: Camada dedicada de lógica de negócios (`TelecommandService`, `SatelliteService`) para separação limpa das preocupações HTTP.
- **Logging Estruturado**: Logging abrangente em toda a aplicação para rastreabilidade e depuração.
- **Modelagem Robusta**: ORM SQLAlchemy 2.0 com restrições, relacionamentos e otimização de eager-loading.
- **Interface Moderna**: Dashboard estilo "Mission Control" responsivo.
- **Dockerizado**: Configuração automatizada com Docker Compose.
- **Detecção de Sinais**: Monitoramento de pacotes UDP em tempo real com limiar configurável e redução de falsos positivos baseada em histerese.

---

### 🏗️ Camada de Serviços

A aplicação segue uma **arquitetura orientada a serviços profissional** com os seguintes serviços:

#### **TelecommandService**
Encapsula toda a lógica de negócios de telecomandos:
- `get_dashboard_data()`: Recupera telecomandos agrupados (pendentes, enviados, histórico) com relacionamentos carregados antecipadamente
- `create(data)`: Valida e persiste novos telecomandos
- `update(tc_id, data)`: Aplica atualizações a telecomandos existentes
- `delete(tc_id)`: Remove telecomandos

**Características principais:**
- Carregamento antecipado de relacionamentos `satellite` e `operator` para evitar erros de instância destacada em templates
- Tratamento estruturado de erros com tipos de exceção específicos
- Logging abrangente para trilhas de auditoria

#### **SatelliteService**
Gerencia operações CRUD de satélites e validação:
- `list_all()`: Recupera todos os satélites
- `create(data)`: Cria novos registros de satélites
- `update(sat_id, data)`: Atualiza detalhes do satélite
- `delete(sat_id)`: Remove satélites

---

### 📝 Padrões de Logging

Todas as operações são registradas usando o módulo `logging` do Python:

- **INFO**: Operações bem-sucedidas (ex: "Telecommand created: SYSTEM_REBOOT")
- **WARNING**: Falhas de validação ou problemas recuperáveis (ex: "Invalid telecommand payload")
- **ERROR**: Exceções e falhas irrecuperáveis (com rastreamento completo)

Exemplo de saída de log:
```
2026-08-30 15:19:09 INFO Loading dashboard page
2026-08-30 15:19:09 INFO Creating telecommand via web form
2026-08-30 15:19:09 INFO Telecommand created: SYSTEM_REBOOT for satellite 1
2026-08-30 15:19:09 INFO Updating satellite 3
2026-08-30 15:19:09 INFO Satellite updated: Catarina-A1 (SAT-OBS-001)
```

---

A maneira mais fácil de rodar o projeto é usando Docker Compose. Isso configurará o Banco de Dados, a Aplicação Web e o PGAdmin automaticamente.

#### 1. Pré-requisitos
- Docker & Docker Compose instalados.

#### 2. Executar a Aplicação
Execute o seguinte comando na raiz do projeto:
```bash
docker-compose up --build
```
*Isso construirá a imagem Python, iniciará o PostgreSQL, inicializará o esquema do banco de dados e lançará o servidor web.*

#### 3. Acessar os Serviços
- **Dashboard Web:** [http://localhost:5000](http://localhost:5000)
- **PGAdmin (Interface do Banco):** [http://localhost:5050](http://localhost:5050)
  - **Email:** `admin@spacelab.com`
  - **Senha:** `admin`

---

### 🔧 Como Executar (Manual / Desenvolvimento Local)

Se preferir rodar a aplicação Python localmente (fora do Docker) para depuração:

#### 1. Pré-requisitos
- Python 3.11+ (Recomendado usar Conda)
- Banco de dados PostgreSQL rodando (você pode usar `docker-compose up -d postgres`)

#### 2. Configurar Ambiente
Crie um arquivo `.env` na raiz ou exporte as variáveis:
```bash
    # String de Conexão: dialect+driver://username:password@host:port/database
    export PG_DATABASE_URL="postgresql+psycopg2://admin:admin@localhost:5432/telecommand_db"
```

#### 3. Instalar Dependências
```bash
    conda create -n tc_generator_web python=3.11
    conda activate tc_generator_web
    pip install -r requirements.txt
```

#### 4. Executar a Aplicação
```bash
    python run.py
```