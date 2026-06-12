import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from pathlib import Path
import os
import sys
import json
import threading
import importlib.util
import re

# =========================================================
# CONFIGURAÇÕES
# =========================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def caminho_arquivo(relative_path): # retorna o caminho do arquivo

    if hasattr(sys, "_MEIPASS"): # se a biblioteca sys identifica uma pasta temporária chamada _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path) # junta o caminho da pasta com o caminho do arquivo
    return os.path.join(os.path.abspath("."), relative_path) # se não tem pasta temporária, usa pasta atual

CONFIG_FILE = caminho_arquivo("config.json")

def salvar_json(chave, valor):
    
    if Path(CONFIG_FILE).exists(): # garante a existência do arquivo de dados de configuração
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {}

    dados[chave] = valor # atribui o dado ao dicionário

    with open(CONFIG_FILE, "w", encoding="utf-8") as f: # salva no arquivo de configurações
        json.dump(dados, f, ensure_ascii=False, indent=4)


# =========================================================
# SPLASH SCREEN
# =========================================================

class SplashScreen(ctk.CTkToplevel):

    def __init__(self, parent):

        super().__init__(parent)
        self.parent = parent

        largura = 500
        altura = 375

        x = int((self.winfo_screenwidth() / 2) - (largura / 2))
        y = int((self.winfo_screenheight() / 2) - (altura / 2))

        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.overrideredirect(True)
        self.configure(fg_color="#111111")

        # =====================================================
        # LOGO
        # =====================================================

        imagem = ctk.CTkImage(
            light_image=Image.open(caminho_arquivo(r"figs\logo_dnit_scan_v2.jpeg")),
            dark_image=Image.open(caminho_arquivo(r"figs\logo_dnit_scan_v2.jpeg")),
            size=(500, 375)
        )

        label_logo = ctk.CTkLabel(
            self,
            image=imagem,
            text=""
        )
        label_logo.pack()

        self.after(100, self.carregar)

    def carregar(self):

        # =====================================================
        # IMPORTS PESADOS
        # =====================================================

        #self.label_status.configure(text="Carregando bibliotecas...")

        #global pd
        #import pandas as pd
        # Exemplos:
        # import lmstudio as lms
        # from langchain_community.vectorstores import FAISS
        self.after(1000, self.finalizar)

    def finalizar(self):

        self.destroy()
        self.parent.deiconify()


# =========================================================
# APLICAÇÃO PRINCIPAL
# =========================================================

class MainApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.geometry("1000x600")

        self.title("CPD-DNIT")

        self.resizable(False, False)

        self.iconbitmap(caminho_arquivo(r"figs\logo_dnit_scan.ico"))

        # =====================================================
        # RESET CONFIG
        # =====================================================

        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)

        # =====================================================
        # INTERFACE
        # =====================================================

        self.criar_interface()

    # =========================================================
    # INTERFACE
    # =========================================================

    def criar_interface(self):

        # =====================================================
        # FRAME ESQUERDO
        # =====================================================

        self.frame_esquerdo = ctk.CTkFrame(
            self,
            fg_color="#ffffff"
        )

        self.frame_esquerdo.place(
            relx=0,
            rely=0,
            relwidth=0.5,
            relheight=1
        )

        self.campos_lado_esquerdo()

        # =====================================================
        # FRAME DIREITO
        # =====================================================

        self.frame_direito = ctk.CTkFrame(
            self,
            fg_color="#ffffff"
        )

        self.frame_direito.place(
            relx=0.5,
            rely=0,
            relwidth=0.5,
            relheight=1
        )

        self.campos_lado_direito()

    # =========================================================
    # LOGO
    # =========================================================

    def atualizar_logo(self, event=None):
        return

    # =========================================================
    # CAMPOS
    # =========================================================

    # =========================================================
    # LADO ESQUERDO
    # =========================================================

    def campos_lado_esquerdo(self):
        
        # =====================================================
        # TÍTULO
        # =====================================================
        titulo = ctk.CTkLabel(
            self.frame_esquerdo,
            text="CPD-DNIT",
            font=("Arial", 28, "bold"),
            text_color="#223467"
        )

        titulo.pack(pady=(20, 15))

        # =====================================================
        # PROCESSO
        # =====================================================
        # cria frame
        frame_processo = ctk.CTkFrame(self.frame_esquerdo, fg_color="transparent")
        frame_processo.pack(fill="x", padx=30)

        # define label
        ctk.CTkLabel(
            frame_processo,
            text="Processo",
            width=75,
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        # cria campo
        self.nm_processo = ctk.CTkEntry(frame_processo)

        # cria grid (tabela)
        self.nm_processo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady= 2
        )

        # define largura dos campos
        frame_processo.grid_columnconfigure(1, weight=1)

        # =====================================================
        # EDITAL
        # =====================================================

        # cria frame
        frame_edital = ctk.CTkFrame(self.frame_esquerdo, fg_color="transparent")
        frame_edital.pack(fill="x", padx=30)

        # define label
        ctk.CTkLabel(
            frame_edital,
            text="Edital",
            width=75,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        # cria campo
        self.nm_edital = ctk.CTkEntry(frame_edital)

        # cria grid (tabela)
        self.nm_edital.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(10, 0)
        )

        # define largura dos campos
        frame_edital.grid_columnconfigure(1, weight=1)


    # =========================================================
    # LADO DIREITO
    # =========================================================

    def campos_lado_direito(self):

        # =====================================================
        # DIRETÓRIO PROJETO
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Selecionar Diretório do Projeto",
            command=self.selecionar_dir_proj,
            width=300
        ).pack(pady=(10, 0))

        self.label_proj = ctk.CTkLabel(
            self.frame_direito,
            text="Nenhum diretório selecionado",
            wraplength=400
        )

        self.label_proj.pack(pady=(0, 15))

        # =====================================================
        # RESULTADOS
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Selecionar Diretório de Resultados",
            command=self.selecionar_dir_resultados,
            width=300
        ).pack(pady=(5, 0))

        self.label_resultados = ctk.CTkLabel(
            self.frame_direito,
            text="Nenhum diretório selecionado"
        )

        self.label_resultados.pack(pady=(0, 15))

        # =====================================================
        # RAP
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Selecionar Arquivo RAP",
            command=self.selecionar_rap,
            width=300
        ).pack(pady=(5, 0))

        self.label_rap = ctk.CTkLabel(
            self.frame_direito,
            text="Nenhum arquivo selecionado"
        )

        self.label_rap.pack(pady=(0, 15))

        # =====================================================
        # COMBO SCRIPTS
        # =====================================================

        self.label_script = ctk.CTkLabel(
            self.frame_direito,
            text="Selecione uma verificação"
        )

        self.label_script.pack(pady=(20, 5))

        self.combo_script = ctk.CTkComboBox(
            self.frame_direito,
            values=[]
        )

        self.combo_script.pack(
            fill="x",
            padx=30
        )

        # =====================================================
        # BOTÃO CARREGAR SCRIPTS
        # =====================================================

        ctk.CTkButton(
            self.frame_direito,
            text="Atualizar Scripts",
            command=self.carregar_scripts
        ).pack(pady=10)

        # =====================================================
        # PROGRESSO
        # =====================================================

        self.progress = ctk.CTkProgressBar(
            self.frame_direito,
            mode="indeterminate"
        )

        # =====================================================
        # EXECUTAR
        # =====================================================

        self.btn_executar = ctk.CTkButton(
            self.frame_direito,
            text="Executar",
            command=self.executar_script,
            width=300
        )

        self.btn_executar.pack(pady=20)

    # =========================================================
    # DIRETÓRIOS
    # =========================================================

    def selecionar_dir_proj(self):

        path = filedialog.askdirectory()

        if path:

            salvar_json("diretorio-proj", path)

            self.label_proj.configure(
                text=path,
                text_color="black"
            )

    def selecionar_dir_resultados(self):

        path = filedialog.askdirectory()

        if path:

            salvar_json("diretorio-resultados", path)

            self.label_resultados.configure(
                text=path,
                text_color="black"
            )

    def selecionar_rap(self):

        path = filedialog.askopenfilename(
            title="Selecione um arquivo RAP",
            filetypes=[("Excel", "*.xlsx")]
        )

        if path:

            salvar_json("arquivo-rap", path)

            self.label_rap.configure(
                text=path,
                text_color="black"
            )

    # =========================================================
    # SCRIPTS
    # =========================================================

    def carregar_scripts(self):

        fase = self.nm_fase.get()

        if fase == "Estudos Preliminares":

            pasta = caminho_arquivo("checks/Estudos/")

        else:

            pasta = caminho_arquivo("checks/Projetos/")

        try:

            scripts = [
                f for f in os.listdir(pasta)
                if f.endswith(".py")
            ]

        except:

            scripts = []

        self.combo_script.configure(values=scripts)

        if scripts:
            self.combo_script.set(scripts[0])

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def executar_script(self):

        br = self.nm_BR.get().strip()

        if not re.match(r"^\d{2,3}/[A-Z]{2}$", br):

            messagebox.showerror(
                "Erro",
                "BR inválida.\nUse XXX/UF"
            )

            return

        script = self.combo_script.get()

        if not script:

            messagebox.showerror(
                "Erro",
                "Selecione um script"
            )

            return

        fase = self.nm_fase.get()

        if fase == "Estudos Preliminares":

            pasta = caminho_arquivo("checks/Estudos/")

        else:

            pasta = caminho_arquivo("checks/Projetos/")

        script_path = os.path.join(
            pasta,
            script
        )

        # =====================================================
        # UI
        # =====================================================

        self.btn_executar.configure(
            state="disabled",
            text="Executando..."
        )

        self.progress.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        self.progress.start()

        # =====================================================
        # THREAD
        # =====================================================

        def rodar():

            try:

                spec = importlib.util.spec_from_file_location(
                    "modulo_temp",
                    script_path
                )

                modulo = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(modulo)

                if hasattr(modulo, "main"):

                    modulo.main()

                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Concluído",
                        "Verificação finalizada!"
                    )
                )

            except Exception as e:

                self.after(
                    0,
                    lambda e=e: messagebox.showerror(
                        "Erro",
                        str(e)
                    )
                )

            finally:

                self.after(
                    0,
                    self.progress.stop
                )

                self.after(
                    0,
                    self.progress.pack_forget
                )

                self.after(
                    0,
                    lambda: self.btn_executar.configure(
                        state="normal",
                        text="Executar"
                    )
                )

        threading.Thread(
            target=rodar,
            daemon=True
        ).start()


# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    app = MainApp()

    # Esconde principal
    app.withdraw()

    # Splash
    splash = SplashScreen(app)

    # Loop único
    app.mainloop()
