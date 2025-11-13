import mysql.connector
import random

# Configurações de conexão
config = {
    "host": "localhost",
    "user": "root",
    "password": "dev1t@24",
    "port": 3306,
    "database": "banco",
}

# Conexão inicial
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Criar banco se não existir
cursor.execute("CREATE DATABASE IF NOT EXISTS banco")
cursor.execute("USE banco")

# Criar tabela categorias
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
)
""")

# Inserir categorias se ainda não existirem
cursor.execute("SELECT COUNT(*) FROM categorias")
if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO categorias (nome) VALUES (%s)",
        [("Básica",), ("Esportiva",), ("Social",), ("Casual",)]
    )
    conn.commit()

# Criar tabela produtos com chave estrangeira
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tamanho VARCHAR(10),
    cor VARCHAR(50),
    preco DECIMAL(10,2),
    categoria_id INT,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
)
""")
conn.commit()

# Dados para gerar produtos
cores = ["BRANCA", "PRETA", "CINZA", "AZUL", "ROSA", "VERMELHA",
        "VERDE", "BEGE", "LILÁS", "CHUMBO"]
tamanhos = ["PP", "P", "M", "G", "GG"]

def gerar_produto():
    cor = random.choice(cores)
    tamanho = random.choice(tamanhos)
    preco = round(random.uniform(39.90, 249.90), 2)
    categoria_id = random.randint(1, 4)  # entre as 4 categorias criadas
    return (tamanho, cor, preco, categoria_id)

# Inserir produtos
N = 100
produtos = [gerar_produto() for _ in range(N)]

sql = "INSERT INTO produtos (tamanho, cor, preco, categoria_id) VALUES (%s, %s, %s, %s)"
cursor.executemany(sql, produtos)
conn.commit()

print(f"{len(produtos)} produtos inseridos com sucesso!")

cursor.close()
conn.close()
