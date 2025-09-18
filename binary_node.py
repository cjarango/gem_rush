from gem_data import GEM_NAMES

class Node:
    def __init__(self, poder):
        self.poder = poder
        self.nombre = GEM_NAMES.get(poder, f"Gema {poder}")
        self.cantidad = 1  # cantidad de gemas de este poder
        self.left = None
        self.right = None

    # Getters y setters para hijos
    def getLeft(self):
        return self.left
    
    def getRight(self):
        return self.right
    
    def setLeft(self, node):
        self.left = node
        
    def setRight(self, node):
        self.right = node

    # Getter y setter para cantidad
    def getCantidad(self):
        return self.cantidad

    def setCantidad(self, cantidad):
        self.cantidad = cantidad

    def __str__(self):
        return f"{self.nombre} (Poder: {self.poder}, Cantidad: {self.cantidad})"
