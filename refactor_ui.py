import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add font import
code = code.replace("import tkinter as tk", "import tkinter as tk\nfrom tkinter import font")

# 2. Remove ctk set_appearance_mode
code = code.replace("ctk.set_appearance_mode(\"dark\")", "# 8-bit mode")
code = code.replace("ctk.set_default_color_theme(\"blue\")", "# Retro")

# Helper for standard tk button
tk_btn = 'bg="#000000", fg="#33FF33", activebackground="#33FF33", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white"'
tk_btn_red = 'bg="#000000", fg="#FF3333", activebackground="#FF3333", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white"'
tk_btn_orange = 'bg="#000000", fg="#FFA500", activebackground="#FFA500", activeforeground="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black", highlightcolor="white"'
tk_frame = 'bg="#000000", relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground="black"'
tk_frame_noborder = 'bg="#000000"'
tk_label = 'bg="#000000", fg="#33FF33"'
font_h1 = 'font=("Courier", 18, "bold")'
font_h2 = 'font=("Courier", 14, "bold")'
font_p = 'font=("Courier", 11)'
font_btn = 'font=("Courier", 14)'
font_small = 'font=("Courier", 10)'

# 3. Replace __init__ UI
init_replacements = [
    ("self.root = ctk.CTk()", f"self.root = tk.Tk()\n        self.root.configure(bg='#000000')"),
    ("ctk.CTkFrame(self.root, fg_color=\"transparent\")", f"tk.Frame(self.root, {tk_frame_noborder})"),
    ("ctk.CTkFrame(self.main_container, fg_color=\"transparent\")", f"tk.Frame(self.main_container, {tk_frame_noborder})"),
    ("ctk.CTkLabel(header_frame, text=\"Dictée intelligente\", font=(\"Segoe UI\", 18, \"bold\"))", f"tk.Label(header_frame, text=\"Dictée intelligente\", {font_h1}, {tk_label})"),
    ("ctk.CTkButton(header_frame, text=\"⚙️\", width=40, height=40, font=(\"Segoe UI\", 16),\n                                          fg_color=\"transparent\", hover_color=\"#3b3b3b\", command=self.open_settings)", f"tk.Button(header_frame, text=\"⚙️\", width=3, {font_btn}, command=self.open_settings, {tk_btn})"),
    ("ctk.CTkButton(header_frame, text=\"➖\", width=40, height=40, font=(\"Segoe UI\", 16),\n                                          fg_color=\"transparent\", hover_color=\"#3b3b3b\", command=self.minimize_window)", f"tk.Button(header_frame, text=\"➖\", width=3, {font_btn}, command=self.minimize_window, {tk_btn})"),
    ("ctk.CTkLabel(self.main_container, text=\"Cliquez pour dicter\\n(Ou maintenez Alt+W n'importe où)\", font=(\"Segoe UI\", 13), text_color=\"gray\")", f"tk.Label(self.main_container, text=\"Cliquez pour dicter\\n(Ou maintenez Alt+W n'importe où)\", {font_p}, bg=\"#000000\", fg=\"#00AA00\")"),
    ("ctk.CTkButton(self.main_container, text=\"🎤 Appuyez et parlez\", font=(\"Segoe UI\", 16, \"bold\"),\n                                 fg_color=\"#2ecc71\", hover_color=\"#27ae60\", height=60, corner_radius=30,\n                                 command=self.toggle_recording)", f"tk.Button(self.main_container, text=\"🎤 Appuyez et parlez\", {font_h2}, command=self.toggle_recording, {tk_btn}, pady=10)"),
    ("ctk.CTkLabel(self.main_container, text=\"Dernières transcriptions\", font=(\"Segoe UI\", 14, \"bold\"))", f"tk.Label(self.main_container, text=\"DERN. TRANSCRIPTIONS\", {font_h2}, {tk_label})"),
    ("ctk.CTkScrollableFrame(self.main_container, fg_color=\"transparent\")", f"tk.Frame(self.main_container, {tk_frame})"),
    ("self.mini_btn = ctk.CTkButton(self.mini_center_frame, text=\"🎤\", font=(\"Segoe UI\", 24),\n                                      fg_color=\"#2ecc71\", hover_color=\"#27ae60\", width=80, height=80, corner_radius=40,\n                                      command=self.toggle_recording)", f"self.mini_btn = tk.Button(self.mini_center_frame, text=\"🎤\", {font_h1}, command=self.toggle_recording, {tk_btn}, width=5, height=2)"),
    ("self.mini_btn._text_label.configure(justify=\"center\")\n", ""),
    ("ctk.CTkButton(self.mini_center_frame, text=\"➕\", font=(\"Segoe UI\", 16), width=40,\n                                          fg_color=\"transparent\", hover_color=\"#3b3b3b\", height=20, command=self.maximize_window)", f"tk.Button(self.mini_center_frame, text=\"➕\", {font_btn}, command=self.maximize_window, {tk_btn}, width=3)"),
    ("self.mini_center_frame = ctk.CTkFrame(self.mini_container, fg_color=\"transparent\")", f"tk.Frame(self.mini_container, {tk_frame_noborder})"),
]

for src, dst in init_replacements:
    code = code.replace(src, dst)

# 4. update_history_ui
code = code.replace("ctk.CTkFrame(self.history_frame, corner_radius=12, fg_color=(\"#f0f0f0\", \"#2b2b2b\"))", f"tk.Frame(self.history_frame, {tk_frame})")
code = code.replace("frame.configure(fg_color=\"#4a1515\") # Rouge foncé pour erreur", f"frame.configure(bg=\"#000000\")")
code = code.replace("ctk.CTkLabel(frame, text=\"⚠️ \" + item.get(\"error_msg\", \"\"), text_color=\"#ff8a80\", font=(\"Segoe UI\", 12), justify=\"left\", wraplength=250)", f"tk.Label(frame, text=\"⚠️ \" + item.get(\"error_msg\", \"\"), {font_small}, bg=\"#000000\", fg=\"#FF3333\", justify=\"left\", wraplength=250)")
code = code.replace("ctk.CTkButton(frame, text=\"🔄\", width=40, height=40, font=(\"Segoe UI\", 16), fg_color=\"#d32f2f\", hover_color=\"#b71c1c\", corner_radius=8,\n                                         command=lambda b=item.get(\"audio_bytes\"), i=item: self.retry_transcription(b, i))", f"tk.Button(frame, text=\"🔄\", width=3, {font_btn}, command=lambda b=item.get(\"audio_bytes\"), i=item: self.retry_transcription(b, i), {tk_btn_red})")
code = code.replace("ctk.CTkTextbox(frame, height=70, wrap=\"word\", font=(\"Segoe UI\", 13), fg_color=\"transparent\", border_spacing=0)", f"tk.Text(frame, height=3, wrap=\"word\", {font_small}, {tk_label}, relief=\"ridge\", borderwidth=3, highlightthickness=2, highlightbackground=\"black\", highlightcolor=\"white\")")
code = code.replace("ctk.CTkButton(frame, text=\"📋\", width=40, height=40, font=(\"Segoe UI\", 18), fg_color=\"transparent\", text_color=(\"black\", \"white\"), hover_color=(\"#e0e0e0\", \"#3b3b3b\"),\n                                         command=lambda t=text_val: pyperclip.copy(t))", f"tk.Button(frame, text=\"📋\", width=3, {font_btn}, command=lambda t=text_val: pyperclip.copy(t), {tk_btn})")

# 5. open_settings
code = code.replace("ctk.CTkToplevel(self.root)", "tk.Toplevel(self.root)\n        dialog.configure(bg=\"#000000\")")
code = code.replace("ctk.CTkLabel(dialog, text=\"Clé API Mistral:\", font=(\"Segoe UI\", 12, \"bold\"))", f"tk.Label(dialog, text=\"Clé API Mistral:\", {font_p}, {tk_label})")
code = code.replace("ctk.CTkEntry(dialog, width=320)", f"tk.Entry(dialog, width=30, {font_p}, {tk_label}, insertbackground=\"#33FF33\", relief=\"ridge\", borderwidth=3, highlightthickness=2, highlightbackground=\"black\", highlightcolor=\"white\")")
code = code.replace("ctk.CTkLabel(dialog, text=\"Profil Sonore:\", font=(\"Segoe UI\", 12, \"bold\"))", f"tk.Label(dialog, text=\"Profil Sonore:\", {font_p}, {tk_label})")
code = code.replace("ctk.CTkFrame(dialog, fg_color=\"transparent\")", f"tk.Frame(dialog, {tk_frame_noborder})")
code = code.replace("ctk.StringVar(value=self.sound_profile)", "tk.StringVar(value=self.sound_profile)")
code = code.replace("ctk.CTkOptionMenu(sound_frame, values=list(SOUND_PROFILES.keys()), variable=sound_var, width=160)", f"tk.OptionMenu(sound_frame, sound_var, *list(SOUND_PROFILES.keys()))")
code = code.replace("sound_menu.pack(side=\"left\", padx=(0, 10))", "sound_menu.configure(bg=\"#000000\", fg=\"#33FF33\", activebackground=\"#33FF33\", activeforeground=\"#000000\", relief=\"ridge\", borderwidth=3, highlightthickness=2, font=(\"Courier\", 10))\n        sound_menu.pack(side=\"left\", padx=(0, 10))")
code = code.replace("ctk.CTkButton(sound_frame, text=\"▶️\", width=40, font=(\"Segoe UI\", 16), fg_color=\"#3498db\", hover_color=\"#2980b9\", command=preview_sound)", f"tk.Button(sound_frame, text=\"▶️\", width=3, {font_btn}, command=preview_sound, {tk_btn})")
code = code.replace("ctk.CTkButton(dialog, text=\"Sauvegarder\", command=save, width=150, fg_color=\"#2ecc71\", hover_color=\"#27ae60\")", f"tk.Button(dialog, text=\"SAUVEGARDER\", command=save, width=15, {font_h2}, {tk_btn})")

# 6. Button configuring in actions
# start_recording
code = code.replace("self.btn.configure(text=\"🔴 0s\", fg_color=\"#e74c3c\", hover_color=\"#c0392b\")", f"self.btn.configure(text=\"🔴 0s\", {tk_btn_red})")
code = code.replace("self.mini_btn.configure(text=\"🔴\\n0s\", font=(\"Segoe UI\", 18, \"bold\"), fg_color=\"#e74c3c\", hover_color=\"#c0392b\")", f"self.mini_btn.configure(text=\"🔴\\n0s\", {tk_btn_red})")
# update_timer
code = code.replace("self.mini_btn.configure(text=f\"🔴\\n{elapsed}s\", font=(\"Segoe UI\", 18, \"bold\"))", f"self.mini_btn.configure(text=f\"🔴\\n{{elapsed}}s\")")
# stop_recording
code = code.replace("self.btn.configure(text=\"⏳ Traitement par Mistral...\", fg_color=\"#f39c12\", hover_color=\"#d68910\", state=\"disabled\")", f"self.btn.configure(text=\"⏳ Mistral...\", state=\"disabled\", {tk_btn_orange})")
code = code.replace("self.mini_btn.configure(text=\"⏳\", font=(\"Segoe UI\", 18), fg_color=\"#f39c12\", hover_color=\"#d68910\", state=\"disabled\")", f"self.mini_btn.configure(text=\"⏳\", state=\"disabled\", {tk_btn_orange})")
# retry
code = code.replace("self.btn.configure(text=\"⏳ Nouvel essai...\", fg_color=\"#f39c12\", hover_color=\"#d68910\", state=\"disabled\")", f"self.btn.configure(text=\"⏳ Essai...\", state=\"disabled\", {tk_btn_orange})")
code = code.replace("self.mini_btn.configure(text=\"⏳\", font=(\"Segoe UI\", 18), fg_color=\"#f39c12\", hover_color=\"#d68910\", state=\"disabled\")", f"self.mini_btn.configure(text=\"⏳\", state=\"disabled\", {tk_btn_orange})")
# reset_ui
code = code.replace("self.btn.configure(text=\"🎤 Appuyez et parlez\", fg_color=\"#2ecc71\", hover_color=\"#27ae60\", state=\"normal\")", f"self.btn.configure(text=\"🎤 Appuyez et parlez\", state=\"normal\", {tk_btn})")
code = code.replace("self.mini_btn.configure(text=\"🎤\", font=(\"Segoe UI\", 24), fg_color=\"#2ecc71\", hover_color=\"#27ae60\", state=\"normal\")", f"self.mini_btn.configure(text=\"🎤\", state=\"normal\", {tk_btn})")

# Ensure app runs
with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)
