# migrar_frete.py
from database import SessionLocal, engine
from sqlalchemy import text

def migrar_frete():
    db = SessionLocal()
    try:
        print("🔄 Adicionando coluna valor_frete...")
        db.execute(text("""
            ALTER TABLE pedidos 
            ADD COLUMN valor_frete DECIMAL(10,2) DEFAULT 0.00
        """))
        
        print("🔄 Adicionando coluna cep_entrega...")
        db.execute(text("""
            ALTER TABLE pedidos 
            ADD COLUMN cep_entrega VARCHAR(10)
        """))
        
        db.commit()
        print("✅ Migração do frete concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrar_frete()