from auth_deps import get_usuario_atual  
from fastapi import (
    APIRouter, Request, Form, UploadFile, File,
    Depends, HTTPException, Cookie
)
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import Produto, Categoria, VariacaoProduto,Usuario
import os, shutil, uuid
from auth_deps import get_usuario_atual 

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
def obter_cor_css(cor_nome):
    """Converte nome da cor para código CSS"""
    if not cor_nome:
        return '#cccccc'
    
    mapa_cores = {
        'preto': '#000000',
        'branco': '#ffffff',
        'vermelho': '#ff0000',
        'azul': '#0000ff', 
        'verde': '#008000',
        'cinza': '#808080',
        'bege': '#f5f5dc',
        'rosa': '#ff69b4',
        'amarelo': '#ffff00',
        'laranja': '#ffa500',
        'roxo': '#800080',
        'marrom': '#8b4513'
    }
    return mapa_cores.get(cor_nome.lower().split()[0], '#cccccc')
# ----------------- FUNÇÕES AUXILIARES ----------------- #
def _ensure_image_obj(produto):
    """
    Garante que o produto tenha uma imagem válida
    CORREÇÃO SIMPLIFICADA
    """
    try:
        # Se não tem imagem ou está vazia, usa padrão
        if not produto.imagem or produto.imagem.strip() == "":
            return 'default.png'
        
        # Remove 'static/' se existir
        if produto.imagem.startswith('static/'):
            return produto.imagem.replace('static/', '')
        
        # Remove 'uploads/' se existir (para evitar duplicação)
        if produto.imagem.startswith('uploads/'):
            return produto.imagem.replace('uploads/', '')
        
        return produto.imagem
        
    except Exception:
        return 'default.png'

async def salvar_imagem(imagem: UploadFile) -> str:
    if not imagem or imagem.filename == "":
        return ""
    nome_unico = f"{uuid.uuid4()}_{imagem.filename}"
    caminho = os.path.join(UPLOAD_DIR, nome_unico)
    with open(caminho, "wb") as arquivo:
        shutil.copyfileobj(imagem.file, arquivo)
    return nome_unico

# FUNÇÃO SIMPLES PARA CRIAR PRODUTO
async def criar_produto_simples(
    nome: str, 
    preco: float, 
    quantidade: int, 
    tamanho: str, 
    cor: str, 
    descricao: str, 
    categoria_id: int,  # ✅ NOVO: categoria
    imagem: UploadFile, 
    db: Session
):
    nome_imagem = await salvar_imagem(imagem)
    novo = Produto(
        nome=nome,
        preco=preco,
        quantidade=quantidade,
        tamanho=tamanho,
        cor=cor,
        descricao=descricao,
        categoria_id=categoria_id,  # ✅ CATEGORIA
        imagem=nome_imagem
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    
    # ✅ CRIA UMA VARIAÇÃO AUTOMATICAMENTE (para o sistema de cores)
    variacao = VariacaoProduto(
        produto_id=novo.id,
        cor=cor,
        tamanho=tamanho,
        quantidade=quantidade,
        imagem=nome_imagem
    )
    db.add(variacao)
    db.commit()
    
    return novo

async def atualizar_produto(id: int, nome: str, preco: float, quantidade: int, tamanho: str, cor: str, descricao: str, imagem: UploadFile, db: Session):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        return None

    produto.nome = nome
    produto.preco = preco
    produto.quantidade = quantidade
    produto.tamanho = tamanho
    produto.cor = cor
    produto.descricao = descricao

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
        # ✅ PRIMEIRO: Deleta as variações do produto
        variacoes = db.query(VariacaoProduto).filter(VariacaoProduto.produto_id == id).all()
        for variacao in variacoes:
            # Remove imagem da variação se existir
            if variacao.imagem and os.path.exists(os.path.join(UPLOAD_DIR, variacao.imagem)):
                try:
                    os.remove(os.path.join(UPLOAD_DIR, variacao.imagem))
                except FileNotFoundError:
                    pass
            db.delete(variacao)
        
        # ✅ DEPOIS: Deleta o produto principal
        if produto.imagem and os.path.exists(os.path.join(UPLOAD_DIR, produto.imagem)):
            try:
                os.remove(os.path.join(UPLOAD_DIR, produto.imagem))
            except FileNotFoundError:
                pass
        
        db.delete(produto)
        db.commit()
    
    return produto

# ----------------- ADMIN COOKIE ----------------- #
def admin_cookie_required(
    is_admin: str = Cookie(default="false"),
    admin_user: str = Cookie(default="")
):
    if is_admin != "true" or not admin_user:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # ✅ Verifica se o usuário está na lista de admins autorizados
    if admin_user not in ADMINS_AUTORIZADOS:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

# ----------------- ROTAS PÚBLICAS ----------------- #
@router.get("/", response_class=HTMLResponse)
async def listar(request: Request, db: Session = Depends(get_db), is_admin: str = Cookie(default="false"), usuario = Depends(get_usuario_atual)):
    produtos = db.query(Produto).all()
    categorias = db.query(Categoria).all()
    
    for produto in produtos:
        _ensure_image_obj(produto)
        
        # ✅ VOLTA AO SISTEMA ANTERIOR (cores por categoria)
        if produto.categoria_id:
            produtos_mesma_categoria = db.query(Produto).filter(
                Produto.categoria_id == produto.categoria_id,
                Produto.id != produto.id
            ).all()
            produto.outras_cores = list(set([p.cor for p in produtos_mesma_categoria if p.cor]))
        else:
            produto.outras_cores = []
    
    mostrar_admin = (is_admin == "true")
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, 
            "produtos": produtos, 
            "is_admin": mostrar_admin, 
            "usuario": usuario,
            "categorias": categorias,
            "obter_cor_css": obter_cor_css
        }
    )
@router.get("/produtos/{id_produto}", response_class=HTMLResponse)
async def detalhe(request: Request, id_produto: int, db: Session = Depends(get_db), is_admin: str = Cookie(default="false"), usuario = Depends(get_usuario_atual)):
    produto = db.query(Produto).filter(Produto.id == id_produto).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    _ensure_image_obj(produto)
    
    # Buscar categoria do produto
    categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first() if produto.categoria_id else None
    
    # Buscar cores e tamanhos disponíveis
    if produto.categoria_id:
        # Busca produtos com mesma categoria
        produtos_mesma_categoria = db.query(Produto).filter(
            Produto.categoria_id == produto.categoria_id
        ).all()
    else:
        produtos_mesma_categoria = [produto]
    
    # Extrai cores e tamanhos únicos
    todas_cores = []
    todos_tamanhos = []
    
    for p in produtos_mesma_categoria:
        if p.cor:
            todas_cores.append(p.cor)
        if p.tamanho:
            todos_tamanhos.append(p.tamanho)
    
    # Remove duplicatas e garante que o produto atual esteja incluído
    cores_disponiveis = list(set(todas_cores))
    tamanhos_disponiveis = list(set(todos_tamanhos))
    
    # Garante que a cor e tamanho do produto atual estejam na lista
    if produto.cor and produto.cor not in cores_disponiveis:
        cores_disponiveis.append(produto.cor)
    
    if produto.tamanho and produto.tamanho not in tamanhos_disponiveis:
        tamanhos_disponiveis.append(produto.tamanho)
    
    # Ordena cores por uma ordem específica se quiser
    ordem_cores = ['BRANCA', 'PRETA', 'CINZA', 'AZUL', 'VERMELHA', 'VERDE', 'BEGE', 'ROSA']
    cores_disponiveis.sort(key=lambda x: ordem_cores.index(x) if x in ordem_cores else len(ordem_cores))
    
    # Ordena tamanhos
    ordem_tamanhos = ['PP', 'P', 'M', 'G', 'GG']
    tamanhos_disponiveis.sort(key=lambda x: ordem_tamanhos.index(x) if x in ordem_tamanhos else len(ordem_tamanhos))
    
    mostrar_admin = (is_admin == "true")
    return templates.TemplateResponse(
        "produto.html",
        {
            "request": request, 
            "produto": produto, 
            "is_admin": mostrar_admin, 
            "usuario": usuario,
            "cores_disponiveis": cores_disponiveis,
            "tamanhos_disponiveis": tamanhos_disponiveis,
            "obter_cor_css": obter_cor_css  # ✅ ADICIONA A FUNÇÃO AQUI
        }
    )
@router.get("/api/produto/{produto_id}")
async def obter_produto_detalhes(produto_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes completos de um produto"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first() if produto.categoria_id else None
    
    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": float(produto.preco),
        "quantidade": produto.quantidade,
        "cor": produto.cor,
        "tamanho": produto.tamanho,
        "imagem": produto.imagem,
        "categoria_id": produto.categoria_id,
        "categoria": categoria.nome if categoria else None
    }
# Adicione esta rota ao produtos_controller.py
@router.get("/api/produto/buscar-por-cor-tamanho")
async def buscar_produto_por_cor_tamanho(
    nome: str,
    cor: str,
    tamanho: str,
    db: Session = Depends(get_db)
):
    """
    Busca um produto pelo nome, cor e tamanho
    """
    print(f"Buscando produto: nome={nome}, cor={cor}, tamanho={tamanho}")
    
    # Busca produto com mesmo nome, cor e tamanho
    produto = db.query(Produto).filter(
        Produto.nome == nome,
        Produto.cor == cor,
        Produto.tamanho == tamanho
    ).first()
    
    if produto:
        return {
            "id": produto.id,
            "nome": produto.nome,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "preco": float(produto.preco),
            "quantidade": produto.quantidade,
            "imagem": produto.imagem
        }
    
    # Se não encontrou, tenta buscar produtos similares
    produtos_similares = db.query(Produto).filter(
        Produto.nome == nome,
        Produto.cor == cor
    ).all()
    
    if produtos_similares:
        # Retorna o primeiro produto com essa cor (independente do tamanho)
        produto = produtos_similares[0]
        return {
            "id": produto.id,
            "nome": produto.nome,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "preco": float(produto.preco),
            "quantidade": produto.quantidade,
            "imagem": produto.imagem
        }
    
    return None
# Adicione esta rota no produtos_controller.py (antes ou depois das outras rotas de API)
@router.get("/api/produto/buscar")
async def buscar_produto_por_cor_tamanho(
    nome: str,
    cor: str,
    tamanho: str,
    db: Session = Depends(get_db)
):
    """
    Busca um produto pelo nome, cor e tamanho
    """
    print(f"Buscando produto: nome={nome}, cor={cor}, tamanho={tamanho}")
    
    # Primeiro: busca exata (nome, cor e tamanho)
    produto = db.query(Produto).filter(
        Produto.nome == nome,
        Produto.cor == cor,
        Produto.tamanho == tamanho
    ).first()
    
    if produto:
        print(f"Produto encontrado (exato): {produto.id} - {produto.nome}")
        return {
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "preco": float(produto.preco),
            "quantidade": produto.quantidade,
            "imagem": produto.imagem
        }
    
    # Segundo: busca por nome e cor (qualquer tamanho)
    produto = db.query(Produto).filter(
        Produto.nome == nome,
        Produto.cor == cor
    ).first()
    
    if produto:
        print(f"Produto encontrado (nome+cor): {produto.id} - {produto.nome}")
        return {
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "preco": float(produto.preco),
            "quantidade": produto.quantidade,
            "imagem": produto.imagem
        }
    
    # Terceiro: busca por nome e tamanho (qualquer cor)
    produto = db.query(Produto).filter(
        Produto.nome == nome,
        Produto.tamanho == tamanho
    ).first()
    
    if produto:
        print(f"Produto encontrado (nome+tamanho): {produto.id} - {produto.nome}")
        return {
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "preco": float(produto.preco),
            "quantidade": produto.quantidade,
            "imagem": produto.imagem
        }
    
    print("Nenhum produto encontrado")
    return None
# ----------------- LISTA ADMIN ----------------- #
@router.get("/lista_adm", response_class=HTMLResponse, dependencies=[Depends(admin_cookie_required)])
async def lista_admin(request: Request, admin_user: str = Cookie(default=""), db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    for produto in produtos:
        _ensure_image_obj(produto)
    
    return templates.TemplateResponse(
        "lista_adm.html",
        {
            "request": request, 
            "produtos": produtos,
            "admin_user": admin_user  # ✅ PASSA O NOME DO ADMIN
        }
    )

# Adicione esta rota no produtos_controller.py
@router.get("/api/produto/variacoes")
async def buscar_variacoes_produto(
    nome: str,
    db: Session = Depends(get_db)
):
    """
    Busca todas as variações (cores/tamanhos) de um produto pelo nome
    """
    print(f"Buscando variações para produto: {nome}")
    
    # Busca todos os produtos com o mesmo nome
    produtos = db.query(Produto).filter(Produto.nome == nome).all()
    
    if not produtos:
        print("Nenhum produto encontrado com esse nome")
        return []
    
    print(f"Encontrados {len(produtos)} produtos com nome '{nome}'")
    
    # Formata os dados para retorno
    variacoes = []
    for produto in produtos:
        variacoes.append({
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao or "Peça essencial e versátil. Confeccionada em algodão macio, com modelagem regular e gola careca. Ideal para o dia a dia ou composições estilosas.",
            "preco": float(produto.preco),
            "quantidade": produto.quantidade,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "imagem": produto.imagem or "default.png",
            "categoria_id": produto.categoria_id
        })
    
    return variacoes
# ----------------- LOGIN ADMIN ----------------- #
@router.get("/login_adm", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login_adm.html", {"request": request})

# Lista de administradores autorizados
ADMINS_AUTORIZADOS = {
    "admin": "sodaz",
    "marlon": "sodaz", 
    "maria": "sodaz",
    "thiago": "sodaz",
    "kayc": "sodaz",
    "matheus": "sodaz",
    "sophia": "sodaz"
}

@router.post("/login_adm")
async def login_adm(request: Request, username: str = Form(...), password: str = Form(...)):
    # Verifica se é um admin autorizado
    if username in ADMINS_AUTORIZADOS and ADMINS_AUTORIZADOS[username] == password:
        response = RedirectResponse("/lista_adm", status_code=303)

        response.set_cookie(key="is_admin", value="true")
        response.set_cookie(key="admin_user", value=username)  
        return response
    
    return templates.TemplateResponse("login_adm.html", {
        "request": request, 
        "error": "Credenciais incorretas"
    })

# ----------------- ROTAS ADMIN ----------------- #
@router.get("/novo", response_class=HTMLResponse, dependencies=[Depends(admin_cookie_required)])
async def form_novo(request: Request, db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return templates.TemplateResponse("novo.html", {
        "request": request, 
        "categorias": categorias
    })

# ✅ ROTA SIMPLIFICADA - APENAS CATEGORIA
@router.post("/novo", dependencies=[Depends(admin_cookie_required)])
async def criar(
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    tamanho: str = Form(...),
    cor: str = Form(...),
    descricao: str = Form(...),
    categoria_id: int = Form(...),  # ✅ CATEGORIA
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    await criar_produto_simples(
        nome, preco, quantidade, tamanho, cor, descricao, categoria_id, imagem, db
    )
    return RedirectResponse("/lista_adm", status_code=303)

@router.get("/editar/{id}", response_class=HTMLResponse, dependencies=[Depends(admin_cookie_required)])
async def form_editar(id: int, request: Request, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    _ensure_image_obj(produto)
    categorias = db.query(Categoria).all()  # ✅ PARA O SELECT DE CATEGORIAS
    return templates.TemplateResponse("editar.html", {
        "request": request, 
        "produto": produto,
        "categorias": categorias
    })

@router.post("/editar/{id}", dependencies=[Depends(admin_cookie_required)])
async def editar(
    id: int,
    nome: str = Form(...),
    preco: float = Form(...),
    quantidade: int = Form(...),
    tamanho: str = Form(...),
    cor: str = Form(...),
    descricao: str = Form(...),
    categoria_id: int = Form(...),  # ✅ CATEGORIA
    imagem: UploadFile = File(None),  # ✅ OPCIONAL
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        return RedirectResponse("/lista_adm", status_code=303)
    
    produto.nome = nome
    produto.preco = preco
    produto.quantidade = quantidade
    produto.tamanho = tamanho
    produto.cor = cor
    produto.descricao = descricao
    produto.categoria_id = categoria_id  # ✅ ATUALIZA CATEGORIA
    
    if imagem and imagem.filename != "":
        if produto.imagem:
            try:
                os.remove(os.path.join(UPLOAD_DIR, produto.imagem))
            except FileNotFoundError:
                pass
        produto.imagem = await salvar_imagem(imagem)
    
    db.commit()
    return RedirectResponse("/lista_adm", status_code=303)

@router.get("/deletar/{id}", dependencies=[Depends(admin_cookie_required)])
async def deletar(id: int, db: Session = Depends(get_db)):
    await deletar_produto(id, db)
    return RedirectResponse("/lista_adm", status_code=303)

# ----------------- ROTAS DE CATEGORIA ----------------- #
@router.get("/categoria/{categoria_id}", response_class=HTMLResponse)
async def produtos_por_categoria(
    request: Request, 
    categoria_id: int,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_atual)
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    produtos = db.query(Produto).filter(Produto.categoria_id == categoria_id).all()
    
    for produto in produtos:
        _ensure_image_obj(produto)
    
    return templates.TemplateResponse("categoria.html", {
        "request": request,
        "categoria": categoria,
        "produtos": produtos,
        "usuario": usuario
    })

# ----------------- ROTAS PÚBLICAS SIMPLES ----------------- #
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/carrinho", response_class=HTMLResponse)
async def mostrar_carrinho(request: Request, usuario: Usuario = Depends(get_usuario_atual)):
    return templates.TemplateResponse(
        "carrinho.html",
        {"request": request,"usuario": usuario or None, "produtos": [], "total_itens": 0}
    )

# ✅ ROTA DO CHECKOUT (adicionar no final do arquivo)
@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(
    request: Request,
    usuario: Usuario = Depends(get_usuario_atual),  # ✅ AGORA Usuario ESTÁ IMPORTADO
    db: Session = Depends(get_db)
):
    """Página de checkout"""
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "usuario": usuario
    })

@router.get("/cadastro", response_class=HTMLResponse)
async def cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@router.get("/sobre", response_class=HTMLResponse)
async def sobre(request: Request):
    return templates.TemplateResponse("sobre.html", {"request": request})

@router.get("/fale_conosco", response_class=HTMLResponse)
async def fale_conosco(request: Request):
    return templates.TemplateResponse("fale_conosco.html", {"request": request})

@router.get("/busca", response_class=HTMLResponse)
async def busca(request: Request):
    return templates.TemplateResponse("busca.html", {"request": request})

@router.get("/api/produto/{produto_id}/variacoes")
async def obter_variacoes_produto(produto_id: int, db: Session = Depends(get_db)):
    """Retorna todas as variações de um produto"""
    variacoes = db.query(VariacaoProduto).filter(
        VariacaoProduto.produto_id == produto_id
    ).all()
    
    variacoes_data = []
    for variacao in variacoes:
        variacoes_data.append({
            "id": variacao.id,
            "cor": variacao.cor,
            "tamanho": variacao.tamanho,
            "quantidade": variacao.quantidade,
            "imagem": variacao.imagem,
            "preco": variacao.produto.preco  # Preço do produto principal
        })
    
    return JSONResponse(variacoes_data)

@router.get("/debug-produtos")
async def debug_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    debug_info = []
    
    for produto in produtos:
        variacoes = db.query(VariacaoProduto).filter(
            VariacaoProduto.produto_id == produto.id
        ).all()
        
        debug_info.append({
            "id": produto.id,
            "nome": produto.nome,
            "cor": produto.cor,
            "quantidade_variacoes": len(variacoes),
            "cores_variacoes": [v.cor for v in variacoes],
            "tem_imagem": bool(produto.imagem)
        })
    
    return JSONResponse(debug_info)

@router.get("/api/produto/{produto_id}/cores-tamanhos")
async def obter_cores_tamanhos_produto(produto_id: int, db: Session = Depends(get_db)):
    """Retorna cores e tamanhos disponíveis para produtos com mesmo nome e categoria"""
    produto_atual = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto_atual:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Busca produtos com mesmo NOME e mesma CATEGORIA
    produtos_semelhantes = db.query(Produto).filter(
        Produto.nome == produto_atual.nome,
        Produto.categoria_id == produto_atual.categoria_id,
        Produto.id != produto_atual.id  # Exclui o produto atual
    ).all()
    
    # Coleta cores e tamanhos únicos
    cores_disponiveis = list(set([p.cor for p in produtos_semelhantes if p.cor]))
    tamanhos_disponiveis = list(set([p.tamanho for p in produtos_semelhantes if p.tamanho]))
    
    return JSONResponse({
        "cores_disponiveis": cores_disponiveis,
        "tamanhos_disponiveis": tamanhos_disponiveis,
        "produto_base": {
            "nome": produto_atual.nome,
            "categoria": produto_atual.categoria.nome if produto_atual.categoria else None
        }
    })

@router.get("/debug-simples/{produto_id}")
async def debug_simples(produto_id: int, db: Session = Depends(get_db)):
    """Debug simples para ver produto e variações"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    variacoes = db.query(VariacaoProduto).filter(VariacaoProduto.produto_id == produto_id).all()
    
    return {
        "produto": {
            "id": produto.id,
            "nome": produto.nome,
            "cor": produto.cor,
            "tamanho": produto.tamanho,
            "quantidade": produto.quantidade,
            "imagem": produto.imagem
        },
        "total_variacoes": len(variacoes),
        "variacoes": [
            {
                "id": v.id,
                "cor": v.cor,
                "tamanho": v.tamanho, 
                "quantidade": v.quantidade,
                "imagem": v.imagem
            } for v in variacoes
        ]
    }


@router.get("/sobre", response_class=HTMLResponse)
async def sobre(request: Request):
    # Obtém o usuário da sessão (se estiver logado)
    usuario = request.session.get("usuario")
    
    return templates.TemplateResponse(
        "sobre.html", 
        {
            "request": request,
            "usuario": usuario  # Passa o usuário para o template
        }
    )
