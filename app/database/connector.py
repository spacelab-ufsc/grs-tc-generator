from sqlalchemy import create_engine, text
# The typical form of a database URL
# dialect+driver://username:password@host:port/database
engine = create_engine("postgresql+psycopg2://root:root@localhost:5432/tc_generator")
conn = engine.connect()



if __name__ == "__main__":
    response = conn.execute(text("SELECT * FROM operators"))
    for row in response:
        print(row)
        print(row.username)
        print(row.email)

    print("Database connection successful")
    conn.close()