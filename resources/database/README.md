# Configuração do Banco de Dados

Este diretório contém os scripts e configurações para o banco de dados PostgreSQL do TC Generator.

## Estrutura do Banco de Dados

O banco de dados contém as seguintes tabelas principais:

- `satellites`: Armazena informações sobre os satélites
- `operators`: Armazena informações sobre os operadores do sistema
- `telecommands`: Armazena os comandos enviados para os satélites
- `execution_logs`: Armazena logs de execução dos comandos

## Configuração

1. Certifique-se de que o PostgreSQL está instalado e em execução
2. Configure as variáveis de ambiente no arquivo `.env` na raiz do projeto:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=tc_generator
   DB_USER=root
   DB_PASSWORD=root
   ```

## Inicialização do Banco de Dados

Para criar e popular o banco de dados, execute o seguinte comando:

```bash
# Torna o script executável (apenas na primeira vez)
chmod +x database/script_init_db.py

# Executa o script de inicialização
python database/script_init_db.py
```

## Acessando o Banco de Dados

### Usando psql (linha de comando)

```bash
psql -h localhost -U root -d tc_generator
```

### Usando Python

```python
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

# Exemplo de consulta
with conn.cursor() as cur:
    cur.execute("SELECT * FROM satellites")
    for row in cur.fetchall():
        print(row)

conn.close()
```

## Visualizações Úteis

O banco de dados inclui as seguintes visualizações:

- `vw_recent_telecommands`: Mostra os comandos recentes com informações de satélite e operador

## Funções Úteis

- `get_satellite_command_stats(days_interval)`: Retorna estatísticas de comandos por satélite

## Migrações

Para fazer alterações no esquema do banco de dados, siga estes passos:

1. Crie um novo arquivo de migração em `database/migrations/` com o formato `YYYYMMDD_nome_da_migracao.sql`
2. Adicione os comandos SQL necessários para a migração
3. Atualize o esquema principal (`schema.sql`) com as alterações

## Backup e Restauração

### Backup

```bash
pg_dump -h localhost -U root -d tc_generator > backup_$(date +%Y%m%d).sql
```

### Restauração

```bash
psql -h localhost -U root -d tc_generator < backup_20231119.sql
```

## Solução de Problemas

- **Erro de conexão**: Verifique se o PostgreSQL está em execução e se as credenciais no `.env` estão corretas
- **Permissões negadas**: Certifique-se de que o usuário do banco de dados tem as permissões necessárias
- **Erro de chave estrangeira**: Verifique se os dados estão sendo inseridos na ordem correta (tabelas referenciadas primeiro)
