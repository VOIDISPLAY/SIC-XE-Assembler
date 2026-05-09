import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from loader import load_htme


class MemoryVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Modi-SIC/XE Memory Visualizer")
        self.root.geometry("1500x850")
        self.root.configure(bg="#202020")
        self.create_title()
        self.create_buttons()
        self.create_table()
        self.load_memory_into_table()

    def create_title(self):
        title = tk.Label(
            self.root,
            text="Modi-SIC/XE Memory Visualizer",
            font=("Consolas", 24, "bold"),
            fg="#FF0000",
            bg="#202020"
        )
        title.pack(pady=10)

    def create_buttons(self):
        button_frame = tk.Frame(self.root, bg="#202020")
        button_frame.pack(fill="x", padx=10)

        reload_button = tk.Button(
            button_frame,
            text="Reload HTME",
            font=("Consolas", 12, "bold"),
            bg="#AA0000",
            fg="white",
            padx=15,
            pady=5,
            command=self.reload_memory
        )

        reload_button.pack(side="right")

    def create_table(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ["Address"] + [f"{i:X}" for i in range(16)]
        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=70, anchor="center")

        scrollbar_y = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar_x = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background="#2B2B2B",
            foreground="white",
            fieldbackground="#2B2B2B",
            rowheight=28,
            font=("Consolas", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#AA0000",
            foreground="white",
            font=("Consolas", 11, "bold")
        )
    def load_memory_into_table(self):
        try:
            current_folder = os.path.dirname(os.path.abspath(__file__))
            parent_folder = os.path.dirname(current_folder)
            htme_path = os.path.join(
                parent_folder,
                "pass2out",
                "HTME.txt"
            )
            memory = load_htme(htme_path)
            for address in range(0, len(memory.mem), 16):
                row = memory.mem[address:address + 16]
                values = [f"{address:06X}"]
                for byte in row:
                    values.append(f"{byte:02X}")
                if any(byte != 0 for byte in row):
                    tag = "used"
                else:
                    tag = "empty"
                self.tree.insert(
                    "",
                    "end",
                    values=values,
                    tags=(tag,)
                )
            self.tree.tag_configure("used", background="#353535")
            self.tree.tag_configure("empty", background="#202020")
        except FileNotFoundError:
            messagebox.showerror(
                "File Error",
                "HTME.txt was not found in the current folder."
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    def reload_memory(self):
        self.load_memory_into_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryVisualizer(root)
    root.mainloop()