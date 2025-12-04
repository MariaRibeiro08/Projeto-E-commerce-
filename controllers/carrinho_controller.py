from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from auth_deps import get_usuario_atual
from models import Usuario, Produto, Pedido, ItemPedido
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/carrinho", tags=["Carrinho"])
templates = Jinja2Templates(directory="templates")

# Rota para visualizar o carrinho (HTML)
@router.get("/", response_class=HTMLResponse)
async def ver_carrinho(
    request: Request, 
    usuario: Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Exibe a página do carrinho com os itens do usuário
    """
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)

    pedido = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id, 
        Pedido.status == "Em andamento"
    ).first()

    itens_carrinho = []
    total_geral = 0.0

    if pedido:
        itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
        for item in itens:
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if produto:
                itens_carrinho.append({
                    "id": item.id,
                    "produto_id": produto.id,
                    "nome": produto.nome,
                    "preco": float(produto.preco),
                    "quantidade": item.quantidade,
                    "subtotal": float(item.subtotal),
                    "imagem": produto.imagem or "static/default.png"
                })
                total_geral += float(item.subtotal)

    return templates.TemplateResponse(
        "carrinho.html",
        {
            "request": request,
            "itens_carrinho": itens_carrinho,
            "total_geral": total_geral,
            "usuario": usuario
        }
    )

@router.post("/adicionar")
async def adicionar_ao_carrinho(
    request: Request,
    produto_id: int = Form(None),
    quantidade: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Adiciona um produto ao carrinho do usuário logado.
    Aceita tanto Form quanto JSON.
    """
    # Caso venha como JSON
    if produto_id is None:
        try:
            data = await request.json()
            produto_id = data.get("produto_id")
            quantidade = data.get("quantidade", 1)
        except Exception:
            raise HTTPException(status_code=400, detail="Dados inválidos")

    usuario = get_usuario_atual(request, db)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    # Validações
    if not produto_id:
        raise HTTPException(status_code=400, detail="ID do produto é obrigatório")
    
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verifica estoque
    if produto.quantidade < quantidade:
        raise HTTPException(
            status_code=400, 
            detail=f"Estoque insuficiente. Disponível: {produto.quantidade}"
        )

    # Busca ou cria pedido em andamento
    pedido = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id, 
        Pedido.status == "Em andamento"
    ).first()
    
    if not pedido:
        pedido = Pedido(
            usuario_id=usuario.id, 
            status="Em andamento", 
            valor_total=0.00
        )
        db.add(pedido)
        db.commit()
        db.refresh(pedido)

    # Busca item existente ou cria novo
    item = db.query(ItemPedido).filter(
        ItemPedido.pedido_id == pedido.id, 
        ItemPedido.produto_id == produto.id
    ).first()
    
    subtotal = float(produto.preco) * int(quantidade)
    
    if item:
        nova_quantidade = item.quantidade + int(quantidade)
        
        # Verifica estoque novamente com a quantidade total
        if produto.quantidade < nova_quantidade:
            raise HTTPException(
                status_code=400, 
                detail=f"Estoque insuficiente para adicionar mais itens. Disponível: {produto.quantidade}"
            )
            
        item.quantidade = nova_quantidade
        item.subtotal = float(item.subtotal) + subtotal
    else:
        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=int(quantidade),
            subtotal=subtotal
        )
        db.add(item)

    db.commit()

    # Atualiza valor total do pedido
    itens_pedido = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
    total = sum(float(it.subtotal) for it in itens_pedido)
    pedido.valor_total = total
    db.commit()

    return JSONResponse({
        "mensagem": "Item adicionado ao carrinho com sucesso",
        "pedido_id": pedido.id,
        "valor_total": float(pedido.valor_total),
        "quantidade_total": sum(it.quantidade for it in itens_pedido)
    })


@router.post("/finalizar")
async def finalizar_pedido(
    request: Request,
    endereco: str = Form(None),
    frete: float = Form(0.00),  # ✅ NOVO: parâmetro para frete
    cep_entrega: str = Form(None),  # ✅ NOVO: CEP de entrega
    db: Session = Depends(get_db)
):
    """
    Finaliza o pedido atual do usuário logado.
    Aceita tanto Form quanto JSON.
    """
    # Caso venha como JSON
    if endereco is None:
        try:
            data = await request.json()
            endereco = data.get("endereco", "")
            frete = data.get("frete", 0.00)  # ✅ NOVO: obtém frete do JSON
            cep_entrega = data.get("cep_entrega", "")  # ✅ NOVO: obtém CEP
        except Exception:
            endereco = ""
            frete = 0.00
            cep_entrega = ""

    usuario = get_usuario_atual(request, db)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    pedido = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id, 
        Pedido.status == "Em andamento"
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Nenhum pedido em andamento")

    # Verifica se há itens no carrinho
    itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
    if not itens:
        raise HTTPException(status_code=400, detail="Carrinho vazio")

    # Atualiza estoque dos produtos
    for item in itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if produto:
            if produto.quantidade < item.quantidade:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Estoque insuficiente para {produto.nome}"
                )
            produto.quantidade -= item.quantidade

    # ✅ ATUALIZA O PEDIDO COM FRETE E CEP
    pedido.endereco_entrega = endereco
    pedido.valor_frete = frete  # ✅ SALVA O VALOR DO FRETE
    pedido.cep_entrega = cep_entrega  # ✅ SALVA O CEP
    pedido.status = "Finalizado"
    db.commit()

    return JSONResponse({
        "mensagem": "Pedido finalizado com sucesso",
        "pedido_id": pedido.id,
        "valor_total": float(pedido.valor_total),
        "valor_frete": float(frete)  # ✅ RETORNA O FRETE NA RESPOSTA
    })


@router.post("/remover/{item_id}")
async def remover_do_carrinho(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove um item do carrinho
    """
    usuario = get_usuario_atual(request, db)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    item = db.query(ItemPedido).filter(ItemPedido.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    # Verifica se o item pertence ao pedido do usuário
    pedido = db.query(Pedido).filter(
        Pedido.id == item.pedido_id,
        Pedido.usuario_id == usuario.id,
        Pedido.status == "Em andamento"
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=403, detail="Item não pertence ao seu carrinho")

    db.delete(item)
    db.commit()

    # Atualiza valor total do pedido
    itens_restantes = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
    total = sum(float(it.subtotal) for it in itens_restantes)
    pedido.valor_total = total
    db.commit()

    return JSONResponse({
        "mensagem": "Item removido do carrinho",
        "valor_total": float(pedido.valor_total)
    })


# Rota para obter dados do carrinho via API (usada pelo JavaScript)
@router.get("/dados")
async def obter_dados_carrinho(
    request: Request,
    usuario: Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Retorna os dados do carrinho em JSON para o frontend
    """
    if not usuario:
        return JSONResponse({
            "itens_carrinho": [],
            "total_geral": 0,
            "total_itens": 0,
            "autenticado": False
        })

    pedido = db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id, 
        Pedido.status == "Em andamento"
    ).first()

    itens_carrinho = []
    total_geral = 0
    total_itens = 0

    if pedido:
        itens = db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido.id).all()
        for item in itens:
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if produto:
                itens_carrinho.append({
                    "id": item.id,
                    "produto_id": produto.id,
                    "nome": produto.nome,
                    "preco": float(produto.preco),
                    "quantidade": item.quantidade,
                    "subtotal": float(item.subtotal),
                    "imagem": produto.imagem or "static/default.png"
                })
                total_geral += float(item.subtotal)
                total_itens += item.quantidade

    return JSONResponse({
        "itens_carrinho": itens_carrinho,
        "total_geral": total_geral,
        "total_itens": total_itens,
        "autenticado": True
    })