import os
import sys

class VFS_CLI:
    def __init__(self, name="VFS"):
        self.vfs_name = name
        self.running = True

    def run(self):
        print(f"Добро пожаловать в {self.vfs_name}!")
        while self.running:
            try:
                user_input = input(f"{self.vfs_name}> ").strip()
                if not user_input:
                    continue
                self.handle_command(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\nВыход из программы.")
                break
            except Exception as e:
                print(e)
                break


    def handle_command(self, user_input: str):
        parts = user_input.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            self.cmd_exit(args)
        elif cmd == "ls":
            self.cmd_ls(args)
        elif cmd == "cd":
            self.cmd_cd(args)
        else:
            print(f"Ошибка: неизвестная команда '{cmd}'.")


    def cmd_ls(self, args):
        print(f"[ls] Аргументы: {args}")

    def cmd_cd(self, args):
        print(f"[cd] Аргументы: {args}")

    def cmd_exit(self, args):
        if args:
            print("Ошибка: команда 'exit' не принимает аргументы.")
            return
        print("Выход из VFS...")
        self.running = False


if __name__ == "__main__":
    name = os.getlogin()
    vfs_name = sys.argv[1] if len(sys.argv) > 1 else name

    cli = VFS_CLI(vfs_name)
    cli.run()
