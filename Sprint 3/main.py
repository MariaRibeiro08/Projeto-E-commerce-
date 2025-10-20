'''
Nome: Maria Eduarda da Silva Ribeiro 
Data: 08/10/2025
RA: 24271585
'''

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from produtos_controller import router
from database import engine, Base
import models

# Cria a instância do app apenas uma vez
app = FastAPI(title="MVC Produtos - MySQL Version")

# Cria tabelas no MySQL (caso não existam)
Base.metadata.create_all(bind=engine)

# Monta os arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui o router de produtos
app.include_router(router)
