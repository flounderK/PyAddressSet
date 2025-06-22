# AddressSet.py - Python translation of Ghidra's AddressSet.java
# For static analysis tooling, including custom red-black tree

from abc import ABC, abstractmethod
from typing import Optional, Iterator, List

# === Core Domain Classes ===
class Address:
    def __init__(self, offset: int):
        self.offset = offset

    def __lt__(self, other: 'Address') -> bool:
        return self.offset < other.offset

    def __le__(self, other: 'Address') -> bool:
        return self.offset <= other.offset

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Address) and self.offset == other.offset

    def __hash__(self):
        return hash(self.offset)

    def next(self) -> 'Address':
        return Address(self.offset + 1)

    def previous(self) -> 'Address':
        return Address(self.offset - 1)

    def subtract(self, other: 'Address') -> int:
        return self.offset - other.offset

    def __repr__(self):
        return f"Address({self.offset})"


class AddressRange:
    def __init__(self, start: Address, end: Address):
        if end < start:
            raise ValueError("End address must not be less than start address")
        self.start = start
        self.end = end

    def contains(self, addr: Address) -> bool:
        return self.start <= addr <= self.end

    def get_min_address(self) -> Address:
        return self.start

    def get_max_address(self) -> Address:
        return self.end

    def get_length(self) -> int:
        return self.end.offset - self.start.offset + 1

    def __repr__(self):
        return f"AddressRange({self.start}, {self.end})"


# === AddressSetView Interface ===
class AddressSetView(ABC):
    @abstractmethod
    def contains(self, *args) -> bool:
        pass

    @abstractmethod
    def get_address_ranges(self) -> Iterator[AddressRange]:
        pass

    @abstractmethod
    def get_num_addresses(self) -> int:
        pass


# === Red-Black Tree Node ===
class RBNode:
    RED = True
    BLACK = False

    def __init__(self, key: Address, value: Address, nil=None):
        self.key = key
        self.value = value
        self.color = RBNode.RED
        self.left = nil
        self.right = nil
        self.parent = nil

    def is_red(self):
        return self.color == RBNode.RED


# === Red-Black Tree ===
class RedBlackTree:
    def __init__(self):
        self.nil = RBNode(None, None)
        self.nil.color = RBNode.BLACK
        self.nil.left = self.nil.right = self.nil.parent = self.nil
        self.root = self.nil

    def left_rotate(self, x: RBNode):
        y = x.right
        x.right = y.left
        if y.left != self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, y: RBNode):
        x = y.left
        y.left = x.right
        if x.right != self.nil:
            x.right.parent = y
        x.parent = y.parent
        if y.parent == self.nil:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def insert(self, key: Address, value: Address):
        z = RBNode(key, value, self.nil)
        y = self.nil
        x = self.root
        while x != self.nil:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y == self.nil:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        z.left = self.nil
        z.right = self.nil
        z.color = RBNode.RED
        self.insert_fixup(z)

    def insert_fixup(self, z: RBNode):
        while z.parent.color == RBNode.RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                if y.color == RBNode.RED:
                    z.parent.color = RBNode.BLACK
                    y.color = RBNode.BLACK
                    z.parent.parent.color = RBNode.RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self.left_rotate(z)
                    z.parent.color = RBNode.BLACK
                    z.parent.parent.color = RBNode.RED
                    self.right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                if y.color == RBNode.RED:
                    z.parent.color = RBNode.BLACK
                    y.color = RBNode.BLACK
                    z.parent.parent.color = RBNode.RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self.right_rotate(z)
                    z.parent.color = RBNode.BLACK
                    z.parent.parent.color = RBNode.RED
                    self.left_rotate(z.parent.parent)
        self.root.color = RBNode.BLACK

    def inorder(self) -> Iterator[RBNode]:
        def _inorder(node):
            if node and node != self.nil:
                yield from _inorder(node.left)
                yield node
                yield from _inorder(node.right)
        return _inorder(self.root)

    def find_range_containing(self, addr: Address) -> Optional[RBNode]:
        node = self.root
        while node != self.nil:
            if addr < node.key:
                node = node.left
            elif addr > node.value:
                node = node.right
            else:
                return node
        return None


# === AddressSet Concrete Implementation ===
class AddressSet(AddressSetView):
    def __init__(self, init_range: Optional[AddressRange] = None):
        self.tree = RedBlackTree()
        self.address_count = 0
        if init_range:
            self.add(init_range)

    def add(self, range_: AddressRange):
        self.tree.insert(range_.start, range_.end)
        self.address_count += range_.get_length()

    def contains(self, *args) -> bool:
        if len(args) == 1 and isinstance(args[0], Address):
            node = self.tree.find_range_containing(args[0])
            return node is not None
        elif len(args) == 2 and all(isinstance(arg, Address) for arg in args):
            start, end = args
            addr = start
            while addr <= end:
                if not self.contains(addr):
                    return False
                addr = addr.next()
            return True
        elif len(args) == 1 and isinstance(args[0], AddressSetView):
            for r in args[0].get_address_ranges():
                if not self.contains(r.get_min_address(), r.get_max_address()):
                    return False
            return True
        else:
            raise TypeError("Unsupported arguments to contains()")

    def get_address_ranges(self) -> Iterator[AddressRange]:
        for node in self.tree.inorder():
            yield AddressRange(node.key, node.value)

    def get_num_addresses(self) -> int:
        return self.address_count

    def intersect(self, other: AddressSetView) -> 'AddressSet':
        result = AddressSet()
        for r1 in self.get_address_ranges():
            for r2 in other.get_address_ranges():
                start = max(r1.get_min_address(), r2.get_min_address())
                end = min(r1.get_max_address(), r2.get_max_address())
                if start <= end:
                    result.add(AddressRange(start, end))
        return result

    def union(self, other: AddressSetView) -> 'AddressSet':
        result = AddressSet()
        for r in self.get_address_ranges():
            result.add(r)
        for r in other.get_address_ranges():
            result.add(r)
        return result
