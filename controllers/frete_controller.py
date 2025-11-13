# frete_controller.py
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from sqlalchemy.orm import Session
import requests
from database import get_db
from auth_deps import get_usuario_atual
from models import Usuario

router = APIRouter()

# CONFIGURAÇÃO REALISTA DA LOJA
LOJA_CONFIG = {
    "cep": "03008020",  # CEP do SENAI Francisco Matarazzo
    "cidade": "São Paulo",
    "estado": "SP",
    "regiao": "Sudeste"
}

# MAPA DE REGIÕES E ESTADOS
REGIOES_BRASIL = {
    "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"]
}

# TABELA DE FRETES POR REGIÃO/DISTÂNCIA
TABELA_FRETES = {
    "local": {  # Mesma cidade (São Paulo)
        "valor": 9.90,
        "prazo": 2
    },
    "estado": {  # Mesmo estado (SP)
        "valor": 12.90,
        "prazo": 3
    },
    "regiao": {  # Mesma região (Sudeste)
        "valor": 18.90,
        "prazo": 5
    },
    "vizinha": {  # Regiões vizinhas (Sul, Centro-Oeste)
        "valor": 24.90,
        "prazo": 7
    },
    "distante": {  # Regiões distantes (Norte, Nordeste)
        "valor": 29.90,
        "prazo": 10
    }
}

@router.get("/api/frete")
def calcular_frete(
    request: Request,
    cep_destino: str = Query(...),
    usuario: Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Calcula o frete baseado no CEP de destino usando regras realistas
    """
    # Verifica se usuário está autenticado
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    # Validação simples de CEP
    if not cep_destino.isdigit() or len(cep_destino) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido")
    
    # Consulta no ViaCEP
    via_cep_url = f"https://viacep.com.br/ws/{cep_destino}/json/"
    
    try:
        resposta = requests.get(via_cep_url, timeout=10)
        resposta.raise_for_status()
        
        dados = resposta.json()
        
        if "erro" in dados:
            raise HTTPException(status_code=400, detail="CEP não encontrado")
        
        # CALCULA FRETE BASEADO NA LOCALIZAÇÃO REAL
        valor_frete, prazo_estimado = calcular_frete_por_localizacao(dados)
        
        # Retorno dados estruturados
        return {
            "endereco": f"{dados.get('logradouro', '')}, {dados.get('bairro', '')}, {dados.get('localidade', '')} - {dados.get('uf', '')}",
            "cep": cep_destino,
            "valor_frete": valor_frete,
            "prazo_estimado_dias": prazo_estimado,
            "cidade": dados.get('localidade', ''),
            "estado": dados.get('uf', ''),
            "regiao": encontrar_regiao_por_estado(dados.get('uf', '')),
            "status": "cálculo concluído"
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Erro ao consultar o CEP: {str(e)}")

def calcular_frete_por_localizacao(dados_destino: dict) -> tuple:
    """
    Calcula frete baseado na distância real entre loja e destino
    """
    cidade_destino = dados_destino.get('localidade', '')
    estado_destino = dados_destino.get('uf', '')
    regiao_destino = encontrar_regiao_por_estado(estado_destino)
    
    # 1. MESMA CIDADE (São Paulo)
    if cidade_destino.upper() == LOJA_CONFIG["cidade"].upper():
        return TABELA_FRETES["local"]["valor"], TABELA_FRETES["local"]["prazo"]
    
    # 2. MESMO ESTADO (SP)
    elif estado_destino.upper() == LOJA_CONFIG["estado"].upper():
        return TABELA_FRETES["estado"]["valor"], TABELA_FRETES["estado"]["prazo"]
    
    # 3. MESMA REGIÃO (Sudeste)
    elif regiao_destino == LOJA_CONFIG["regiao"]:
        return TABELA_FRETES["regiao"]["valor"], TABELA_FRETES["regiao"]["prazo"]
    
    # 4. REGIÕES VIZINHAS (Sul, Centro-Oeste)
    elif regiao_destino in ["Sul", "Centro-Oeste"]:
        return TABELA_FRETES["vizinha"]["valor"], TABELA_FRETES["vizinha"]["prazo"]
    
    # 5. REGIÕES DISTANTES (Norte, Nordeste)
    elif regiao_destino in ["Norte", "Nordeste"]:
        return TABELA_FRETES["distante"]["valor"], TABELA_FRETES["distante"]["prazo"]
    
    # Fallback para casos não mapeados
    else:
        return 25.90, 8

def encontrar_regiao_por_estado(uf: str) -> str:
    """
    Encontra a região do Brasil baseado na UF
    """
    uf = uf.upper()
    for regiao, estados in REGIOES_BRASIL.items():
        if uf in estados:
            return regiao
    return "Desconhecida"

# ROTA EXTRA: CONSULTAR TABELA DE FRETES
@router.get("/api/frete/tabela")
def consultar_tabela_frete():
    """
    Retorna a tabela completa de fretes para exibição no frontend
    """
    return {
        "loja": LOJA_CONFIG,
        "tabela_fretes": TABELA_FRETES,
        "regioes": REGIOES_BRASIL
    }