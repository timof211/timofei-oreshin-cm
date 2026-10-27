import tkinter as tk

VFS_NAME = "vfs"


class ShellEmulator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"Shell Emulator — {VFS_NAME}")
        self.root.geometry("700x450")

        self.cwd = "/"
        self.running = True
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



    def execute(self, line: str) -> None:
        parts = self.parse(line)
        if not parts:
            return
        cmd, args = parts[0], parts[1:]
        handler = self.commands.get(cmd)
        if handler is None:
            self.print(f"{cmd}: command not found")
            return
        try:
            handler(args)
        except Exception as exc:
            self.print(f"error: {exc}")


    def cmd_ls(self, args):
        self.print(f"ls: args={args}")

    def cmd_cd(self, args):
        self.print(f"cd: args={args}")

    def cmd_exit(self, args):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulator(root)
    root.mainloop()