class Camiseta:
    def __init__(self, id, tamanho, cor, preco):
        self.id = id
        self.tamanho = tamanho
        self.cor = cor
        self.preco = preco

    def to_dict(self):
        return {
            "id": self.id,
            "tamanho": self.tamanho,
            "cor": self.cor,
            "preco": self.preco
        }
