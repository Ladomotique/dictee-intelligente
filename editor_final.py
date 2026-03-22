import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Lock resizing
orig_init_geometry = """        self.root.geometry("450x650")
        self.root.attributes("-topmost", True)"""
new_init_geometry = """        self.root.geometry("450x650")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)"""
code = code.replace(orig_init_geometry, new_init_geometry)


# 2. Fix Hotkey capture
orig_capture = """        self.capturing = False
        def capture_hk():
            self.capturing = True
            hk_btn.configure(text="Appuyez...", fg="#FF3333")
            def wait_for_key():
                hk = keyboard.read_hotkey(suppress=False)
                self.hotkey = hk
                hk_btn.configure(text=self.hotkey, fg=self.fg_color)
                self.capturing = False
            import threading
            threading.Thread(target=wait_for_key, daemon=True).start()"""
new_capture = """        self.capturing = False
        self.tmp_hk = getattr(self, "hotkey", "alt+w")
        def capture_hk():
            self.capturing = True
            hk_btn.configure(text="Appuyez...", fg="#FF3333")
            def wait_for_key():
                hk = keyboard.read_hotkey(suppress=False)
                self.tmp_hk = hk
                hk_btn.configure(text=self.tmp_hk, fg=self.fg_color)
                self.capturing = False
            import threading
            threading.Thread(target=wait_for_key, daemon=True).start()"""
code = code.replace(orig_capture, new_capture)


# 3. Update save() to use tmp_hk and enlarge SAUVEGARDER button
orig_save_fn = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            self.bg_color = getattr(self, 'tmp_bg', self.bg_color)
            self.fg_color = getattr(self, 'tmp_fg', self.fg_color)
            save_config(self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color)
            dialog.destroy()
            if hasattr(self, 'apply_theme'): self.apply_theme()
            self.reset_ui()
            
        tk.Button(dialog, text="SAUVEGARDER", command=save, width=15, font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color).pack(pady=(15, 5))"""

new_save_fn = """        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            self.bg_color = getattr(self, 'tmp_bg', self.bg_color)
            self.fg_color = getattr(self, 'tmp_fg', self.fg_color)
            if hasattr(self, 'tmp_hk'): self.hotkey = self.tmp_hk
            save_config(self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color)
            dialog.destroy()
            if hasattr(self, 'apply_theme'): self.apply_theme()
            self.reset_ui()
            
        tk.Button(dialog, text="SAUVEGARDER", command=save, width=25, font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color).pack(pady=(20, 10))"""
code = code.replace(orig_save_fn, new_save_fn)


with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Final changes applied.")
