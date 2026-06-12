import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import time

# =========================================================
# CONFIGURAÇÃO INICIAL
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================================================
# JANELA PRINCIPAL
# =========================================================

app = ctk.CTk()
app.title("IA Local Interface")
app.geometry("1200x700")

# =========================================================
# FUNÇÕES
# =========================================================

def enviar_prompt():
    prompt = entrada_prompt.get("1.0", "end").strip()

    if not prompt:
        return

    chat_box.insert("end", f"\n🧑 Você:\n{prompt}\n")
    entrada_prompt.delete("1.0", "end")

    progresso.set(0)
    status_label.configure(text="Processando...")

    # Thread separada para não travar a interface
    threading.Thread(
        target=simular_ia,
        args=(prompt,),
        daemon=True
    ).start()


def simular_ia(prompt):
    for i in range(101):
        progresso.set(i / 100)
        time.sleep(0.02)

    resposta = f"Resposta simulada para:\n'{prompt}'"

    chat_box.insert("end", f"\n🤖 IA:\n{resposta}\n")
    chat_box.see("end")

    status_label.configure(text="Pronto")


def escolher_arquivo():
    arquivo = filedialog.askopenfilename()

    if arquivo:
        status_label.configure(text=f"Arquivo: {arquivo}")


def alterar_tema(valor):
    ctk.set_appearance_mode(valor.lower())


# =========================================================
# LAYOUT PRINCIPAL
# =========================================================

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# =========================================================
# SIDEBAR
# =========================================================

sidebar = ctk.CTkFrame(app, width=220, corner_radius=0)
sidebar.grid(row=0, column=0, sticky="nsw")

titulo = ctk.CTkLabel(
    sidebar,
    text="IA LOCAL",
    font=("Arial", 22, "bold")
)
titulo.pack(pady=(20, 10))

# ---------------------------------------------------------

modelo_label = ctk.CTkLabel(sidebar, text="Modelo")
modelo_label.pack(pady=(20, 5))

modelo_menu = ctk.CTkOptionMenu(
    sidebar,
    values=[
        "Llama 3",
        "Mistral",
        "Gemma",
        "Phi"
    ]
)
modelo_menu.pack(padx=20)

# ---------------------------------------------------------

tema_label = ctk.CTkLabel(sidebar, text="Tema")
tema_label.pack(pady=(20, 5))

tema_menu = ctk.CTkOptionMenu(
    sidebar,
    values=["Dark", "Light"],
    command=alterar_tema
)
tema_menu.pack(padx=20)

# ---------------------------------------------------------

temperatura_label = ctk.CTkLabel(sidebar, text="Temperatura")
temperatura_label.pack(pady=(20, 5))

temperatura_slider = ctk.CTkSlider(
    sidebar,
    from_=0,
    to=1
)
temperatura_slider.set(0.7)
temperatura_slider.pack(padx=20)

# ---------------------------------------------------------

tokens_label = ctk.CTkLabel(sidebar, text="Max Tokens")
tokens_label.pack(pady=(20, 5))

tokens_slider = ctk.CTkSlider(
    sidebar,
    from_=100,
    to=4000
)
tokens_slider.set(2048)
tokens_slider.pack(padx=20)

# ---------------------------------------------------------

arquivo_btn = ctk.CTkButton(
    sidebar,
    text="Selecionar Arquivo",
    command=escolher_arquivo
)
arquivo_btn.pack(pady=30, padx=20)

# =========================================================
# ÁREA PRINCIPAL
# =========================================================

main_frame = ctk.CTkFrame(app)
main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)

# =========================================================
# TABS
# =========================================================

tabs = ctk.CTkTabview(main_frame)
tabs.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

tabs.add("Chat")
tabs.add("Logs")
tabs.add("Config")

# =========================================================
# ABA CHAT
# =========================================================

chat_tab = tabs.tab("Chat")

chat_tab.grid_columnconfigure(0, weight=1)
chat_tab.grid_rowconfigure(0, weight=1)

# Chat box
chat_box = ctk.CTkTextbox(
    chat_tab,
    wrap="word",
    font=("Consolas", 14)
)
chat_box.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=10,
    pady=10
)

chat_box.insert(
    "end",
    "🤖 Bem-vindo ao sistema de IA local.\n"
)

# Prompt box
entrada_prompt = ctk.CTkTextbox(
    chat_tab,
    height=120
)
entrada_prompt.grid(
    row=1,
    column=0,
    sticky="ew",
    padx=10,
    pady=(0, 10)
)

# =========================================================
# BOTÕES INFERIORES
# =========================================================

bottom_frame = ctk.CTkFrame(main_frame)
bottom_frame.grid(
    row=2,
    column=0,
    sticky="ew",
    padx=10,
    pady=(0, 10)
)

bottom_frame.grid_columnconfigure(0, weight=1)

enviar_btn = ctk.CTkButton(
    bottom_frame,
    text="Enviar Prompt",
    command=enviar_prompt,
    height=40
)
enviar_btn.grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

# Progress bar
progresso = ctk.CTkProgressBar(bottom_frame, width=300)
progresso.grid(
    row=0,
    column=1,
    padx=10
)

progresso.set(0)

# Status
status_label = ctk.CTkLabel(
    bottom_frame,
    text="Pronto"
)
status_label.grid(
    row=0,
    column=2,
    padx=10
)

# =========================================================
# ABA LOGS
# =========================================================

logs_tab = tabs.tab("Logs")

logs_text = ctk.CTkTextbox(logs_tab)
logs_text.pack(
    expand=True,
    fill="both",
    padx=10,
    pady=10
)

logs_text.insert(
    "end",
    "Logs do sistema aparecerão aqui.\n"
)

# =========================================================
# ABA CONFIG
# =========================================================

config_tab = tabs.tab("Config")

config_label = ctk.CTkLabel(
    config_tab,
    text="Configurações da IA",
    font=("Arial", 18, "bold")
)
config_label.pack(pady=20)

checkbox_gpu = ctk.CTkCheckBox(
    config_tab,
    text="Usar GPU"
)
checkbox_gpu.pack(pady=10)

checkbox_stream = ctk.CTkCheckBox(
    config_tab,
    text="Streaming de resposta"
)
checkbox_stream.pack(pady=10)

# =========================================================
# LOOP PRINCIPAL
# =========================================================

app.mainloop()