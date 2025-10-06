from typing import List, Tuple

from VFSDir import VFSDir
from VFSNode import VFSNode


class ShellState:
    def __init__(self, vfs_root: VFSDir, vfs_name: str, current_user: str = "guest"):
        self.vfs_root = vfs_root
        self.vfs_name = vfs_name
        self.current_dir: List[str] = [vfs_root.name]  # path components from root (root included)
        self.current_user = current_user

    def resolve_path(self, path: str) -> Tuple[VFSNode, List[str]]:
        """
        Простой путь:
        - Абсолютный: начинается с '/'
        - Относительный: относительно текущей директории
        - '..' поддерживается
        Возвращает (node, full_path_components)
        """
        if path == "":
            # текущая директория
            node = self._node_by_components(self.current_dir)
            return node, list(self.current_dir)
        comps = path.split("/")
        if path.startswith("/"):
            comps = [c for c in comps if c]  # drop leading empty
            start = [self.vfs_root.name]
        else:
            comps = [c for c in comps if c]
            start = list(self.current_dir)
        stack = start
        for c in comps:
            if c == "." or c == "":
                continue
            if c == "..":
                if len(stack) > 1:
                    stack.pop()
                continue
            # descend
            node = self._node_by_components(stack)
            if not isinstance(node, VFSDir):
                raise NotADirectoryError(f"'{ '/'.join(stack) }' is not a directory")
            if c not in node.children:
                raise FileNotFoundError(f"No such file or directory: {c}")
            stack.append(c)
        node = self._node_by_components(stack)
        return node, stack

    def _node_by_components(self, comps: List[str]) -> VFSNode:
        node: VFSNode = self.vfs_root
        if not comps:
            return node
        # comps[0] is root.name
        if comps[0] != self.vfs_root.name:
            raise ValueError("Invalid path (root mismatch)")
        for comp in comps[1:]:
            if not isinstance(node, VFSDir):
                raise NotADirectoryError(f"'{node.name}' is not a directory")
            if comp not in node.children:
                raise FileNotFoundError(f"No such file or directory: {comp}")
            node = node.children[comp]
        return node

    def cwd_str(self) -> str:
        # Return path like /root/home/alice
        return "/" + "/".join(self.current_dir[1:])  # omit root name in leading slash for nicer format
