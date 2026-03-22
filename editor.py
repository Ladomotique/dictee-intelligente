import re
import os

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update load_config / save_config
orig_config = """def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("api_key", ""), data.get("sound_profile", "Classique")
        except:
            pass
    return "", "Classique"

def save_config(api_key, sound_profile):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key, "sound_profile": sound_profile}, f)"""

new_config = """def load_config():
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
code = code.replace(orig_config, new_config)

# 2. Update __init__ load
orig_init_load = """self.api_key, self.sound_profile = load_config()"""
new_init_load = """self.api_key, self.sound_profile, self.hotkey = load_config()"""
code = code.replace(orig_init_load, new_init_load)

# 3. Restore emojis for min and sys
code = code.replace('text="SYS"', 'text="⚙️"')
code = code.replace('text="MIN"', 'text="➖"')

# 4. Fix history layout & copy emoji
import_copy_block = r"""                txt_box = tk.Text\(frame, height=3, wrap="word", font=\("Courier", 10\), bg="#000000", fg="#33FF33", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white"\)\s+txt_box.pack\(side="left", fill="both", expand=True, padx=10, pady=10\)\s+txt_box.insert\("1.0", text_val\)\s+txt_box.configure\(state="disabled"\) # Lecture seule\s+btn_copy = tk.Button\(frame, text="COPIER", width=6, font=\("Courier", 14\), command=lambda t=text_val: pyperclip.copy\(t\), bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white"\)\s+btn_copy.pack\(side="right", padx=10, pady=10\)"""

new_copy_block = """                btn_copy = tk.Button(frame, text="📋", width=3, font=("Courier", 14), command=lambda t=text_val: pyperclip.copy(t), bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white")
                btn_copy.pack(side="right", padx=10, pady=10)
                
                txt_box = tk.Text(frame, height=3, wrap="word", font=("Courier", 10), bg="#000000", fg="#33FF33", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white")
                txt_box.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                txt_box.insert("1.0", text_val)
                txt_box.configure(state="disabled") # Lecture seule"""
code = re.sub(import_copy_block, new_copy_block, code)

# 5. Fix open_settings to Overlay and Add Hotkey
orig_settings = """    def open_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.configure(bg="#000000")
        dialog.title("Paramètres")
        dialog.geometry("400x260")
        dialog.attributes("-topmost", True)
        dialog.transient(self.root)
        dialog.grab_set()"""
new_settings = """    def open_settings(self):
        dialog = tk.Frame(self.root, bg="#000000", relief="ridge", borderwidth=5, highlightthickness=2, highlightbackground="#33FF33")
        dialog.place(relx=0.5, rely=0.5, anchor="center", width=380, height=320)
        
        # Titre
        tk.Label(dialog, text="--- PARAMETRES ---", font=("Courier", 14, "bold"), bg="#000000", fg="#33FF33").pack(pady=(10, 5))"""
code = code.replace(orig_settings, new_settings)

# Hotkey setting inside open_settings
orig_save_fn = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            save_config(self.api_key, self.sound_profile)
            dialog.destroy()
            
        tk.Button(dialog, text="SAUVEGARDER", command=save, width=15, font=("Courier", 14, "bold"), bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white").pack(pady=15)"""

new_save_fn = """        tk.Label(dialog, text="Raccourci Clavier:", font=("Courier", 11), bg="#000000", fg="#33FF33").pack(pady=(10, 5))
        hk_frame = tk.Frame(dialog, bg="#000000")
        hk_frame.pack(pady=5)
        
        hk_btn = tk.Button(hk_frame, text=self.hotkey, width=15, font=("Courier", 10, "bold"), bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3)
        hk_btn.pack(side="left", padx=5)
        
        self.capturing = False
        def capture_hk():
            self.capturing = True
            hk_btn.configure(text="Appuyez...", fg="#FF3333")
            def wait_for_key():
                hk = keyboard.read_hotkey(suppress=False)
                self.hotkey = hk
                hk_btn.configure(text=self.hotkey, fg="#33FF33")
                self.capturing = False
            import threading
            threading.Thread(target=wait_for_key, daemon=True).start()
            
        tk.Button(hk_frame, text="EDITE", width=6, font=("Courier", 10), command=capture_hk, bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3).pack(side="left")

        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            save_config(self.api_key, self.sound_profile, self.hotkey)
            dialog.destroy()
            
        tk.Button(dialog, text="SAUVEGARDER", command=save, width=15, font=("Courier", 14, "bold"), bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white").pack(pady=(15, 5))
        tk.Button(dialog, text="FERMER", command=dialog.destroy, width=15, font=("Courier", 10), bg="#000000", fg="#FF3333", activebackground="#FF3333", activeforeground="#000000", relief="ridge", borderwidth=3).pack(pady=5)"""
code = code.replace(orig_save_fn, new_save_fn)

# 6. Update monitor_hotkey
orig_hotkey_monitor = """    def monitor_hotkey(self):
        hotkey_was_pressed = False
        while True:
            try:
                is_pressed = keyboard.is_pressed("alt") and keyboard.is_pressed("w")
                if is_pressed and not hotkey_was_pressed:"""

new_hotkey_monitor = """    def monitor_hotkey(self):
        hotkey_was_pressed = False
        while True:
            try:
                is_pressed = keyboard.is_pressed(self.hotkey) if getattr(self, 'hotkey', None) else False
                if is_pressed and not hotkey_was_pressed:"""
code = code.replace(orig_hotkey_monitor, new_hotkey_monitor)


with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Editor script completed")
