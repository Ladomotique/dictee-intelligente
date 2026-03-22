import json

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Open Settings -> color picker 
orig_color_frame = """        # Colors Setting
        col_frame = tk.Frame(dialog, bg=self.bg_color)
        col_frame.pack(pady=5)
        
        tk.Label(col_frame, text="Fond:", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color).pack(side="left")
        bg_entry = tk.Entry(col_frame, width=8, font=("Courier", 10), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, relief="ridge", borderwidth=3)
        bg_entry.pack(side="left", padx=5)
        bg_entry.insert(0, self.bg_color)
        
        tk.Label(col_frame, text="Texte:", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(10,0))
        fg_entry = tk.Entry(col_frame, width=8, font=("Courier", 10), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, relief="ridge", borderwidth=3)
        fg_entry.pack(side="left", padx=5)
        fg_entry.insert(0, self.fg_color)"""

new_color_frame = """        # Colors Setting
        tk.Label(dialog, text="- COULEURS -", font=("Courier", 11, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=(5, 5))
        col_frame = tk.Frame(dialog, bg=self.bg_color)
        col_frame.pack(pady=5)
        
        from tkinter import colorchooser
        
        self.tmp_bg = self.bg_color
        self.tmp_fg = self.fg_color
        
        def pick_bg():
            color = colorchooser.askcolor(color=self.tmp_bg, title="Couleur de fond")[1]
            if color:
                self.tmp_bg = color
                bg_btn.configure(text=color, bg=color, fg=self.tmp_fg)
                
        def pick_fg():
            color = colorchooser.askcolor(color=self.tmp_fg, title="Couleur du texte")[1]
            if color:
                self.tmp_fg = color
                fg_btn.configure(text=color, fg=color, bg=self.tmp_bg)

        tk.Label(col_frame, text="Fond:", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color).pack(side="left")
        bg_btn = tk.Button(col_frame, text=self.bg_color, width=8, font=("Courier", 9, "bold"), command=pick_bg, relief="ridge", borderwidth=3)
        bg_btn.configure(bg=self.bg_color, fg=self.fg_color)
        bg_btn.pack(side="left", padx=5)
        
        tk.Label(col_frame, text="Texte:", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(10,0))
        fg_btn = tk.Button(col_frame, text=self.fg_color, width=8, font=("Courier", 9, "bold"), command=pick_fg, relief="ridge", borderwidth=3)
        fg_btn.configure(bg=self.bg_color, fg=self.fg_color)
        fg_btn.pack(side="left", padx=5)"""

code = code.replace(orig_color_frame, new_color_frame)


orig_save = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            b = bg_entry.get().strip()
            f = fg_entry.get().strip()
            self.bg_color = b if b else "#000000"
            self.fg_color = f if f else "#33FF33"
            save_config(self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color)
            dialog.destroy()
            if hasattr(self, 'apply_theme'): self.apply_theme()
            self.reset_ui()"""

new_save = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            self.bg_color = getattr(self, 'tmp_bg', self.bg_color)
            self.fg_color = getattr(self, 'tmp_fg', self.fg_color)
            save_config(self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color)
            dialog.destroy()
            if hasattr(self, 'apply_theme'): self.apply_theme()
            self.reset_ui()"""
code = code.replace(orig_save, new_save)


with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Colors updated successfully")
