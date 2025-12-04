from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal
import models
from database import get_db

router = APIRouter(prefix="/checkout", tags=["Checkout e Pedidos"])

# ============================================================
# MODELOS DE REQUISIÇÃO E RESPOSTA
# ============================================================

class IdentificacaoRequest(BaseModel):
    email: EmailStr
    nome: Optional[str] = None
    telefone: Optional[str] = None

class CarrinhoItem(BaseModel):
    produto_id: int
    quantidade: int

class CheckoutRequest(BaseModel):
    usuario_id: int
    endereco_entrega: str
    itens: List[CarrinhoItem]

class ItemPedidoResponse(BaseModel):
    produto: str
    quantidade: int
    subtotal: Decimal

class PedidoResponse(BaseModel):
    id: int
    data_pedido: str
    status: str
    valor_total: Decimal
    endereco_entrega: str
    itens: List[ItemPedidoResponse]

# ============================================================
# ROTA 1 - IDENTIFICAÇÃO DO USUÁRIO
# ============================================================
@router.post("/identificacao")
def identificacao_usuario(dados: IdentificacaoRequest, db: Session = Depends(get_db)):
    """Verifica se o usuário existe; se não, cria um novo."""
    usuario = db.query(models.Usuario).filter(models.Usuario.email == dados.email).first()
    if not usuario:
        novo = models.Usuario(
            nome=dados.nome or dados.email.split("@")[0],
            email=dados.email,
            telefone=dados.telefone or "",
            senha="default"
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        usuario = novo

    return {
        "mensagem": "Usuário identificado com sucesso",
        "usuario_id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    }

# ============================================================
# ROTA 2 - FINALIZAR CHECKOUT
# ============================================================
@router.post("/finalizar", response_model=PedidoResponse)
def finalizar_pedido(dados: CheckoutRequest, db: Session = Depends(get_db)):
    """Cria o pedido real no banco com os itens do carrinho."""
    usuario = db.query(models.Usuario).get(dados.usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not dados.itens:
        raise HTTPException(status_code=400, detail="Carrinho vazio")

    # Cria o pedido no banco
    novo_pedido = models.Pedido(
        usuario_id=usuario.id,
        endereco_entrega=dados.endereco_entrega,
        status="Em andamento",
        valor_total=Decimal("0.00")
    )
    db.add(novo_pedido)
    db.flush()

    total = Decimal("0.00")
    itens_resposta = []

    for item in dados.itens:
        produto = db.query(models.Produto).get(item.produto_id)
        if not produto:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")

        subtotal = Decimal(str(produto.preco)) * item.quantidade
        total += subtotal

        novo_item = models.ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=produto.id,
            quantidade=item.quantidade,
            subtotal=subtotal
        )
        db.add(novo_item)

        itens_resposta.append(ItemPedidoResponse(
            produto=produto.nome,
            quantidade=item.quantidade,
            subtotal=subtotal
        ))

    novo_pedido.valor_total = total
    db.commit()
    db.refresh(novo_pedido)

    return PedidoResponse(
        id=novo_pedido.id,
        data_pedido=str(novo_pedido.data_pedido),
        status=novo_pedido.status,
        valor_total=novo_pedido.valor_total,
        endereco_entrega=novo_pedido.endereco_entrega,
        itens=itens_resposta
    )

# ============================================================
# ROTA 3 - HISTÓRICO DE PEDIDOS
# ============================================================
@router.get("/historico/{usuario_id}", response_model=List[PedidoResponse])
def historico_pedidos(usuario_id: int, db: Session = Depends(get_db)):
    """Retorna o histórico de pedidos de um usuário."""
    pedidos = db.query(models.Pedido).filter(models.Pedido.usuario_id == usuario_id).all()
    if not pedidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido encontrado para este usuário")

    resposta = []
    for pedido in pedidos:
        itens_resposta = [
            ItemPedidoResponse(
                produto=db.query(models.Produto).get(item.produto_id).nome if item.produto_id else "Produto removido",
                quantidade=item.quantidade,
                subtotal=item.subtotal
            )
            for item in pedido.itens
        ]
        resposta.append(PedidoResponse(
            id=pedido.id,
            data_pedido=str(pedido.data_pedido),
            status=pedido.status,
            valor_total=pedido.valor_total,
            endereco_entrega=pedido.endereco_entrega,
            itens=itens_resposta
        ))
    return resposta
