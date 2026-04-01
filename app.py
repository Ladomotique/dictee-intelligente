import customtkinter as ctk
import tkinter as tk
from tkinter import font
import threading
import sounddevice as sd
import numpy as np
import io
import wave
import queue
import keyboard
import pyperclip
import requests
import time
import sys
import winsound
import json
import os
import math
import struct

# 8-bit mode
# Retro

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MISTRAL_API_URL = "https://api.mistral.ai/v1/audio/transcriptions"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return (data.get("api_key", ""), data.get("sound_profile", "Classique"), 
                        data.get("hotkey", "alt+w"), data.get("bg_color", "#000000"), data.get("fg_color", "#33FF33"), data.get("context_bias", ""))
        except:
            pass
    return "", "Classique", "alt+w", "#000000", "#33FF33", ""

def save_config(api_key, sound_profile, hotkey, bg_color, fg_color, context_bias):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key, "sound_profile": sound_profile, "hotkey": hotkey, "bg_color": bg_color, "fg_color": fg_color, "context_bias": context_bias}, f)

def generate_wav_memory(notes, sample_rate=44100):
    if not notes:
        return None
    audio_data = bytearray()
    for freq, duration in notes:
        num_samples = int(sample_rate * (duration / 1000.0))
        for i in range(num_samples):
            t = float(i) / sample_rate
            sample = math.sin(2.0 * math.pi * freq * t)
            # Enveloppe douce : fade in très rapide, fade out exponentiel
            fade_in = min(1.0, i / (int(sample_rate * 0.005) + 1))
            fade_out = math.exp(-3.0 * (i / num_samples))
            sample = sample * fade_in * fade_out
            
            # Réduction du volume global pour un son "soft" (30%)
            val = int(sample * 32767 * 0.3)
            audio_data.extend(struct.pack("<h", val))
            
    # Entête WAV
    header = bytearray()
    header.extend(b"RIFF")
    header.extend(struct.pack("<I", 36 + len(audio_data)))
    header.extend(b"WAVE")
    header.extend(b"fmt ")
    header.extend(struct.pack("<I", 16))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<I", sample_rate))
    header.extend(struct.pack("<I", sample_rate * 2))
    header.extend(struct.pack("<H", 2))
    header.extend(struct.pack("<H", 16))
    header.extend(b"data")
    header.extend(struct.pack("<I", len(audio_data)))
    
    return bytes(header + audio_data)

# Profils sur mesure (Doux et précis, pas de bruits stridents Windows)
SOUND_PROFILES = {
    "Classique": ([(800, 150)], [(600, 150)]),
    "Goutte d'eau": ([(1200, 50)], [(1000, 50)]),
    "Bulle": ([(500, 40), (700, 40), (900, 60)], [(900, 40), (700, 40), (500, 60)]),
    "Robot": ([(300, 80), (400, 80), (500, 80)], [(500, 80), (400, 80), (300, 80)]),
    "Laser Rapide": ([(1500, 40), (1000, 40)], [(1000, 40), (1500, 40)]),
    "Cristallin": ([(1400, 100), (1800, 150)], [(1800, 100), (1400, 150)]),
    "Grave Doux": ([(300, 200)], [(250, 200)]),
    "Accord Joyeux": ([(523, 100), (659, 100), (784, 150)], [(1046, 200)]),
    "Clic Bref": ([(2000, 30), (100, 20)], [(100, 20), (2000, 30)]),
    "Silencieux": ([], [])
}

# ==========================================
# AUDIO RECORDER
# ==========================================
class Recorder:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.q = queue.Queue()
        self.recording = False
        self.stream = None
        self.audio_data = []

    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.q.put(indata.copy())

    def start(self):
        self.audio_data = []
        self.recording = True
        with self.q.mutex:
            self.q.queue.clear()
            
        self.stream = sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self.callback)
        self.stream.start()

    def stop(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        while not self.q.empty():
            self.audio_data.append(self.q.get())

        if len(self.audio_data) == 0:
            return None

        audio_concat = np.concatenate(self.audio_data, axis=0)
        
        if np.max(np.abs(audio_concat)) == 0:
            return None

        audio_concat = (audio_concat * 32767).astype(np.int16)

        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio_concat.tobytes())
            
        wav_io.seek(0)
        return wav_io

# ==========================================
# MAIN APPLICATION
# ==========================================
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(bg='#000000')
        self.root.title("Dictée Vocale Mistral")
        self.root.minsize(450, 650)
        self.root.geometry("450x650")
        self.root.attributes("-topmost", True)
        
        
        self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color, self.context_bias = load_config()
        if self.sound_profile not in SOUND_PROFILES:
            self.sound_profile = "Classique"
            
        self.recorder = Recorder()
        self.is_recording = False
        self.is_processing = False
        self.record_source = None
        self.record_start_time = 0
        self.is_compact = False
        
        # --- CONTAINERS ---
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True)
        
        self.mini_container = tk.Frame(self.root, bg=self.bg_color)
        
        # Draggable top bar for mini container
        self.mini_drag_bar = tk.Frame(self.mini_container, bg=self.fg_color, height=15, cursor="fleur")
        self.mini_drag_bar.pack(fill="x", side="top")
        
        # Add tiny "grab" visual in the center of the drag bar
        tk.Label(self.mini_drag_bar, text="======", bg=self.fg_color, fg=self.bg_color, font=("Courier", 8, "bold"), pady=0).pack()

        # Dragging logic
        self._offsetx = 0
        self._offsety = 0

        def click_window(event):
            self._offsetx = event.x
            self._offsety = event.y

        def drag_window(event):
            x = self.root.winfo_pointerx() - self._offsetx
            y = self.root.winfo_pointery() - self._offsety
            self.root.geometry(f"+{x}+{y}")

        self.mini_drag_bar.bind("<ButtonPress-1>", click_window)
        self.mini_drag_bar.bind("<B1-Motion>", drag_window)
        for child in self.mini_drag_bar.winfo_children():
            child.bind("<ButtonPress-1>", click_window)
            child.bind("<B1-Motion>", drag_window)

        self.mini_center_frame = tk.Frame(self.mini_container, bg=self.bg_color)
        self.mini_center_frame.pack(expand=True)
        
        self.mini_btn = tk.Button(self.mini_center_frame, text="🎤", font=("Courier", 18, "bold"), command=self.toggle_recording, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color, width=5, height=2)
        # Forcer le texte à être centré horizontalement et verticalement
        self.mini_btn.pack(pady=(0, 10))
        
        self.maximize_btn = tk.Button(self.mini_center_frame, text="▲ MAX", font=("Courier", 14), command=self.maximize_window, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color, width=7)
        self.maximize_btn.pack()

        # Thread d'écoute clavier global
        self.hook_thread = threading.Thread(target=self.monitor_hotkey, daemon=True)
        self.hook_thread.start()

        # --- MAIN UI SETUP ---
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Titre posé à gauche du bandeau
        title_label = tk.Label(header_frame, text="Dictée intelligente", font=("Courier", 18, "bold"), bg=self.bg_color, fg=self.fg_color)
        title_label.pack(side="left")
        
        self.settings_btn = tk.Button(header_frame, text="⚙️", width=3, font=("Courier", 14), command=self.open_settings, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.settings_btn.pack(side="right")
        
        self.minimize_btn = tk.Button(header_frame, text="➖", width=3, font=("Courier", 14), command=self.minimize_window, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.minimize_btn.pack(side="right", padx=5)
        
        self.label = tk.Label(self.main_container, text=f"Cliquez pour dicter\n(Ou maintenez {self.hotkey.upper()} n'importe où)", font=("Courier", 11), bg=self.bg_color, fg="#00AA00")
        self.label.pack(pady=5)

        self.btn = tk.Button(self.main_container, text="🎤 Appuyez et parlez", font=("Courier", 14, "bold"), command=self.toggle_recording, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color, pady=10)
        self.btn.pack(pady=15, padx=30, fill="x")

        # History Frame
        history_label = tk.Label(self.main_container, text="DERN. TRANSCRIPTIONS", font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color)
        history_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.history_frame = tk.Frame(self.main_container, bg=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color)
        self.history_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.history = []

    def update_history_ui(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.history):
            frame = tk.Frame(self.history_frame, bg=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color)
            frame.pack(fill="x", pady=6, padx=5)
            
            if isinstance(item, dict) and item.get("type") == "error":
                frame.configure(bg=self.bg_color)
                
                error_label = tk.Label(frame, text="⚠️ " + item.get("error_msg", ""), font=("Courier", 10), bg=self.bg_color, fg="#FF3333", justify="left", wraplength=250)
                error_label.pack(side="left", fill="both", expand=True, padx=15, pady=15)
                
                btn_retry = tk.Button(frame, text="RETRY", width=5, font=("Courier", 14), command=lambda b=item.get("audio_bytes"), i=item: self.retry_transcription(b, i), bg=self.bg_color, fg="#FF3333", activebackground="#FF3333", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
                btn_retry.pack(side="right", padx=10, pady=10)
            else:
                text_val = item.get("text", "") if isinstance(item, dict) else item
                btn_copy = tk.Button(frame, text="📋", width=3, font=("Courier", 14), command=lambda t=text_val: pyperclip.copy(t), bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
                btn_copy.pack(side="right", padx=10, pady=10)
                
                txt_box = tk.Text(frame, height=3, wrap="word", font=("Courier", 10), bg=self.bg_color, fg=self.fg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
                txt_box.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                txt_box.insert("1.0", text_val)
                txt_box.configure(state="disabled") # Lecture seule

    def open_settings(self):
        dialog = tk.Frame(self.root, bg=self.bg_color, relief="ridge", borderwidth=5, highlightthickness=2, highlightbackground=self.fg_color)
        dialog.place(relx=0.5, rely=0.5, anchor="center", width=420, height=580)
        
        def save():
            self.api_key = api_entry.get().strip()
            self.sound_profile = sound_var.get()
            self.bg_color = getattr(self, 'tmp_bg', self.bg_color)
            self.fg_color = getattr(self, 'tmp_fg', self.fg_color)
            if hasattr(self, 'tmp_hk'): self.hotkey = self.tmp_hk
            self.context_bias = bias_text.get("1.0", tk.END).strip()
            save_config(self.api_key, self.sound_profile, self.hotkey, self.bg_color, self.fg_color, self.context_bias)
            dialog.destroy()
            if hasattr(self, 'apply_theme'): self.apply_theme()
            self.reset_ui()
            
        def close_dialog():
            save()

        # Close 'X' Button
        tk.Button(dialog, text="X", command=close_dialog, bg=self.bg_color, fg=self.fg_color, font=("Courier", 14, "bold"), relief="flat", activebackground=self.fg_color, activeforeground=self.bg_color).place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne", width=30, height=30)

        # Fixed Save Button at the Bottom
        save_btn_frame = tk.Frame(dialog, bg=self.bg_color)
        save_btn_frame.pack(side="bottom", fill="x", pady=10)
        tk.Button(save_btn_frame, text="SAUVEGARDER", command=save, width=25, font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color).pack(pady=10)

        # scrollable canvas
        canvas = tk.Canvas(dialog, bg=self.bg_color, highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
            
        canvas.bind("<Configure>", configure_canvas_width)
        
        canvas.pack(side="top", fill="both", expand=True, pady=(40, 5), padx=(5, 5))
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            
        dialog.bind("<Enter>", bind_mousewheel)
        dialog.bind("<Leave>", unbind_mousewheel)

        # Titre
        tk.Label(scrollable_frame, text="--- PARAMETRES ---", font=("Courier", 14, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))
        
        # 1. Mots personnalisés (Context Bias)
        tk.Label(scrollable_frame, text="Mots personnalisés (Context Bias):", font=("Courier", 11), bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))
        tk.Label(scrollable_frame, text="(Séparés par des virgules, max 100)", font=("Courier", 9), bg=self.bg_color, fg=self.fg_color).pack(pady=(0, 5))
        bias_text = tk.Text(scrollable_frame, height=4, width=35, font=("Courier", 10), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color, wrap="word")
        bias_text.pack(pady=5, padx=20)
        if self.context_bias:
            bias_text.insert("1.0", self.context_bias)
            
        # 2. Clé API
        tk.Label(scrollable_frame, text="Clé API Mistral:", font=("Courier", 11), bg=self.bg_color, fg=self.fg_color).pack(pady=(15, 5))
        api_entry = tk.Entry(scrollable_frame, width=30, font=("Courier", 11), bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        api_entry.pack(pady=5)
        api_entry.insert(0, self.api_key)
        
        # 3. Raccourci Clavier
        tk.Label(scrollable_frame, text="Raccourci Clavier:", font=("Courier", 11), bg=self.bg_color, fg=self.fg_color).pack(pady=(15, 5))
        hk_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        hk_frame.pack(pady=5)
        
        hk_btn = tk.Button(hk_frame, text=self.hotkey, width=15, font=("Courier", 10, "bold"), bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3)
        hk_btn.pack(side="left", padx=5)
        
        self.capturing = False
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
            threading.Thread(target=wait_for_key, daemon=True).start()
            
        tk.Button(hk_frame, text="EDITE", width=6, font=("Courier", 10), command=capture_hk, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3).pack(side="left")

        # 4. Profil Sonore
        tk.Label(scrollable_frame, text="Profil Sonore:", font=("Courier", 11), bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 5))
        
        sound_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        sound_frame.pack(pady=5)
        
        sound_var = tk.StringVar(value=self.sound_profile)
        sound_menu = tk.OptionMenu(sound_frame, sound_var, *list(SOUND_PROFILES.keys()))
        sound_menu.configure(bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, font=("Courier", 10))
        sound_menu.pack(side="left", padx=(0, 10))
        
        def preview_sound():
            def run_preview():
                selected = sound_var.get()
                profile = SOUND_PROFILES.get(selected)
                if profile:
                    wav_start = generate_wav_memory(profile[0])
                    wav_stop = generate_wav_memory(profile[1])
                    if wav_start:
                        winsound.PlaySound(wav_start, winsound.SND_MEMORY | winsound.SND_NODEFAULT)
                    time.sleep(0.3)
                    if wav_stop:
                        winsound.PlaySound(wav_stop, winsound.SND_MEMORY | winsound.SND_NODEFAULT)
            threading.Thread(target=run_preview, daemon=True).start()
            
        btn_play = tk.Button(sound_frame, text="PLAY", width=4, font=("Courier", 14), command=preview_sound, bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        btn_play.pack(side="left")
        

        # Colors Setting
        tk.Label(scrollable_frame, text="- COULEURS -", font=("Courier", 11, "bold"), bg=self.bg_color, fg=self.fg_color).pack(pady=(20, 5))
        col_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
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
        fg_btn.pack(side="left", padx=5)



    def monitor_hotkey(self):
        hotkey_was_pressed = False
        while True:
            try:
                is_pressed = keyboard.is_pressed(self.hotkey) if getattr(self, 'hotkey', None) else False
                if is_pressed and not hotkey_was_pressed:
                    hotkey_was_pressed = True
                    if not self.is_recording and not self.is_processing:
                        self.root.after(0, lambda: self.start_recording("hotkey"))
                elif not is_pressed and hotkey_was_pressed:
                    hotkey_was_pressed = False
                    if self.is_recording and self.record_source == "hotkey":
                        self.root.after(0, lambda: self.stop_recording("hotkey"))
            except Exception:
                pass
            time.sleep(0.02)

    def toggle_recording(self):
        if not self.is_processing:
            if not self.is_recording:
                self.start_recording("button")
            else:
                self.stop_recording("button")

    def update_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.record_start_time)
            self.btn.configure(text=f"🔴 Arrêter l'enregistrement ({elapsed}s)")
            self.mini_btn.configure(text=f"🔴\n{elapsed}s")
            self.root.after(1000, self.update_timer)

    def play_sound_profile(self, state):
        profile = SOUND_PROFILES.get(self.sound_profile, SOUND_PROFILES["Classique"])
        notes = profile[0] if state == "start" else profile[1]
        
        wav_bytes = generate_wav_memory(notes)
        if wav_bytes:
            winsound.PlaySound(wav_bytes, winsound.SND_MEMORY | winsound.SND_NODEFAULT)

    def start_recording(self, source):
        if self.is_recording:
            return
            
        if not self.api_key:
            self.open_settings()
            return
            
        self.record_source = source
        self.is_recording = True
        self.record_start_time = time.time()
        
        threading.Thread(target=self.play_sound_profile, args=("start",), daemon=True).start()
        
        self.btn.configure(text="🔴 0s", bg=self.bg_color, fg="#FF3333", activebackground="#FF3333", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.mini_btn.configure(text="🔴\n0s", bg=self.bg_color, fg="#FF3333", activebackground="#FF3333", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.label.configure(text="Enregistrement en cours...")
        self.recorder.start()
        self.update_timer()

    def stop_recording(self, source):
        if not self.is_recording:
            return
            
        # Ignore release if the other source started it
        if source == "hotkey" and self.record_source == "button":
            return
            
        self.is_recording = False
        
        threading.Thread(target=self.play_sound_profile, args=("stop",), daemon=True).start()
        
        self.btn.configure(text="⏳ Mistral...", state="disabled", bg=self.bg_color, fg="#FFA500", activebackground="#FFA500", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.mini_btn.configure(text="⏳", state="disabled", bg=self.bg_color, fg="#FFA500", activebackground="#FFA500", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.label.configure(text="Envoi en cours...")
        self.is_processing = True
        
        wav_io = self.recorder.stop()
        
        if wav_io is not None:
            wav_bytes = wav_io.read()
            threading.Thread(target=self.transcribe_and_paste, args=(wav_bytes,), daemon=True).start()
        else:
            self.reset_ui()

    def transcribe_and_paste(self, wav_bytes):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            files = {
                "file": ("audio.wav", wav_bytes, "audio/wav")
            }
            
            data = {
                "model": "voxtral-mini-latest" 
            }
            if self.context_bias:
                # Nettoyage et formatage du context_bias comme exigé par l'API :
                # - Pas d'espaces (remplacés par des underscores `_`)
                # - Séparés par des virgules
                # - Pas d'éléments vides
                mots_bruts = self.context_bias.replace('\n', ',').split(',')
                mots_propres = []
                for mot in mots_bruts:
                    mot = mot.strip()
                    if mot:
                        mot = mot.replace(' ', '_')
                        mots_propres.append(mot)
                
                if mots_propres:
                    data["context_bias"] = ",".join(mots_propres)

            # Timeout de 15 sec pour éviter un freeze
            response = requests.post(MISTRAL_API_URL, headers=headers, files=files, data=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "")
                
                if text:
                    pyperclip.copy(text)
                    self.add_to_history({"type": "success", "text": text})
                    
                    while keyboard.is_pressed('alt') or keyboard.is_pressed('ctrl') or keyboard.is_pressed('shift'):
                        time.sleep(0.05)
                        
                    keyboard.send("ctrl+v")
            else:
                error_msg = f"Erreur API ({response.status_code}): {response.text}"
                print(error_msg)
                self.add_to_history({"type": "error", "error_msg": error_msg, "audio_bytes": wav_bytes})

        except requests.exceptions.Timeout:
            error_msg = "Erreur: Le serveur Mistral est trop long à répondre (Timeout)."
            print(error_msg)
            self.add_to_history({"type": "error", "error_msg": error_msg, "audio_bytes": wav_bytes})
        except Exception as e:
            error_msg = f"Erreur lors de la connexion : {e}"
            print(error_msg)
            self.add_to_history({"type": "error", "error_msg": error_msg, "audio_bytes": wav_bytes})

        finally:
            self.root.after(0, self.reset_ui)

    def add_to_history(self, item):
        self.history.insert(0, item)
        if len(self.history) > 10:
            self.history.pop()
        self.root.after(0, self.update_history_ui)

    def retry_transcription(self, wav_bytes, item):
        try:
            self.history.remove(item)
            self.update_history_ui()
        except ValueError:
            pass
            
        self.btn.configure(text="⏳ Essai...", state="disabled", bg=self.bg_color, fg="#FFA500", activebackground="#FFA500", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.mini_btn.configure(text="⏳", state="disabled", bg=self.bg_color, fg="#FFA500", activebackground="#FFA500", activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.label.configure(text="Renvoi à Mistral...")
        self.is_processing = True
        
        threading.Thread(target=self.transcribe_and_paste, args=(wav_bytes,), daemon=True).start()

    def reset_ui(self):
        self.is_processing = False
        self.btn.configure(text="🎤 Appuyez et parlez", state="normal", bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.mini_btn.configure(text="🎤", state="normal", bg=self.bg_color, fg=self.fg_color, activebackground=self.fg_color, activeforeground=self.bg_color, relief="ridge", borderwidth=3, highlightthickness=2, highlightbackground=self.bg_color, highlightcolor=self.fg_color)
        self.label.configure(text=f"Cliquez pour dicter\n(Ou maintenez {self.hotkey.upper()} n'importe où)")

    def apply_theme(self):
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

    def minimize_window(self):
        self.is_compact = True
        self.main_container.pack_forget()
        self.root.minsize(0, 0)
        self.root.geometry("160x200")
        self.mini_container.pack(fill="both", expand=True)

    def maximize_window(self):
        self.is_compact = False
        self.mini_container.pack_forget()
        self.root.minsize(450, 650)
        self.root.geometry("450x650")
        self.main_container.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.root.mainloop()
