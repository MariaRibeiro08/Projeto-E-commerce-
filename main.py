'''
Nome: Maria Eduarda da Silva Ribeiro 
Data: 08/10/2025
RA: 24271585
'''

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from controllers.produtos_controller import router as produtos_router
from controllers.usuario_controller import router as usuario_router  # JWT
from controllers.carrinho_controller import router as carrinho_router
from database import engine, Base
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import models
from controllers.categorias_controller import router as categorias_router
from controllers.checkout_controller import router as checkout_router  
from controllers.dashboard_controller import router as dashboard_router ################

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================
DB_USER = "root"
DB_PASS = quote_plus("dev1t@24")  # codifica o @ corretamente
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "banco"

# Conexão temporária (sem banco definido) para garantir que o DB exista
try:
    temp_engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}")
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        print("✅ Banco de dados verificado/criado com sucesso.")
except Exception as e:
    print(f"❌ Erro ao verificar/criar o banco de dados: {e}")

# =========================
# CRIAÇÃO DAS TABELAS
# =========================
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas/verificadas com sucesso.")
except Exception as e:
    print(f"❌ Erro ao criar tabelas no banco: {e}")

# =========================
# CRIAÇÃO DO APP FASTAPI
# =========================
app = FastAPI(
    title="MVC Produtos - MySQL Version",
    debug=True  # Mostra o traceback completo no navegador
)

# Monta os arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui os routers
app.include_router(categorias_router)
app.include_router(produtos_router)
app.include_router(usuario_router)
app.include_router(carrinho_router)
app.include_router(checkout_router)  
app.include_router(dashboard_router) #############


# =========================
# ROTA RAIZ
# =========================
@app.get("/")
def root():
    return {"status": "Servidor rodando corretamente 🚀"}
