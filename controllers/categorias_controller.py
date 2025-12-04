# categorias_controller.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Categoria

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Página para criar categoria
@router.get("/categorias/nova", response_class=HTMLResponse)
def form_nova_categoria(request: Request):
    return templates.TemplateResponse("nova_categoria.html", {"request": request})

# Criar categoria
@router.post("/categorias/nova")
def criar_categoria(
    request: Request,
    nome: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verifica se já existe
    categoria_existente = db.query(Categoria).filter(Categoria.nome == nome).first()
    if categoria_existente:
        return templates.TemplateResponse("nova_categoria.html", {
            "request": request,
            "erro": "Categoria já existe!"
        })
    
    nova_categoria = Categoria(nome=nome)
    db.add(nova_categoria)
    db.commit()
    
    return RedirectResponse(url="/novo", status_code=303)

# API para buscar categorias (usada no select)
@router.get("/api/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return JSONResponse([{"id": c.id, "nome": c.nome} for c in categorias])