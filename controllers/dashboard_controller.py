# dashboard_controller.py
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth_deps import get_usuario_atual, login_required
from models import Usuario, Pedido, ItemPedido, Produto
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# =========================
# DASHBOARD DO USUÁRIO
# =========================
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_usuario(
    request: Request,
    usuario: Usuario = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Página principal do dashboard do usuário
    """
    # Buscar pedidos do usuário
    pedidos = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id
    ).order_by(Pedido.data_pedido.desc()).all()
    
    # Formatar dados dos pedidos
    pedidos_formatados = []
    for pedido in pedidos:
        itens_pedido = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
        
        # Buscar detalhes dos produtos
        itens_detalhados = []
        for item in itens_pedido:
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if produto:
                itens_detalhados.append({
                    'nome': produto.nome,
                    'quantidade': item.quantidade,
                    'preco_unitario': float(produto.preco),
                    'subtotal': float(item.subtotal),
                    'imagem': produto.imagem or 'static/default.png'
                })
        
        pedidos_formatados.append({
            'id': pedido.id,
            'data_pedido': pedido.data_pedido.strftime('%d/%m/%Y %H:%M'),
            'status': pedido.status,
            'valor_total': float(pedido.valor_total),
            'endereco_entrega': pedido.endereco_entrega,
            'itens': itens_detalhados
        })
    
    # Estatísticas do usuário
    total_pedidos = len(pedidos)
    pedidos_ativos = len([p for p in pedidos if p.status in ['Em andamento', 'Processando']])
    total_gasto = sum(float(p.valor_total) for p in pedidos)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuario": usuario,
        "pedidos": pedidos_formatados,
        "estatisticas": {
            "total_pedidos": total_pedidos,
            "pedidos_ativos": pedidos_ativos,
            "total_gasto": total_gasto
        }
    })

# =========================
# DETALHES DO PEDIDO
# =========================
@router.get("/dashboard/pedido/{pedido_id}", response_class=HTMLResponse)
async def detalhes_pedido(
    request: Request,
    pedido_id: int,
    usuario: Usuario = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Página de detalhes de um pedido específico
    """
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id,
        Pedido.usuario_id == usuario.id
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Buscar itens do pedido com detalhes dos produtos
    itens_pedido = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
    
    itens_detalhados = []
    for item in itens_pedido:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if produto:
            itens_detalhados.append({
                'id': item.id,
                'produto_id': produto.id,
                'nome': produto.nome,
                'quantidade': item.quantidade,
                'preco_unitario': float(produto.preco),
                'subtotal': float(item.subtotal),
                'imagem': produto.imagem or 'static/default.png',
                'cor': produto.cor,
                'tamanho': produto.tamanho
            })
    
    return templates.TemplateResponse("detalhes_pedido.html", {
        "request": request,
        "usuario": usuario,
        "pedido": {
            'id': pedido.id,
            'data_pedido': pedido.data_pedido.strftime('%d/%m/%Y às %H:%M'),
            'status': pedido.status,
            'valor_total': float(pedido.valor_total),
            'endereco_entrega': pedido.endereco_entrega
        },
        "itens": itens_detalhados
    })

# =========================
# PERFIL DO USUÁRIO
# =========================
@router.get("/dashboard/perfil", response_class=HTMLResponse)
async def perfil_usuario(
    request: Request,
    usuario: Usuario = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Página de perfil do usuário
    """
    return templates.TemplateResponse("perfil_usuario.html", {
        "request": request,
        "usuario": usuario
    })

@router.post("/dashboard/perfil/atualizar")
async def atualizar_perfil(
    request: Request,
    nome: str = Form(...),
    telefone: str = Form(...),
    usuario: Usuario = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados do perfil do usuário
    """
    usuario.nome = nome
    usuario.telefone = telefone
    db.commit()
    
    return RedirectResponse("/dashboard/perfil?sucesso=true", status_code=303)

# =========================
# HISTÓRICO DE PEDIDOS
# =========================
@router.get("/dashboard/pedidos", response_class=HTMLResponse)
async def historico_pedidos(
    request: Request,
    usuario: Usuario = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Página com histórico completo de pedidos
    """
    pedidos = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id
    ).order_by(Pedido.data_pedido.desc()).all()
    
    pedidos_formatados = []
    for pedido in pedidos:
        itens_count = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).count()
        
        pedidos_formatados.append({
            'id': pedido.id,
            'data_pedido': pedido.data_pedido.strftime('%d/%m/%Y'),
            'status': pedido.status,
            'valor_total': float(pedido.valor_total),
            'quantidade_itens': itens_count
        })
    
    return templates.TemplateResponse("historico_pedidos.html", {
        "request": request,
        "usuario": usuario,
        "pedidos": pedidos_formatados
    })

# =========================
# CANCELAR PEDIDO
# =========================
@router.post("/dashboard/pedido/{pedido_id}/cancelar")
async def cancelar_pedido(
    pedido_id: int,
    usuario: Usuario = Depends(login_required),
    db: Session = Depends(get_db)
):
    """
    Cancela um pedido (apenas se estiver em andamento)
    """
    pedido = db.query(Pedido).filter(
        Pedido.id == pedido_id,
        Pedido.usuario_id == usuario.id,
        Pedido.status.in_(['Em andamento', 'Processando'])
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado ou não pode ser cancelado")
    
    # Restaurar estoque dos produtos
    itens_pedido = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
    for item in itens_pedido:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if produto:
            produto.quantidade += item.quantidade
    
    # Cancelar pedido
    pedido.status = "Cancelado"
    db.commit()
    
    return RedirectResponse("/dashboard/pedidos?cancelado=true", status_code=303)