'''
Nome: Thiago Albuquerque
Data: 05/10/2025
RA: 24271684
'''

from sqlalchemy import Column, Integer, String, Float
from database import Base

class Produto(Base):
    __tablename__ = "produtos"   # nome da tabela no banco

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)
    imagem = Column(String(200), nullable=True)

