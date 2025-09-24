from core.binary_node import Node
from core.interfaces.i_inventory import IInventory
from typing import Optional, List

class Inventory(IInventory):
    """BST que almacena gemas por su poder (clave)."""

    def __init__(self):
        self.root: Optional[Node] = None

    # -------------------
    # Implementación de IInventory
    # -------------------
    def insert(self, poder: int, cantidad: int = 1) -> None:
        node = self.search(poder)
        if node:
            node.setCantidad(node.getCantidad() + cantidad)
        else:
            self.root = self._insert_recursive(self.root, poder, cantidad)

    def _insert_recursive(self, current, poder, cantidad):
        if current is None:
            new_node = Node(poder)
            new_node.setCantidad(cantidad)
            return new_node
        if poder < current.poder:
            current.setLeft(self._insert_recursive(current.getLeft(), poder, cantidad))
        elif poder > current.poder:
            current.setRight(self._insert_recursive(current.getRight(), poder, cantidad))
        else:  # Ya existe nodo, sumamos cantidad
            current.setCantidad(current.getCantidad() + cantidad)
        return current

    def search(self, poder: int) -> Optional[Node]:
        return self._search_recursive(self.root, poder)

    def _search_recursive(self, node, poder) -> Optional[Node]:
        if node is None:
            return None
        if node.poder == poder:
            return node
        elif poder < node.poder:
            return self._search_recursive(node.getLeft(), poder)
        else:
            return self._search_recursive(node.getRight(), poder)

    def delete(self, poder: int, cantidad: int = 1) -> None:
        self.root = self._delete_recursive(self.root, poder, cantidad)

    def _delete_recursive(self, node, poder, cantidad):
        if node is None:
            return None
        if poder < node.poder:
            node.setLeft(self._delete_recursive(node.getLeft(), poder, cantidad))
        elif poder > node.poder:
            node.setRight(self._delete_recursive(node.getRight(), poder, cantidad))
        else:
            if node.cantidad > cantidad:
                node.setCantidad(node.cantidad - cantidad)
                return node
            if node.getLeft() is None:
                return node.getRight()
            if node.getRight() is None:
                return node.getLeft()
            successor = self._min_value_node(node.getRight())
            node.poder = successor.poder
            node.nombre = successor.nombre
            node.cantidad = successor.cantidad
            node.setRight(self._delete_recursive(node.getRight(), successor.poder, successor.cantidad))
        return node

    def inorder(self) -> List[Node]:
        elements = []
        self._inorder_recursive(self.root, elements)
        return elements

    def _inorder_recursive(self, node, elements: List[Node]):
        if node:
            self._inorder_recursive(node.getLeft(), elements)
            elements.append(node)
            self._inorder_recursive(node.getRight(), elements)
    
    def _min_value_node(self, node):
        current = node
        while current.getLeft():
            current = current.getLeft()
        return current
