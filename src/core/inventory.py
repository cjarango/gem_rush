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
        else:
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
            # Reducir cantidad si es mayor a la que se desea eliminar
            if node.cantidad > cantidad:
                node.setCantidad(node.cantidad - cantidad)
                return node
            # Si no hay hijo izquierdo
            if node.getLeft() is None:
                return node.getRight()
            # Si no hay hijo derecho
            if node.getRight() is None:
                return node.getLeft()
            # Encontrar sucesor y reemplazar
            successor = self._min_value_node(node.getRight())
            node.poder = successor.poder
            node.nombre = getattr(successor, "nombre", None)
            node.cantidad = successor.cantidad
            node.setRight(self._delete_recursive(node.getRight(), successor.poder, successor.cantidad))
        return node

    # -------------------
    # Método auxiliar
    # -------------------
    def _min_value_node(self, node):
        """Devuelve el nodo con menor poder en el subárbol dado."""
        current = node
        while current.getLeft():
            current = current.getLeft()
        return current

    # -------------------
    # Recorridos
    # -------------------
    def inorder(self) -> List[Node]:
        elements = []
        self._inorder_recursive(self.root, elements)
        return elements

    def _inorder_recursive(self, node, elements: List[Node]):
        if node:
            self._inorder_recursive(node.getLeft(), elements)
            elements.append(node)
            self._inorder_recursive(node.getRight(), elements)

    def preorder(self) -> List[str]:
        result = []
        self._preorder_recursive(self.root, result)
        return result

    def _preorder_recursive(self, node, result: List[str]):
        if node:
            result.append(f"{node.poder};{node.getCantidad()}")
            self._preorder_recursive(node.getLeft(), result)
            self._preorder_recursive(node.getRight(), result)

    # -------------------
    # Métodos adicionales
    # -------------------
    def max_value(self) -> Optional[Node]:
        current = self.root
        if not current:
            return None
        while current.getRight():
            current = current.getRight()
        return current

    def min_value(self) -> Optional[Node]:
        current = self.root
        if not current:
            return None
        while current.getLeft():
            current = current.getLeft()
        return current

    def successor(self, poder: int) -> Optional[Node]:
        succ = None
        node = self.root
        while node:
            if poder < node.poder:
                succ = node
                node = node.getLeft()
            else:
                node = node.getRight()
        return succ

    def predecessor(self, poder: int) -> Optional[Node]:
        pred = None
        node = self.root
        while node:
            if poder > node.poder:
                pred = node
                node = node.getRight()
            else:
                node = node.getLeft()
        return pred
