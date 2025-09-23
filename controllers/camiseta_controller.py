from models.camiseta import Camiseta

class CamisetaController:
    def __init__(self):
        self.camisetas = []
        self.next_id = 1

    def listar(self):
        return [c.to_dict() for c in self.camisetas]

    def buscar(self, id):
        for c in self.camisetas:
            if c.id == id:
                return c
        return None

    def criar(self, tamanho, cor, preco):
        nova = Camiseta(self.next_id, tamanho, cor, preco)
        self.camisetas.append(nova)
        self.next_id += 1
        return nova

    def atualizar(self, id, tamanho, cor, preco):
        camiseta = self.buscar(id)
        if camiseta:
            camiseta.tamanho = tamanho
            camiseta.cor = cor
            camiseta.preco = preco
            return camiseta
        return None

    def deletar(self, id):
        camiseta = self.buscar(id)
        if camiseta:
            self.camisetas.remove(camiseta)
            return True
        return False
