import sys
import tkinter as tk

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 1. Fix Resizing bounds
    if "self.root.resizable(False, False)" in line:
        line = line.replace("self.root.resizable(False, False)", "self.root.minsize(450, 650)")
    
    if "self.root.geometry(\"160x200\")" in line:
        new_lines.append("        self.root.minsize(0, 0)\n")
        new_lines.append(line)
        continue
        
    if "self.root.geometry(\"450x650\")" in line and "self.root.minsize" not in "".join(new_lines[-2:]):
        new_lines.append("        self.root.minsize(450, 650)\n")
        new_lines.append(line)
        continue

    # 2. Inject apply_theme right before minimize_window
    if "def minimize_window(self):" in line:
        theme_func = """    def apply_theme(self):
        def set_colors(widget):
            # Safe imports inside method if tk not global
            import tkinter as tk
            try:
                if isinstance(widget, tk.Button) and (widget.cget("text") == "🔴 0s" or widget.cget("fg") == "#FF3333"): return
                if isinstance(widget, tk.Label) and widget.cget("fg") == "#FF3333": return
                widget.configure(bg=self.bg_color)
            except: pass
            
            try:
                if not ((isinstance(widget, tk.Button) or isinstance(widget, tk.Label)) and widget.cget("fg") == "#FF3333"):
                    widget.configure(fg=self.fg_color)
                
                if isinstance(widget, tk.Button) and widget.cget("fg") != "#FF3333":
                    widget.configure(activebackground=self.fg_color, activeforeground=self.bg_color, highlightbackground=self.bg_color)
                
                if isinstance(widget, tk.Text) or isinstance(widget, tk.Entry):
                    widget.configure(insertbackground=self.fg_color, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
                
                if isinstance(widget, tk.Frame) or isinstance(widget, tk.Toplevel):
                    widget.configure(highlightbackground=self.bg_color)
            except: pass
            
            for child in widget.winfo_children():
                set_colors(child)
        
        self.root.configure(bg=self.bg_color)
        set_colors(self.root)

"""
        new_lines.append(theme_func)

    new_lines.append(line)

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("File fully repaired.")
