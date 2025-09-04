import argparse
import os
import sys

class VFS_CLI:
    def __init__(self, name: str, vfs_path: str):
        self.vfs_name = name
        self.vfs_path = os.path.abspath(vfs_path) if vfs_path else None
        self.running = True


    def run_interactive(self):
        """Интерактивный режим."""
        print(f"Добро пожаловать в {self.vfs_name}!")
        while self.running:
            try:
                user_input = input(f"{self.vfs_name}> ").strip()
                if not user_input:
                    continue
                ok = self.handle_command(user_input)

                # В интерактиве ошибки только пропускаются (не останавливают цикл)
                if not ok:
                    pass
            except (KeyboardInterrupt, EOFError):
                print("\nВыход из программы.")
                break

    def run_script(self, script_path: str) -> bool:
        """
        Выполнение стартового скрипта. Останавливается при первой ошибке.
        На экран выводится и "ввод", и "вывод" для имитации диалога.
        Возвращает True при полном успехе, False — если исполнение остановлено из-за ошибки.
        """
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as e:
            print(f"Ошибка: не удалось открыть стартовый скрипт '{script_path}': {e}")
            return False

        for i, raw in enumerate(lines, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            print(f"{self.vfs_name}> {line}")
            ok = self.handle_command(line)
            if not ok:
                print(f"Ошибка во время исполнения стартового скрипта '{script_path}' на строке {i}.")
                return False
            if not self.running:
                return True
        return True


    def handle_command(self, user_input: str) -> bool:
        """Парсинг и выполнение команды. True при успехе, False при ошибке."""
        parts = user_input.split()
        if not parts:
            return True
        cmd, *args = parts

        if cmd == "exit":
            return self.cmd_exit(args)
        elif cmd == "ls":
            return self.cmd_ls(args)
        elif cmd == "cd":
            return self.cmd_cd(args)
        else:
            print(f"Ошибка: неизвестная команда '{cmd}'.")
            return False


    def cmd_ls(self, args) -> bool:
        print(f"[ls] Аргументы: {args}")
        return True

    def cmd_cd(self, args) -> bool:
        print(f"[cd] Аргументы: {args}")
        return True

    def cmd_exit(self, args) -> bool:
        if args:
            print("Ошибка: команда 'exit' не принимает аргументы.")
            return False
        print("Выход из VFS...")
        self.running = False
        return True


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="vfs_cli",
        description="Минимальный VFS-эмулятор (Этап 2)."
    )
    parser.add_argument(
        "--vfs-path",
        required=True,
        help="Путь к физическому расположению VFS (обязательный)."
    )
    parser.add_argument(
        "--startup-script",
        help="Путь к стартовому скрипту. Если задан — выполняется перед интерактивом и останавливается на первой ошибке."
    )
    parser.add_argument(
        "--name",
        help="Имя VFS для приглашения. По умолчанию — basename от --vfs-path, либо 'VFS'."
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Не входить в интерактивный режим после успешного выполнения скрипта."
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Имя VFS: --name -> basename(vfs_path) -> "VFS"
    vfs_name = args.name or (os.path.basename(os.path.abspath(args.vfs_path)) or "VFS")

    print("DEBUG | Параметры запуска:")
    print(f"DEBUG | --vfs-path       = {args.vfs_path}")
    print(f"DEBUG | --startup-script = {args.startup_script}")
    print(f"DEBUG | --name           = {args.name}")
    print(f"DEBUG | --no-interactive = {args.no_interactive}")

    cli = VFS_CLI(name=vfs_name, vfs_path=args.vfs_path)

    if args.startup_script:
        ok = cli.run_script(args.startup_script)
        if not ok:
            sys.exit(1)

        if not cli.running:
            sys.exit(0)

    if not args.no_interactive:
        cli.run_interactive()

    return 0


if __name__ == "__main__":
    sys.exit(main())
