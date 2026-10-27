import argparse
import os
import sys
import tkinter as tk

VFS_NAME = "vfs"


class ShellEmulator:
    def __init__(self, root: tk.Tk, vfs_path: str, script_path: str | None):
        self.root = root
        self.root.title(f"Shell Emulator — {VFS_NAME}")
        self.root.geometry("700x450")

        self.cwd = "/"
        self.running = True
        self.vfs_path = os.path.abspath(vfs_path)
        self.script_path = os.path.abspath(script_path) if script_path else None

        self.commands = {
            "ls":   self.cmd_ls,
            "cd":   self.cmd_cd,
            "exit": self.cmd_exit,
        }

        self.console = tk.Text(
            root, bg="black", fg="#00ff00",
            font=("Consolas", 11),
            insertbackground="#d0ffd0",
        )
        self.console.pack(fill="both", expand=True)
        self.console.focus_set()

        self.console.bind("<Return>",    self.on_enter)
        self.console.bind("<BackSpace>", self.on_backspace)
        self.console.bind("<Delete>",    self.on_delete)
        self.console.bind("<Left>",      self.clamp_left)
        self.console.bind("<Up>",        self.block_key)
        self.console.bind("<Down>",      self.block_key)
        self.console.bind("<Tab>",       self.block_key)
        self.console.bind("<Home>",      self.on_home)
        self.console.bind("<Button-1>",  self.clamp_click)


        self.print(f"[debug] VFS path      : {self.vfs_path}")
        self.print(f"[debug] Script path   : {self.script_path or '<none>'}")
        if self.script_path:
            self.print(f"[debug] Script exists : {os.path.isfile(self.script_path)}")
        self.print("")


        if self.script_path:
            self.run_script(self.script_path)

        if self.running:
            self.new_prompt()


    def prompt(self) -> str:
        return f"{VFS_NAME}:{self.cwd}$ "

    def print(self, text: str) -> None:
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def new_prompt(self) -> None:
        self.console.insert("end", self.prompt())
        self.console.mark_set("input_start", "end-1c")
        self.console.mark_gravity("input_start", "left")
        self.console.see("end")



    def on_enter(self, _event):
        line = self.console.get("input_start", "end-1c")
        self.console.insert("end", "\n")
        self.execute(line)
        if self.running:
            self.new_prompt()
        return "break"

    def on_backspace(self, _event):
        if self.console.compare("insert", ">", "input_start"):
            return
        return "break"

    def on_delete(self, _event):
        if self.console.compare("insert", "<", "end-1c"):
            return
        return "break"

    def clamp_left(self, _event):
        if self.console.compare("insert", "<=", "input_start"):
            return "break"

    def on_home(self, _event):
        self.console.mark_set("insert", "input_start")
        return "break"

    def block_key(self, _event):
        return "break"

    def clamp_click(self, event):
        idx = self.console.index(f"@{event.x},{event.y}")
        if self.console.compare(idx, "<", "input_start"):
            self.console.mark_set("insert", "end-1c")
            return "break"


    def parse(self, line: str) -> list[str]:
        return line.split()


    def execute(self, line: str) -> bool:
        parts = self.parse(line)
        if not parts:
            return True
        cmd, args = parts[0], parts[1:]
        handler = self.commands.get(cmd)
        if handler is None:
            self.print(f"{cmd}: command not found")
            return False
        try:
            return handler(args) is not False
        except Exception as exc:
            self.print(f"error: {exc}")
            return False


    def run_script(self, path: str) -> None:
        self.print(f"[script] Running: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as exc:
            self.print(f"[script] cannot read script: {exc}")
            return

        for lineno, raw in enumerate(lines, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            self.print(self.prompt() + line)
            ok = self.execute(line)
            if not ok:
                self.print(f"[script] stopped at line {lineno} (error)")
                return
            if not self.running:
                return
        self.print("[script] done")

    # ---------- команды ----------
    def cmd_ls(self, args):
        self.print(f"ls: args={args}")

    def cmd_cd(self, args):
        self.print(f"cd: args={args}")

    def cmd_exit(self, args):
        self.running = False
        self.root.destroy()


# ---------- CLI ----------
def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Shell Emuator of UNIX-like OS",
    )
    p.add_argument(
        "--vfs", default=".",
        help="physical path to VFS",
    )
    p.add_argument(
        "--script", default=None,
        help="path to a script with emulator commands",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if not os.path.isdir(args.vfs):
        print(f"error: VFS path is not a directory: {args.vfs}", file=sys.stderr)
        return 1
    if args.script and not os.path.isfile(args.script):
        print(f"error: script not found: {args.script}", file=sys.stderr)
        return 1

    root = tk.Tk()
    ShellEmulator(root, vfs_path=args.vfs, script_path=args.script)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())