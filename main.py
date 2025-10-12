import argparse
import sys

from Shell import ShellState
from utils import load_vfs_from_json, default_vfs, run_repl, execute_startup_script


def main(argv=None):
    parser = argparse.ArgumentParser(description="VFS Shell Emulator (variant 13)")
    parser.add_argument("--vfs", help="Path to VFS JSON file", default=None)
    parser.add_argument("--startup", help="Path to startup script", default=None)
    parser.add_argument("--vfs-name", help="Name of VFS to display in prompt (overrides)", default=None)
    parser.add_argument("--user", help="Current user name (whoami)", default="guest")
    args = parser.parse_args(argv)


    print("Debug: startup parameters:")
    print(f"  vfs: {args.vfs}")
    print(f"  startup: {args.startup}")
    print(f"  vfs_name override: {args.vfs_name}")
    print(f"  user: {args.user}")


    if args.vfs:
        try:
            vfs_root, vfs_name = load_vfs_from_json(args.vfs)
        except Exception as e:
            print(f"Error loading VFS: {e}")
            sys.exit(1)
    else:
        vfs_root, vfs_name = default_vfs()

    if args.vfs_name:
        vfs_name = args.vfs_name

    state = ShellState(vfs_root=vfs_root, vfs_name=vfs_name, current_user=args.user)



    if args.startup:
        try:
            execute_startup_script(state, args.startup)
        except SystemExit:
            print("Startup script requested exit. Exiting.")
            sys.exit(0)
        except Exception as e:
            print(f"Error during startup script execution: {e}")
            sys.exit(1)


    run_repl(state)

if __name__ == "__main__":
    main()