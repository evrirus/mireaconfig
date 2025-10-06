import base64
import json
import os
from typing import Tuple

from VFSNode import VFSNode
from commands import *
from exceptions import CommandError


def load_vfs_from_json(path: str) -> Tuple[VFSDir, str]:
    """
    Ожидаемый формат JSON:
    {
      "name": "vfs_root",
      "type": "dir",
      "owner": "user",
      "children": [
         {"name":"file1.txt","type":"file","owner":"user","content_b64":"..."},
         {"name":"subdir","type":"dir","owner":"user","children":[ ... ]}
      ]
    }
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"VFS file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    root, vfs_name = _parse_vfs_node(data)
    if not isinstance(root, VFSDir):
        raise ValueError("Корневой объект VFS должен быть директорией")
    return root, vfs_name

def _parse_vfs_node(data: dict) -> Tuple[VFSNode, str]:
    if "type" not in data or "name" not in data:
        raise ValueError("VFS node missing 'type' or 'name'")
    node_type = data["type"]
    name = data["name"]
    owner = data.get("owner", "root")
    if node_type == "file":
        content_b64 = data.get("content_b64", "")
        return VFSFile(name=name, content_b64=content_b64, owner=owner), name
    elif node_type == "dir":
        dirnode = VFSDir(name=name, owner=owner)
        for child in data.get("children", []):
            child_node, _ = _parse_vfs_node(child)
            dirnode.add_child(child_node)
        return dirnode, name
    else:
        raise ValueError(f"Unknown VFS node type: {node_type}")

def default_vfs() -> Tuple[VFSDir, str]:
    # Минимальный встроенный VFS для запуска без файла
    root = VFSDir(name="root", owner="root")
    root.add_child(VFSFile("readme.txt", content_b64=base64.b64encode(b"Welcome to VFS emulator\n").decode()))
    etc = VFSDir("etc")
    etc.add_child(VFSFile("config", content_b64=base64.b64encode(b"config=1\n").decode()))
    home = VFSDir("home")
    alice = VFSDir("alice", owner="alice")
    alice.add_child(VFSFile("notes.txt", content_b64=base64.b64encode(b"These are Alice's notes\nLine2\n").decode(), owner="alice"))
    home.add_child(alice)
    root.add_child(etc)
    root.add_child(home)
    return root, "builtin_vfs"


def simple_parse(line: str) -> Tuple[str, List[str]]:
    """
    Разделяет по пробелам на команду и аргументы.
    (Соответствует требованию: простой парсер)
    """
    parts = [p for p in line.strip().split(" ") if p != ""]
    if not parts:
        return "", []
    return parts[0], parts[1:]


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "whoami": cmd_whoami,
    "cat": cmd_cat,
    "head": cmd_head,
    "chown": cmd_chown,
    "rmdir": cmd_rmdir,
}
# -------------------------
# REPL и выполнение строк
# -------------------------
def execute_command_line(state: ShellState, line: str) -> str:
    cmd_name, args = simple_parse(line)
    if cmd_name == "":
        return ""
    if cmd_name not in COMMANDS:
        raise CommandError(f"Unknown command: {cmd_name}")
    func = COMMANDS[cmd_name]
    return func(state, args)

def run_repl(state: ShellState):
    try:
        while True:
            prompt = f"{state.vfs_name}:{state.cwd_str()}$ "
            try:
                line = input(prompt)
            except EOFError:
                print()
                break
            try:
                out = execute_command_line(state, line)
                if out is not None and out != "":
                    print(out)
            except CommandError as ce:
                print(f"Error: {ce}")
            except SystemExit:
                break
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")

# -------------------------
# Стартовый скрипт
# -------------------------
def execute_startup_script(state: ShellState, script_path: str) -> None:
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Startup script not found: {script_path}")
    with open(script_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for raw in lines:
        line = raw.rstrip("\n")
        # echo the input as if user typed it
        print(f"{state.vfs_name}:{state.cwd_str()}$ {line}")
        try:
            out = execute_command_line(state, line)
            if out is not None and out != "":
                print(out)
        except CommandError as ce:
            print(f"Error: {ce}")
            raise RuntimeError(f"Startup script stopped due to error: {ce}")
        except SystemExit:
            # exit in script -> terminate
            raise SystemExit(0)