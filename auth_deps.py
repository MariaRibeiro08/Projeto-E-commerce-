# auth_deps.py
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from auth import verificar_token

def get_usuario_atual(request: Request, db: Session = Depends(get_db)):
    """
    Dependency para obter o usuário atual baseado no token JWT
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
    
    except Exception:
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