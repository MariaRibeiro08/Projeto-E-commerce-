from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from urllib.parse import quote_plus
import random

# =========================
# CONEXÃO COM O BANCO
# =========================

usuario = "root"
senha = quote_plus("dev1t@24")  # Codifica o @ corretamente
host = "localhost"
porta = "3306"
banco = "banco"  # altere se o nome for diferente

DATABASE_URL = f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# =========================
# MODELOS (TABELAS)
# =========================

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)

    produtos = relationship("Produto", back_populates="categoria")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    preco = Column(DECIMAL(10, 2), nullable=False)
    quantidade = Column(Integer, nullable=False)
    imagem = Column(String(200))
    tamanho = Column(String(50))
    cor = Column(String(50))
    descricao = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    categoria = relationship("Categoria", back_populates="produtos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    data_cadastro = Column(TIMESTAMP, server_default=func.current_timestamp())

    pedidos = relationship("Pedido", back_populates="usuario")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_pedido = Column(TIMESTAMP, server_default=func.current_timestamp())
    status = Column(String(50), default="Em andamento")
    valor_total = Column(DECIMAL(10, 2), default=0.00)

    usuario = relationship("Usuario", back_populates="pedidos")

# =========================
# CRIAÇÃO DAS TABELAS
# =========================

Base.metadata.create_all(engine)

# =========================
# INSERÇÃO DE DADOS INICIAIS
# =========================

Session = sessionmaker(bind=engine)
session = Session()

# Inserir categorias iniciais
if session.query(Categoria).count() == 0:
    categorias = ["Básica", "Esportiva", "Social", "Casual"]
    session.add_all([Categoria(nome=c) for c in categorias])
    session.commit()
    print("✅ Categorias criadas com sucesso!")

# Geração de produtos automáticos
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

# Inserir produtos automáticos
if session.query(Produto).count() == 0:
    N = 10
    produtos = [gerar_produto() for _ in range(N)]
    session.add_all(produtos)
    session.commit()
    print(f"✅ {N} produtos inseridos com sucesso!")

print("✅ Tabelas criadas e dados iniciais prontos!")
session.close()
