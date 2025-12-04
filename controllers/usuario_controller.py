# usuario_controller.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from auth_deps import get_usuario_atual
from database import get_db
from models import Usuario
from auth import gerar_hash_senha, verificar_senha, criar_token, verificar_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# PÁGINA DE CADASTRO (GET)
@router.get("/register", response_class=HTMLResponse)
def pagina_cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

# CADASTRO (POST)
@router.post("/register", response_class=HTMLResponse)
def cadastrar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verifica se já existe
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        return templates.TemplateResponse("cadastro.html", {"request": request, "mensagem": "E-mail já cadastrado!"})

    # Cria usuário
    senha_hash = gerar_hash_senha(senha)
    novo_usuario = Usuario(nome=nome, email=email, telefone=telefone, senha=senha_hash)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # Após cadastrar, redireciona para login
    return RedirectResponse(url="/login", status_code=303)

# PÁGINA DE LOGIN (GET)
@router.get("/login", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# LOGIN (POST)
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    # usuário não encontrado ou senha inválida -> renderiza login com mensagem
    if not usuario or not verificar_senha(senha, usuario.senha):
        return templates.TemplateResponse("login.html", {"request": request, "mensagem": "Credenciais inválidas"})

    # cria token JWT (payload com sub=email)
    token = criar_token({"sub": usuario.email})
    response = RedirectResponse(url="/home", status_code=303)
    # configura cookie com HttpOnly
    response.set_cookie(key="token", value=token, httponly=True, samesite="lax", path="/")
    return response

# HOME - renderiza home e passa 'usuario' se autenticado
@router.get("/home", response_class=HTMLResponse)
def home(request: Request, usuario: Usuario = Depends(get_usuario_atual)):
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "usuario": usuario  
    })
# LOGOUT
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    
    # Remove ambos os cookies
    response.delete_cookie("token", path="/")
    response.delete_cookie("is_admin", path="/")
    response.delete_cookie("admin_user", path="/")  # ✅ NOVO: remove admin_user
    
    return response
# Debug endpoint para verificar cookies
@router.get("/debug-cookies")
def debug_cookies(request: Request):
    token = request.cookies.get("token")
    is_admin = request.cookies.get("is_admin")
    
    return {
        "token_present": token is not None,
        "admin_cookie": is_admin,
        "all_cookies": dict(request.cookies)
    }


