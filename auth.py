# auth.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = "chave-secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Hash de senha
def gerar_hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)

# Criar token JWT
def criar_token(dados: dict):
    dados_token = dados.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    dados_token.update({"exp": expira})
    token_jwt = jwt.encode(dados_token, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

# Verificar token JWT
def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
