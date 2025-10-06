from typing import Dict

from VFSNode import VFSNode


class VFSDir(VFSNode):
    def __init__(self, name: str, owner: str = "root"):
        super().__init__(name, owner)
        self.children: Dict[str, VFSNode] = {}

    def is_dir(self) -> bool:
        return True

    def add_child(self, node: VFSNode):
        self.children[node.name] = node

    def remove_child(self, name: str):
        if name in self.children:
            del self.children[name]
        else:
            raise KeyError(f"Child '{name}' not found")