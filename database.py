from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

# =========================
# CONFIGURAÇÃO DO BANCO (MySQL)
# =========================
DB_USER = "root"
DB_PASS = quote_plus("dev1t@24")  # codifica o @ corretamente
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "banco"

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# =========================
# ENGINE E SESSÃO
# =========================
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =========================
# DEPENDÊNCIA PARA USO NAS ROTAS FASTAPI
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
