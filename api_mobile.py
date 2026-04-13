from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Produto, Categoria, Usuario
from auth_deps import get_usuario_atual
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/mobile", tags=["Mobile API"])

# Modelos de resposta
class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: float
    descricao: Optional[str] = None
    imagem: Optional[str] = None
    cor: Optional[str] = None
    tamanho: Optional[str] = None
    categoria_id: Optional[int] = None
    categoria_nome: Optional[str] = None

class CategoriaResponse(BaseModel):
    id: int
    nome: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    senha: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    usuario: Optional[UsuarioResponse] = None
    message: str

# ✅ ENDPOINT: Listar produtos (JSON)
@router.get("/produtos", response_model=List[ProdutoResponse])
def listar_produtos_mobile(
    db: Session = Depends(get_db),
    categoria_id: Optional[int] = None
):
    """Retorna lista de produtos em JSON"""
    query = db.query(Produto)
    
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    
    produtos = query.all()
    
    resultado = []
    for p in produtos:
        resultado.append(ProdutoResponse(
            id=p.id,
            nome=p.nome,
            preco=float(p.preco),
            descricao=p.descricao,
            imagem=f"/static/uploads/{p.imagem}" if p.imagem else None,
            cor=p.cor,
            tamanho=p.tamanho,
            categoria_id=p.categoria_id,
            categoria_nome=p.categoria.nome if p.categoria else None
        ))
    
    return resultado

# ✅ ENDPOINT: Detalhes de um produto
@router.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def detalhe_produto_mobile(produto_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de um produto em JSON"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return ProdutoResponse(
        id=produto.id,
        nome=produto.nome,
        preco=float(produto.preco),
        descricao=produto.descricao,
        imagem=f"/static/uploads/{produto.imagem}" if produto.imagem else None,
        cor=produto.cor,
        tamanho=produto.tamanho,
        categoria_id=produto.categoria_id,
        categoria_nome=produto.categoria.nome if produto.categoria else None
    )

# ✅ ENDPOINT: Listar categorias
@router.get("/categorias", response_model=List[CategoriaResponse])
def listar_categorias_mobile(db: Session = Depends(get_db)):
    """Retorna lista de categorias em JSON"""
    categorias = db.query(Categoria).all()
    return [CategoriaResponse(id=c.id, nome=c.nome) for c in categorias]

# ✅ ENDPOINT: Login (retorna JSON)
@router.post("/login", response_model=LoginResponse)
def login_mobile(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login que retorna token em JSON (não usa cookie)"""
    from auth import verificar_senha, criar_token
    
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    
    if not usuario or not verificar_senha(dados.senha, usuario.senha):
        return LoginResponse(
            success=False,
            message="Credenciais inválidas"
        )
    
    # Criar token JWT
    token = criar_token({"sub": usuario.email})
    
    return LoginResponse(
        success=True,
        token=token,
        usuario=UsuarioResponse(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            telefone=usuario.telefone
        ),
        message="Login realizado com sucesso"
    )

# ✅ ENDPOINT: Verificar token
@router.get("/verificar-token")
def verificar_token_mobile(
    usuario: Usuario = Depends(get_usuario_atual)
):
    """Verifica se o token é válido"""
    if not usuario:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        }
    }

# ✅ ENDPOINT: Carrinho - listar itens
@router.get("/carrinho")
def get_carrinho(
    usuario: Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """Retorna os itens do carrinho do usuário"""
    if not usuario:
        return {"itens": [], "total": 0, "autenticado": False}
    
    from models import Pedido, ItemPedido
    
    pedido = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id,
        Pedido.status == "Em andamento"
    ).first()
    
    itens = []
    total = 0
    
    if pedido:
        itens_db = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
        for item in itens_db:
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if produto:
                itens.append({
                    "id": item.id,
                    "produto_id": produto.id,
                    "nome": produto.nome,
                    "preco": float(produto.preco),
                    "quantidade": item.quantidade,
                    "subtotal": float(item.subtotal),
                    "imagem": f"/static/uploads/{produto.imagem}" if produto.imagem else None
                })
                total += float(item.subtotal)
    
    return {
        "itens": itens,
        "total": total,
        "total_itens": sum(i["quantidade"] for i in itens),
        "autenticado": True
    }

# ✅ ENDPOINT: Adicionar ao carrinho
@router.post("/carrinho/adicionar")
def adicionar_carrinho(
    dados: dict,
    usuario: Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """Adiciona item ao carrinho"""
    from models import Pedido, ItemPedido
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade", 1)
    
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Busca ou cria pedido em andamento
    pedido = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id,
        Pedido.status == "Em andamento"
    ).first()
    
    if not pedido:
        pedido = Pedido(usuario_id=usuario.id, status="Em andamento", valor_total=0)
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
    
    # Verifica se item já existe
    item = db.query(ItemPedido).filter(
        ItemPedido.pedido_id == pedido.id,
        ItemPedido.produto_id == produto_id
    ).first()
    
    subtotal = float(produto.preco) * quantidade
    
    if item:
        item.quantidade += quantidade
        item.subtotal += subtotal
    else:
        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto_id,
            quantidade=quantidade,
            subtotal=subtotal
        )
        db.add(item)
    
    # Atualiza total do pedido
    itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
    total = sum(float(i.subtotal) for i in itens)
    pedido.valor_total = total
    
    db.commit()
    
    return {"success": True, "message": "Item adicionado ao carrinho"}