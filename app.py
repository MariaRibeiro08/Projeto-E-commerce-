from fastapi import FastAPI, HTTPException
from controllers.camiseta_controller import CamisetaController

app = FastAPI()
controller = CamisetaController()

@app.get("/camisetas")
def listar_camisetas():
    return controller.listar()

@app.get("/camisetas/{id}")
def buscar_camiseta(id: int):
    camiseta = controller.buscar(id)
    if camiseta:
        return camiseta.to_dict()
    raise HTTPException(status_code=404, detail="Camiseta não encontrada")

@app.post("/camisetas")
def criar_camiseta(tamanho: str, cor: str, preco: float):
    nova = controller.criar(tamanho, cor, preco)
    return nova.to_dict()

@app.put("/camisetas/{id}")
def atualizar_camiseta(id: int, tamanho: str, cor: str, preco: float):
    camiseta = controller.atualizar(id, tamanho, cor, preco)
    if camiseta:
        return camiseta.to_dict()
    raise HTTPException(status_code=404, detail="Camiseta não encontrada")

@app.delete("/camisetas/{id}")
def deletar_camiseta(id: int):
    if controller.deletar(id):
        return {"detail": "Camiseta deletada"}
    raise HTTPException(status_code=404, detail="Camiseta não encontrada")
