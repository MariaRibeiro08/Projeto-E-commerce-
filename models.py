# models.py
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Text, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    produtos = relationship("Produto", back_populates="categoria")

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)
    imagem = Column(String(200), nullable=True)
    tamanho = Column(String(50))
    cor = Column(String(50))
    descricao = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    categoria = relationship("Categoria", back_populates="produtos")
    variacoes = relationship("VariacaoProduto", back_populates="produto")

    itens = relationship("ItemPedido", back_populates="produto")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    telefone = Column(String(20))
    pedidos = relationship("Pedido", back_populates="usuario")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_pedido = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Em andamento")
    valor_total = Column(DECIMAL(10, 2), default=0.00)
    endereco_entrega = Column(String(255))
    usuario = relationship("Usuario", back_populates="pedidos")
    itens = relationship("ItemPedido", back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    pedido = relationship("Pedido", back_populates="itens")
    
    produto = relationship("Produto", back_populates="itens")

class VariacaoProduto(Base):
    __tablename__ = "variacoes_produto"
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    cor = Column(String(50), nullable=False)
    tamanho = Column(String(10), nullable=False)
    quantidade = Column(Integer, nullable=False)
    imagem = Column(String(200), nullable=True)
    produto = relationship("Produto")