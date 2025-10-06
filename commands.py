from typing import List

from Shell import ShellState
from VFSDir import VFSDir
from VFSFile import VFSFile
from exceptions import CommandError


def cmd_ls(state: ShellState, args: List[str]) -> str:
    # ls [path]
    path = args[0] if args else ""
    try:
        node, comps = state.resolve_path(path) if path else (state._node_by_components(state.current_dir), list(state.current_dir))
    except Exception as e:
        raise CommandError(str(e))
    if node.is_file():
        return node.name
    if isinstance(node, VFSDir):
        lines = []
        for name, child in sorted(node.children.items()):
            t = "d" if child.is_dir() else "-"
            owner = child.owner
            lines.append(f"{t} {owner} {name}")
        return "\n".join(lines)
    return ""

def cmd_cd(state: ShellState, args: List[str]) -> str:
    # cd path
    if not args:
        # go to root/home? we'll go to root
        state.current_dir = [state.vfs_root.name]
        return ""
    path = args[0]
    try:
        node, comps = state.resolve_path(path)
    except Exception as e:
        raise CommandError(str(e))
    if node.is_file():
        raise CommandError("cd: not a directory")
    state.current_dir = comps
    return ""

def cmd_exit(state: ShellState, args: List[str]) -> str:
    raise SystemExit(0)

def cmd_whoami(state: ShellState, args: List[str]) -> str:
    return state.current_user

def cmd_cat(state: ShellState, args: List[str]) -> str:
    if not args:
        raise CommandError("cat: missing operand")
    out_parts = []
    for path in args:
        try:
            node, comps = state.resolve_path(path)
        except Exception as e:
            raise CommandError(str(e))
        if node.is_dir():
            raise CommandError(f"cat: {path}: Is a directory")
        if isinstance(node, VFSFile):
            out_parts.append(node.read_text())
    return "\n".join(out_parts)

def cmd_head(state: ShellState, args: List[str]) -> str:
    # head [-n NUM] file
    n = 10
    files = []
    i = 0
    if len(args) >= 2 and args[0] == "-n":
        try:
            n = int(args[1])
            i = 2
        except ValueError:
            raise CommandError("head: invalid number of lines")
    for path in args[i:]:
        try:
            node, _ = state.resolve_path(path)
        except Exception as e:
            raise CommandError(str(e))
        if node.is_dir():
            raise CommandError(f"head: {path}: Is a directory")
        files.append(node)
    if not files:
        raise CommandError("head: missing file operand")
    out = []
    for f in files:
        text = f.read_text()
        lines = text.splitlines()
        out.append("\n".join(lines[:n]))
    return "\n".join(out)

def cmd_chown(state: ShellState, args: List[str]) -> str:
    # chown owner path
    if len(args) != 2:
        raise CommandError("chown: requires owner and path")
    owner, path = args
    try:
        node, _ = state.resolve_path(path)
    except Exception as e:
        raise CommandError(str(e))
    node.owner = owner
    return ""

def cmd_rmdir(state: ShellState, args: List[str]) -> str:
    # rmdir path
    if len(args) != 1:
        raise CommandError("rmdir: requires single directory path")
    path = args[0]
    try:
        node, comps = state.resolve_path(path)
    except Exception as e:
        raise CommandError(str(e))
    if not node.is_dir():
        raise CommandError("rmdir: not a directory")
    # check empty
    if node.children:
        raise CommandError("rmdir: directory not empty")
    # remove from parent
    if len(comps) <= 1:
        raise CommandError("rmdir: cannot remove root")
    parent_comps = comps[:-1]
    parent = state._node_by_components(parent_comps)
    parent.remove_child(comps[-1])
    return ""
