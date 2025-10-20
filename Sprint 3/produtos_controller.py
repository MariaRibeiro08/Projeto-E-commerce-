from fastapi import (
    APIRouter, Request, Form, UploadFile, File,
    Depends, HTTPException, Cookie
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Produto
import os, shutil, uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------- FUNÇÕES AUXILIARES ----------------- #
async def salvar_imagem(imagem: UploadFile) -> str:
    if not imagem or imagem.filename == "":
        return ""
    nome_unico = f"{uuid.uuid4()}_{imagem.filename}"
    caminho = os.path.join(UPLOAD_DIR, nome_unico)
    with open(caminho, "wb") as arquivo:
        shutil.copyfileobj(imagem.file, arquivo)
    return nome_unico


async def criar_produto(nome: str, preco: float, quantidade: int, imagem: UploadFile, db: Session):
    nome_imagem = await salvar_imagem(imagem)
    novo = Produto(nome=nome, preco=preco, quantidade=quantidade, imagem=nome_imagem)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


async def atualizar_produto(id: int, nome: str, preco: float, quantidade: int, imagem: UploadFile, db: Session):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        return None

    produto.nome = nome
    produto.preco = preco
    produto.quantidade = quantidade

    if imagem and imagem.filename != "":
        if produto.imagem:
            try:
                os.remove(os.path.join(UPLOAD_DIR, produto.imagem))
            except FileNotFoundError:
                pass
        produto.imagem = await salvar_imagem(imagem)

    db.commit()
    db.refresh(produto)
    return produto


async def deletar_produto(id: int, db: Session):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if produto:
        if produto.imagem:
            try:
                os.remove(os.path.join(UPLOAD_DIR, produto.imagem))
            except FileNotFoundError:
                pass
        db.delete(produto)
        db.commit()
    return produto


# ----------------- ADMIN COOKIE ----------------- #
def admin_cookie_required(is_admin: str = Cookie(default="false")):
    if is_admin != "true":
        raise HTTPException(status_code=403, detail="Acesso negado")


# ----------------- ROTAS PÚBLICAS ----------------- #
@router.get("/", response_class=HTMLResponse)
async def listar(request: Request, db: Session = Depends(get_db), is_admin: str = Cookie(default="false")):
    produtos = db.query(Produto).all()
    mostrar_admin = (is_admin == "true")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "produtos": produtos, "is_admin": mostrar_admin}
    )


@router.get("/produtos/{id_produto}", response_class=HTMLResponse)
async def detalhe(request: Request, id_produto: int, db: Session = Depends(get_db), is_admin: str = Cookie(default="false")):
    produto = db.query(Produto).filter(Produto.id == id_produto).first()
    mostrar_admin = (is_admin == "true")
    return templates.TemplateResponse(
        "produto.html",
        {"request": request, "produto": produto, "is_admin": mostrar_admin}
    )


# ----------------- LISTA ADMIN ----------------- #
@router.get("/lista_adm", response_class=HTMLResponse, dependencies=[Depends(admin_cookie_required)])
async def lista_admin(request: Request, db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return templates.TemplateResponse(
        "lista_adm.html",
        {"request": request, "produtos": produtos}
    )


# ----------------- LOGIN ADMIN ----------------- #
@router.get("/login_adm", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login_adm.html", {"request": request})


@router.post("/login_adm")
async def login_adm(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "1234":
        response = RedirectResponse("/lista_adm", status_code=303)
        response.set_cookie(key="is_admin", value="true")
        return response
    return templates.TemplateResponse("login_adm.html", {"request": request, "error": "Credenciais incorretas"})


# ----------------- LOGOUT ----------------- #
@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("is_admin")
    return response


# ----------------- ROTAS ADMIN ----------------- #
@router.get("/novo", response_class=HTMLResponse, dependencies=[Depends(admin_cookie_required)])
async def form_novo(request: Request):
    return templates.TemplateResponse("novo.html", {"request": request})


@router.post("/novo", dependencies=[Depends(admin_cookie_required)])
async def criar(
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    await criar_produto(nome, preco, quantidade, imagem, db)
    return RedirectResponse("/lista_adm", status_code=303)


@router.get("/editar/{id}", response_class=HTMLResponse, dependencies=[Depends(admin_cookie_required)])
async def form_editar(id: int, request: Request, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    return templates.TemplateResponse("editar.html", {"request": request, "produto": produto})


@router.post("/editar/{id}", dependencies=[Depends(admin_cookie_required)])
async def editar(
    id: int,
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    await atualizar_produto(id, nome, preco, quantidade, imagem, db)
    return RedirectResponse("/lista_adm", status_code=303)


@router.get("/deletar/{id}", dependencies=[Depends(admin_cookie_required)])
async def deletar(id: int, db: Session = Depends(get_db)):
    await deletar_produto(id, db)
    return RedirectResponse("/lista_adm", status_code=303)

# ----------------- ROTAS PÚBLICAS SIMPLES ----------------- #
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/carrinho", response_class=HTMLResponse)
async def mostrar_carrinho(request: Request):
    """
    Renderiza a página do carrinho vazio ou com produtos.
    """
    return templates.TemplateResponse(
        "carrinho.html",
        {"request": request, "produtos": [], "total_itens": 0}
    )

@router.get("/cadastro", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@router.get("/sobre", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request})

@router.get("/fale_conosco", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("fale_conosco.html", {"request": request})

@router.get("/busca", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("busca.html", {"request": request})