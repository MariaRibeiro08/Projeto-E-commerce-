
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from auth import verificar_token

def get_usuario_atual(request: Request, db: Session = Depends(get_db)):
    """
    Dependency para obter o usuário atual baseado no token JWT
    Retorna None se não estiver autenticado (em vez de erro)
    """
    token = request.cookies.get("token")
    
    if not token:
        return None
    
    try:
        payload = verificar_token(token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        return usuario
    
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return None

def login_required(request: Request, db: Session = Depends(get_db)):
    """
    Dependency que redireciona para login se não estiver autenticado
    """
    usuario = get_usuario_atual(request, db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return usuario

# ✅ NOVO: Função para verificar se é admin
def admin_required(request: Request, db: Session = Depends(get_db)):
    """
    Dependency que verifica se o usuário é admin
    """
    usuario = get_usuario_atual(request, db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    
    # Verifica se está na lista de admins (precisa ser implementado)
    # Por enquanto usa o sistema de cookies existente
    is_admin = request.cookies.get("is_admin") == "true"
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    return usuario