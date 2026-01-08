#!/usr/bin/env python3
"""
Script para inicializar o banco de dados PostgreSQL.

Este script lê as configurações do arquivo .env e executa o script SQL
para criar e popular o banco de dados.
"""
import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

def load_environment():
    """Carrega as variáveis de ambiente do arquivo .env."""
    load_dotenv()
    
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME',
        'DB_USER', 'DB_PASSWORD'
    ]
    
    config = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"Erro: Variável de ambiente {var} não encontrada no arquivo .env")
            sys.exit(1)
        config[var.lower()] = value
    
    return config

def execute_sql_file(cursor, file_path):
    """Executa um arquivo SQL no banco de dados."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        # Executa os comandos SQL
        cursor.execute(sql_commands)
        print(f"Script SQL executado com sucesso: {file_path}")
        return True
    except Exception as e:
        print(f"Erro ao executar o script SQL {file_path}: {e}")
        return False

def main():
    """Função principal."""
    print("Iniciando a inicialização do banco de dados...")
    
    # Carrega as configurações do ambiente
    config = load_environment()
    
    # Conecta ao PostgreSQL (sem especificar o banco de dados)
    conn_params = {
        'host': config['db_host'],
        'port': config['db_port'],
        'user': config['db_user'],
        'password': config['db_password'],
        'dbname': 'postgres'  # Conecta ao banco padrão 'postgres'
    }
    
    try:
        # Conecta ao PostgreSQL
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verifica se o banco de dados já existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config['db_name'],))
        if not cursor.fetchone():
            # Cria o banco de dados se não existir
            print(f"Criando o banco de dados {config['db_name']}...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(config['db_name']))
            )
            print(f"Banco de dados {config['db_name']} criado com sucesso!")
        else:
            print(f"O banco de dados {config['db_name']} já existe.")
        
        # Fecha a conexão com o banco 'postgres'
        cursor.close()
        conn.close()
        
        # Conecta ao banco de dados recém-criado
        conn_params['dbname'] = config['db_name']
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Executa o script SQL
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_file):
            print(f"Executando o script de schema: {schema_file}")
            if execute_sql_file(cursor, schema_file):
                print("Banco de dados inicializado com sucesso!")
            else:
                print("Erro ao executar o script de schema.")
                sys.exit(1)
        else:
            print(f"Arquivo de schema não encontrado: {schema_file}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

if __name__ == "__main__":
    main()
