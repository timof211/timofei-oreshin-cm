import argparse
import base64
import io
import os
import posixpath
import sys
import tkinter as tk
import zipfile

VFS_NAME = "vfs"


class VFS:
    def __init__(self):
        self.nodes: dict = {"/": {"type": "dir"}}

    @classmethod
    def from_zip(cls, zip_path: str) -> "VFS":
        vfs = cls()
        with open(zip_path, "rb") as f:
            raw = f.read()
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for info in zf.infolist():
                name = info.filename.rstrip("/")
                if not name:
                    continue
                path = "/" + name.lstrip("/")
                vfs._ensure_dir(posixpath.dirname(path))
                if info.is_dir():
                    vfs.nodes[path] = {"type": "dir"}
                else:
                    vfs.nodes[path] = {"type": "file", "data": zf.read(info)}
        return vfs

    def _ensure_dir(self, path: str) -> None:
        if not path or path == "/" or path in self.nodes:
            return
        self._ensure_dir(posixpath.dirname(path))
        self.nodes[path] = {"type": "dir"}

    def resolve(self, cwd: str, path: str) -> str:
        if not path.startswith("/"):
            path = posixpath.join(cwd, path)
        return posixpath.normpath(path)

    def exists(self, path: str) -> bool:
        return path in self.nodes

    def is_dir(self, path: str) -> bool:
        n = self.nodes.get(path)
        return n is not None and n["type"] == "dir"

    def listdir(self, path: str) -> list:
        prefix = path.rstrip("/") + "/"
        result = []
        for p in self.nodes:
            if p == "/" or not p.startswith(prefix):
                continue
            rest = p[len(prefix):]
            if rest and "/" not in rest:
                result.append(rest)
        return sorted(result)

    def read(self, path: str) -> bytes:
        n = self.nodes.get(path)
        if n is None:
            raise FileNotFoundError(f"no such file: {path}")
        if n["type"] == "dir":
            raise IsADirectoryError(f"is a directory: {path}")
        return n["data"]

    def mkdir(self, path: str) -> None:
        if path in self.nodes:
            raise FileExistsError(f"already exists: {path}")
        self._ensure_dir(path)

    def touch(self, path: str) -> None:
        if path in self.nodes:
            return
        self._ensure_dir(posixpath.dirname(path))
        self.nodes[path] = {"type": "file", "data": b""}

    def remove(self, path: str) -> None:
        if path not in self.nodes:
            raise FileNotFoundError(f"no such file or directory: {path}")
        if path == "/":
            raise PermissionError("cannot remove root")
        prefix = path.rstrip("/") + "/"
        for p in [p for p in self.nodes if p == path or p.startswith(prefix)]:
            del self.nodes[p]


class ShellEmulator:
    def __init__(self, root: tk.Tk, vfs: VFS, script_path: str | None):
        self.root = root
        self.root.title(f"Shell Emulator — {VFS_NAME}")
        self.root.geometry("1920x1080")

        self.cwd = "/"
        self.running = True
        self.vfs = vfs
        self.script_path = os.path.abspath(script_path) if script_path else None

        self.commands = {
            "ls":    self.cmd_ls,
            "cd":    self.cmd_cd,
            "pwd":   self.cmd_pwd,
            "cat":   self.cmd_cat,
            "mkdir": self.cmd_mkdir,
            "touch": self.cmd_touch,
            "rm":    self.cmd_rm,
            "exit":  self.cmd_exit,
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

        self.print(f"[debug] VFS name      : {VFS_NAME}")
        self.print(f"[debug] VFS nodes     : {len(self.vfs.nodes)}")
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
        if not self.running:
            return
        try:
            self.console.insert("end", text + "\n")
            self.console.see("end")
        except tk.TclError:
            pass

    def new_prompt(self) -> None:
        if not self.running:
            return
        try:
            self.console.insert("end", self.prompt())
            self.console.mark_set("input_start", "end-1c")
            self.console.mark_gravity("input_start", "left")
            self.console.see("end")
        except tk.TclError:
            pass

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
        try:
            idx = self.console.index(f"@{event.x},{event.y}")
            if self.console.compare(idx, "<", "input_start"):
                self.console.mark_set("insert", "end-1c")
                return "break"
        except tk.TclError:
            pass

    def parse(self, line: str) -> list:
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
            self.print(f"{cmd}: {exc}")
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
            if not self.running:
                return
            if not ok:
                self.print(f"[script] stopped at line {lineno} (error)")
                return
        self.print("[script] done")

    def cmd_ls(self, args):
        target = self.vfs.resolve(self.cwd, args[0]) if args else self.cwd
        if not self.vfs.is_dir(target):
            raise NotADirectoryError(f"not a directory: {target}")
        names = self.vfs.listdir(target)
        if names:
            self.print("  ".join(names))

    def cmd_cd(self, args):
        target = self.vfs.resolve(self.cwd, args[0]) if args else "/"
        if not self.vfs.is_dir(target):
            raise NotADirectoryError(f"not a directory: {target}")
        self.cwd = target

    def cmd_pwd(self, args):
        self.print(self.cwd)

    def cmd_cat(self, args):
        if not args:
            raise ValueError("usage: cat <file> [<file>...]")
        for arg in args:
            target = self.vfs.resolve(self.cwd, arg)
            data = self.vfs.read(target)
            try:
                self.print(data.decode("utf-8"))
            except UnicodeDecodeError:
                # двоичные данные — в base64
                self.print(base64.b64encode(data).decode("ascii"))

    def cmd_mkdir(self, args):
        if not args:
            raise ValueError("usage: mkdir <dir> [<dir>...]")
        for arg in args:
            self.vfs.mkdir(self.vfs.resolve(self.cwd, arg))

    def cmd_touch(self, args):
        if not args:
            raise ValueError("usage: touch <file> [<file>...]")
        for arg in args:
            self.vfs.touch(self.vfs.resolve(self.cwd, arg))

    def cmd_rm(self, args):
        if not args:
            raise ValueError("usage: rm <path> [<path>...]")
        for arg in args:
            self.vfs.remove(self.vfs.resolve(self.cwd, arg))

    def cmd_exit(self, args):
        self.running = False
        self.root.destroy()


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Shell Emulator of UNIX-like OS",
    )
    p.add_argument("--vfs", required=True,
                   help="path to VFS ZIP archive")
    p.add_argument("--script", default=None,
                   help="path to a script with emulator commands")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if not os.path.isfile(args.vfs):
        print(f"error: VFS archive not found: {args.vfs}", file=sys.stderr)
        return 1
    if args.script and not os.path.isfile(args.script):
        print(f"error: script not found: {args.script}", file=sys.stderr)
        return 1

    try:
        vfs = VFS.from_zip(args.vfs)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"error: cannot load VFS: {exc}", file=sys.stderr)
        return 1

    root = tk.Tk()
    ShellEmulator(root, vfs=vfs, script_path=args.script)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())