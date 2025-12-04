from sqlalchemy.orm import sessionmaker
from database import engine
from models import Base, Categoria, Produto
import random

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Cria categorias iniciais
if session.query(Categoria).count() == 0:
    categorias = ["Básica", "Esportiva", "Social", "Casual"]
    session.add_all([Categoria(nome=c) for c in categorias])
    session.commit()
    print("Categorias criadas com sucesso!")

# Gera produtos fakes automáticos
cores = ["BRANCA", "PRETA", "CINZA", "AZUL", "ROSA", "VERMELHA", "VERDE", "BEGE", "LILÁS", "CHUMBO"]
tamanhos = ["PP", "P", "M", "G", "GG"]

def gerar_produto():
    nome_tipo = random.choice(["Básica", "Esportiva", "Social", "Casual"])
    nome = f"Camiseta {nome_tipo}"
    cor = random.choice(cores)
    tamanho = random.choice(tamanhos)
    preco = round(random.uniform(39.90, 249.90), 2)
    quantidade = random.randint(1, 50)
    descricao = f"Camiseta {cor.lower()} tamanho {tamanho}"
    categoria_id = random.randint(1, 4)
    return Produto(
        nome=nome,
        preco=preco,
        quantidade=quantidade,
        imagem=None,
        tamanho=tamanho,
        cor=cor,
        descricao=descricao,
        categoria_id=categoria_id
    )

# Insere produtos se tabela estiver vazia
if session.query(Produto).count() == 0:
    N = 10
    produtos = [gerar_produto() for _ in range(N)]
    session.add_all(produtos)
    session.commit()
    print(f"{N} produtos inseridos com sucesso!")

print("Banco inicializado com sucesso!")
session.close()
