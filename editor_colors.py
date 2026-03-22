import re
import json

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update load/save config to support bg_color and fg_color
orig_config = """def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("api_key", ""), data.get("sound_profile", "Classique"), data.get("hotkey", "alt+w")
        except:
            pass
    return "", "Classique", "alt+w"

def save_config(api_key, sound_profile, hotkey):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key, "sound_profile": sound_profile, "hotkey": hotkey}, f)"""

new_config = """def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return (data.get("api_key", ""), data.get("sound_profile", "Classique"), 
                        data.get("hotkey", "alt+w"), data.get("bg_color", "#000000"), data.get("fg_color", "#33FF33"))
        except:
            pass
    return "", "Classique", "alt+w", "#000000", "#33FF33"

def save_config(api_key, sound_profile, hotkey, bg_color, fg_color):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key, "sound_profile": sound_profile, "hotkey": hotkey, "bg_color": bg_color, "fg_color": fg_color}, f)"""
code = code.replace(orig_config, new_config)


# 2. Update __init__ load
orig_init_load = """self.api_key, self.sound_profile, self.hotkey = load_config()"""
new_init_load = """self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color = load_config()"""
code = code.replace(orig_init_load, new_init_load)


# 3. Add X close button + Color settings
orig_settings_top = """    def open_settings(self):
        dialog = tk.Frame(self.root, bg="#000000", relief="ridge", borderwidth=5, highlightthickness=2, highlightbackground="#33FF33")
        dialog.place(relx=0.5, rely=0.5, anchor="center", width=380, height=320)
        
        # Titre
        tk.Label(dialog, text="--- PARAMETRES ---", font=("Courier", 14, "bold"), bg="#000000", fg="#33FF33").pack(pady=(10, 5))"""

new_settings_top = """    def open_settings(self):
        dialog = tk.Frame(self.root, bg=self.bg_color, relief="ridge", borderwidth=5, highlightthickness=2, highlightbackground=self.fg_color)
        dialog.place(relx=0.5, rely=0.5, anchor="center", width=420, height=420)
        
        # Close 'X' Button
        tk.Button(dialog, text="X", command=dialog.destroy, bg=self.bg_color, fg=self.fg_color, font=("Courier", 14, "bold"), relief="flat", activebackground=self.fg_color, activeforeground=self.bg_color).place(x=380, y=5, width=30, height=30)

        # Titre
        tk.Label(dialog, text="--- PARAMETRES ---", font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))"""
code = code.replace(orig_settings_top, new_settings_top)

orig_hotkey_frame = """        tk.Label(dialog, text="Raccourci Clavier:", font=("Courier", 11), bg="#000000", fg="#33FF33").pack(pady=(10, 5))"""
new_hotkey_frame = """
        # Colors Setting
        col_frame = tk.Frame(dialog, bg=self.bg_color)
        col_frame.pack(pady=5)
        
        tk.Label(col_frame, text="Fond:", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color).pack(side="left")
        bg_entry = tk.Entry(col_frame, width=8, font=("Courier", 10), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, relief="ridge", borderwidth=3)
        bg_entry.pack(side="left", padx=5)
        bg_entry.insert(0, self.bg_color)
        
        tk.Label(col_frame, text="Texte:", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(10,0))
        fg_entry = tk.Entry(col_frame, width=8, font=("Courier", 10), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, relief="ridge", borderwidth=3)
        fg_entry.pack(side="left", padx=5)
        fg_entry.insert(0, self.fg_color)

        tk.Label(dialog, text="Raccourci Clavier:", font=("Courier", 11), bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))"""
code = code.replace(orig_hotkey_frame, new_hotkey_frame)


orig_save = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            save_config(self.api_key, self.sound_profile, self.hotkey)
            dialog.destroy()
            
        tk.Button(dialog, text="SAUVEGARDER", command=save, width=15, font=("Courier", 14, "bold"), bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white").pack(pady=(15, 5))
        tk.Button(dialog, text="FERMER", command=dialog.destroy, width=15, font=("Courier", 10), bg="#000000", fg="#FF3333", activebackground="#FF3333", activeforeground="#000000", relief="ridge", borderwidth=3).pack(pady=5)"""

new_save = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            b = bg_entry.get().strip()
            f = fg_entry.get().strip()
            self.bg_color = b if b else "#000000"
            self.fg_color = f if f else "#33FF33"
            save_config(self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color)
            dialog.destroy()
            if hasattr(self, 'apply_theme'): self.apply_theme()
            self.reset_ui()
            
        tk.Button(dialog, text="SAUVEGARDER", command=save, width=15, font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color).pack(pady=(15, 5))"""
code = code.replace(orig_save, new_save)


# 4. Update the reset_ui label and add apply_theme
orig_reset = """    def reset_ui(self):
        self.is_processing = False
        self.btn.configure(text="🎤 Appuyez et parlez", state="normal", bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white")
        self.mini_btn.configure(text="🎤", state="normal", bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white", width=5, height=2)
        self.label.configure(text="Cliquez pour dicter\\n(Ou maintenez Alt+W n'importe où)")"""

new_reset = """    def reset_ui(self):
        self.is_processing = False
        self.btn.configure(text="🎤 Appuyez et parlez", state="normal", bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.mini_btn.configure(text="🎤", state="normal", bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.label.configure(text=f"Cliquez pour dicter\\n(Ou maintenez {self.hotkey.upper()} n'importe où)")

    def apply_theme(self):
        def set_colors(widget):
            try:
                # Ne pas changer les labels/boutons d'erreur ou rouges specifiquement
                if isinstance(widget, tk.Button) and (widget.cget("text") == "🔴 0s"): return
                if isinstance(widget, tk.Button) and widget.cget("fg") == "#FF3333": return
                if isinstance(widget, tk.Label) and widget.cget("fg") == "#FF3333": return
                
                widget.configure(bg=self.bg_color)
            except: pass
            
            try:
                if not (isinstance(widget, tk.Button) and widget.cget("fg") == "#FF3333") and not (isinstance(widget, tk.Label) and widget.cget("fg") == "#FF3333"):
                    widget.configure(fg=self.fg_color)
                
                if isinstance(widget, tk.Button):
                    if widget.cget("fg") != "#FF3333":
                        widget.configure(activebackground=self.fg_color, activeforeground=self.bg_color, highlightbackground=self.bg_color)
                
                if isinstance(widget, tk.Text) or isinstance(widget, tk.Entry):
                    widget.configure(insertbackground=self.fg_color, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
                
                if isinstance(widget, tk.Frame):
                    widget.configure(highlightbackground=self.bg_color)
            except: pass
            
            for child in widget.winfo_children():
                set_colors(child)
        set_colors(self.root)"""

code = code.replace(orig_reset, new_reset)

# 5. Fix remaining hardcoded string assignments to use self.bg_color properly at init time
code = code.replace('bg="#000000"', 'bg=self.bg_color')
code = code.replace('fg="#33FF33"', 'fg=self.fg_color')
code = code.replace('activebackground="#33FF33"', 'activebackground=self.fg_color')
code = code.replace('activeforeground="#000000"', 'activeforeground=self.bg_color')
code = code.replace('highlightbackground="black"', 'highlightbackground=self.bg_color')
code = code.replace('highlightcolor="white"', 'highlightcolor=self.fg_color')
code = code.replace('insertbackground="#33FF33"', 'insertbackground=self.fg_color')


with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Colors and Overlay X updated.")
