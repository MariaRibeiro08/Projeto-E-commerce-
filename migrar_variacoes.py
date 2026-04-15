
# migrar_variações.py
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal
from models import Produto, VariacaoProduto

db = SessionLocal()

# Para cada produto, cria uma variação baseada nos dados atuais
produtos = db.query(Produto).all()

for produto in produtos:
    # Verifica se já existe variação para este produto
    variacao_existente = db.query(VariacaoProduto).filter(
        VariacaoProduto.produto_id == produto.id
    ).first()
    
    if not variacao_existente and produto.cor and produto.tamanho:
        # Cria variação com os dados atuais
        variacao = VariacaoProduto(
            produto_id=produto.id,
            cor=produto.cor,
            tamanho=produto.tamanho,
            quantidade=produto.quantidade,
            imagem=produto.imagem
        )
        db.add(variacao)
        print(f"Criada variação para produto {produto.id} - {produto.nome}")

db.commit()
print("Migração concluída!")
db.close()