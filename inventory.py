from binary_node import Node
from gem_data import GEM_NAMES

class Inventory:
    def __init__(self):
        self.root = None

    def insert(self, poder, cantidad=1):
        """Insertar gema en el BST. Si existe, aumentar cantidad."""
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
        else:
            current.setRight(self._insert_recursive(current.getRight(), poder, cantidad))
        return current

    def search(self, poder):
        return self._search_recursive(self.root, poder)

    def _search_recursive(self, node, poder):
        if node is None:
            return None
        if node.poder == poder:
            return node
        elif poder < node.poder:
            return self._search_recursive(node.getLeft(), poder)
        else:
            return self._search_recursive(node.getRight(), poder)

    def inorder(self):
        elements = []
        self._inorder_recursive(self.root, elements)
        return elements

    def _inorder_recursive(self, node, elements):
        if node:
            self._inorder_recursive(node.getLeft(), elements)
            elements.append(node)
            self._inorder_recursive(node.getRight(), elements)

    def delete(self, poder, cantidad=1):
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
            if node.getLeft() is None and node.getRight() is None:
                return None
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

    def _min_value_node(self, node):
        current = node
        while current.getLeft():
            current = current.getLeft()
        return current

    def summary(self):
        elements = self.inorder()
        if not elements:
            return "Inventario vacío"

        lines = []
        for node in elements:
            nombre = GEM_NAMES.get(node.poder, f"Gema {node.poder}")
            lines.append(f"{nombre} × {node.cantidad}")

        return "\n".join(lines)
