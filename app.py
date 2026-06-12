import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog, PhotoImage
from pathlib import Path
import os
import sys 
import threading
import json
import importlib.util
import re
import unicodedata
from datetime import datetime
import pandas as pd
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import funcs.common_functions as fc
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
import lmstudio as lms


# Configurações básicas
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# função para salvar no JSON
def salvar_json(chave, valor):
    # Lê o JSON existente, se houver
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {}

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({chave: valor}, f)

    # Atualiza ou adiciona a nova chave
    dados[chave] = valor
    
    # Salva de volta
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def salvar_diretorio(path, info):
        """Salva o caminho escolhido em um arquivo JSON."""
        with open(CONFIG_FILE, "w") as f:
            json.dump({info: path}, f)


def selecionar_dir_proj():
    path = filedialog.askdirectory()
    if path:
        salvar_diretorio(path, 'diretorio-proj')
        label_proj.configure(text=f"Diretório selecionado:\n{path}", text_color='black')

def selecionar_fase():
    salvar_json('fase-de-projeto', nm_fase.get())

def resource_path(relative_path):
    """Retorna o caminho absoluto para um recurso, mesmo quando empacotado em .exe"""
    if hasattr(sys, '_MEIPASS'):  # atributo criado pelo PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CONFIG_FILE = resource_path("config.json")

# ---------------------------
# Resetar o arquivo ao iniciar
# ---------------------------
with open(CONFIG_FILE, "w") as f:
    json.dump({}, f)

# Carregar dados
with open(CONFIG_FILE, "r") as f:
    dados = json.load(f)

def abrir_painel():
    painel = ctk.CTkToplevel(app)
    painel.title("CPD-DNIT")
    painel.geometry("500x350") # tamanho da janela 
    painel.resizable(False, False) # não redimensionar janela
    painel.iconbitmap(resource_path(r"figs\logo_dnit_scan.ico"))
    painel.protocol("WM_DELETE_WINDOW", app.destroy) # quando o painel for fechado, encerra o programa de vez
    
    def voltar_pag_inicial():
        painel.destroy()  # fecha a secundária
        app.deiconify()  # reaparece a principal
    ctk.CTkButton(painel, text="↩️Voltar", command=voltar_pag_inicial, width=30).pack(pady=(2, 1), anchor="w", padx=2)

    def selecionar_dir_resultados():
        path = filedialog.askdirectory()
        if path:
            salvar_json('diretorio-resultados', path)
            label_dir_resultados.configure(text=f"Diretório selecionado:\n{path}", text_color='black')

    def selecionar_dir_RAP():
        path = filedialog.askopenfilename(title="Selecione um arquivo", filetypes=[("Todos os arquivos", "*.xlsx*")])
        if path:
            salvar_json('arquivo-rap', path)
            label_dir_RAP.configure(text=f"Arquivo selecionado:\n{path}", text_color='black')

    #ctk.CTkLabel(painel, text="Selecione diretório exportação de resultados:", font=ctk.CTkFont(size=14)).pack(pady=(25, 5))
    botao_diretorio_resultados = ctk.CTkButton(painel, text="Selecione diretório de exportação de resultados", command=selecionar_dir_resultados, width=250)
    botao_diretorio_resultados.pack(anchor="center", pady=(20,0))
    label_dir_resultados = ctk.CTkLabel(painel, text="", fg_color="transparent") # texto alterado com a função selecionar_diretorio
    label_dir_resultados.pack(anchor="center", pady=2)

    botao_diretorio_RAP = ctk.CTkButton(painel, text="Selecione arquivo de status do RAP", command=selecionar_dir_RAP, width=250)
    botao_diretorio_RAP.pack(anchor="center", pady=(15,0))
    label_dir_RAP = ctk.CTkLabel(painel, text="", fg_color="transparent") # texto alterado com a função selecionar_diretorio
    label_dir_RAP.pack(anchor="center", pady=2)

    ctk.CTkLabel(painel, text="Selecione uma verificação:", font=ctk.CTkFont(size=14)).pack(pady=((20,2)))

    if nm_fase.get() == "Estudos Preliminares": # Se estudos -> pasta de estudos, senão -> pasta de projetos
        PASTA_SCRIPTS = resource_path("checks/Estudos/")
    else: 
        PASTA_SCRIPTS = resource_path("checks/Projetos/")


    try:
        scripts = [f for f in os.listdir(PASTA_SCRIPTS) if f.endswith(".py")] # Procura dentro da pasta PASTA_SCRIPTS todos os arquivos Python (.py)
        '''
        scripts = [
            os.path.splitext(f)[0]  # pega só o nome, sem ".py"
            for f in os.listdir(PASTA_SCRIPTS)
            if f.endswith(".py")
        ]
        '''
    except FileNotFoundError:
        scripts = []
    combo_script = ctk.CTkComboBox(painel, values=scripts)
    combo_script.pack(pady=2)

    # Botão executar (mantemos referência para habilitar/desabilitar)
    btn_executar = ctk.CTkButton(painel, text="Executar", width=250) # É o botão que dispara a execução do script escolhido.
    btn_executar.pack(pady=(20,5))

    # Barra de progresso indeterminada (apenas quando rodando)
    progress = ctk.CTkProgressBar(painel, mode="indeterminate", width=250)
    progress.set(0)

    def executar():
        with open(CONFIG_FILE, "r") as f:
            #selecionar_fase()
            dados = json.load(f)
            if dados.get("diretorio-resultados") == None:
                label_dir_resultados.configure(text=f"Selecione um diretório de resultados para continuar", text_color='red')
            elif dados.get("arquivo-rap") == None:
                label_dir_RAP.configure(text=f"Selecione o arquivo RAP para continuar", text_color='red')
            else:
                script_file  = combo_script.get()
                script_path = os.path.join(PASTA_SCRIPTS, script_file)

                # UI: preparando execução
                btn_executar.configure(state="disabled", text="Executando…")
                progress.pack(pady=(0, 10))
                progress.start()

                def rodar_script():
                    try:
                        # Cria o módulo a partir do arquivo
                        spec = importlib.util.spec_from_file_location("modulo_temp", script_path)
                        modulo = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(modulo)
                        # Roda a função principal do script
                        if hasattr(modulo, "main"):
                            modulo.main()
                        else:
                            print("O script não tem função 'main()'.")
                        app.after(0, lambda: messagebox.showinfo("Concluído", "✅ Verificação finalizada!"))
                    except Exception as e:
                        app.after(0, lambda e=e: messagebox.showerror("Erro", f"❌ Erro ao executar: {e}"))

                    finally:
                        app.after(0, progress.stop)
                        app.after(0, progress.pack_forget)
                        app.after(0, lambda: btn_executar.configure(state="normal", text="Executar"))


                # Executa em segundo plano
                threading.Thread(target=rodar_script, daemon=True).start()

    btn_executar.configure(command=executar)

def continuar():
    if os.path.exists(CONFIG_FILE):
        salvar_json('fase-de-projeto', nm_fase.get())
        salvar_json('processo', nm_processo.get())
        salvar_json('br', nm_BR.get())
        salvar_json('lote', fc.padronizar_lote(nm_lote.get()))
        salvar_json('analista', nm_analista.get())
        salvar_json('extensao', nm_extensao.get())
        if nm_tp_proj.get() == 'Tipo...':
            salvar_json('tipo-de-projeto', '')
        else:
            salvar_json('tipo-de-projeto', nm_tp_proj.get())
        with open(CONFIG_FILE, "r") as f:
            #selecionar_fase()
            dados = json.load(f)
            if dados.get("diretorio-proj") == None:
                label_proj.configure(text=f"Selecione um diretório de projeto para continuar", text_color='red')
            
            campos_obr = ['diretorio-proj', 'fase-de-projeto','processo', 'br', 'lote', 'analista', 'extensao']
            dic_campos = {'fase-de-projeto': nm_fase, 'processo': nm_processo, 'br': nm_BR, 'lote': nm_lote, 'analista': nm_analista, 'extensao': nm_extensao}
            campos_vazios = []
            for campo in campos_obr:
                if any((dados.get(campo) == None, dados.get(campo) == "", dados.get(campo) == "Fase...")):
                    campos_vazios.append(campo)
                    try: 
                        if campo == 'diretorio-proj':
                            continue
                        dic_campos[campo].configure(placeholder_text_color="red")
                    except:
                        if campo == 'diretorio-proj':
                            continue
                        dic_campos[campo].configure(text_color="red")

            if len(campos_vazios) != 0:
                label_error.configure(text=f"Preencha os campos obrigatórios para continuar", text_color='red')
            
            elif dados.get("fase-de-projeto") == "Fase...":
                label_error.configure(text=f"Selecione uma fase para continuar", text_color='red')
                #salvar_json('fase-de-projeto', nm_fase.get())

            elif not re.match(r"^\d{2,3}/[A-Z]{2}$", nm_BR.get().strip()):
                label_error.configure(
                    text="Rodovia inválida! Use o formato XXX/UF (ex: 123/DF).",
                    text_color="red"
                )

            else:
                salvar_json('processo', nm_processo.get())
                salvar_json('edital', nm_edital.get())
                salvar_json('contrato', nm_contrato.get())
                salvar_json('modalidade-de-contratacao', nm_modalidade_contratacao.get())
                salvar_json('br', nm_BR.get())
                salvar_json('lote', fc.padronizar_lote(nm_lote.get()))
                salvar_json('numero-analise', nm_analise.get())
                salvar_json('numero-ult-relatorio', nm_ult_relatorio.get())
                salvar_json('analista', nm_analista.get())
                app.withdraw()  # esconde a janela principal
                abrir_painel()


if __name__ == "__main__":
    # Janela principal
    app = ctk.CTk()
    app.geometry("820x545")
    app.title("CPD-DNIT") # Primeira tela 
    app.resizable(False, False)
    app.iconbitmap(resource_path(r"figs\logo_dnit_scan.ico"))

    # Frame Esquerdo - Logo com CROP estilo "preencher"
    frame_esquerdo = ctk.CTkFrame(app, fg_color="black")
    frame_esquerdo.place(relx=0, rely=0, relwidth=0.55, relheight=1)

    def atualizar_logo(event=None):
            
        frame_width = frame_esquerdo.winfo_width()
        frame_height = frame_esquerdo.winfo_height()

        imagem_logo = Image.open(resource_path(r"figs\logo_dnit_scan.jpeg"))
        # exemplo de uso
        img_width, img_height = imagem_logo.size
        img_ratio = img_width / img_height
        frame_ratio = frame_width / frame_height

        if img_ratio > frame_ratio:
            new_height = frame_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = frame_width
            new_height = int(new_width / img_ratio)

        imagem_logo = imagem_logo.resize((new_width, new_height), Image.LANCZOS)
        
        left = (new_width - frame_width) / 2
        top = (new_height - frame_height) / 2
        right = (new_width + frame_width) / 2
        bottom = (new_height + frame_height) / 2
        imagem_logo = imagem_logo.crop((left, top, right, bottom))

        logo_tk = ImageTk.PhotoImage(imagem_logo)
        label_logo.configure(image=logo_tk)
        label_logo.image = logo_tk  # evita garbage collection

    label_logo = ctk.CTkLabel(frame_esquerdo, text="")
    label_logo.pack(fill="both", expand=True)
    
    # Atualiza a logo quando o frame for redimensionado
    frame_esquerdo.bind("<Configure>", atualizar_logo)
    #ctk.CTkLabel(frame_esquerdo, image=logo_tk, text="").pack()

    # Frame Direito - Login
    frame_direito = ctk.CTkFrame(app, fg_color="#ffffff")
    frame_direito.place(relx=0.55, rely=0, relwidth=0.45, relheight=1)

    card = ctk.CTkFrame(frame_direito, corner_radius=15, fg_color="#ffffff", border_width=2, border_color="#223467")
    card.pack(pady=5, padx=10, expand=True)

    frame_botao_dir_proj = ctk.CTkFrame(card, fg_color="transparent")
    frame_botao_dir_proj.pack(pady=4, padx=20, fill="x")
    botao_dir_proj = ctk.CTkButton(frame_botao_dir_proj, text="Selecionar Diretório de Projeto", command=selecionar_dir_proj, width=250)
    botao_dir_proj.pack(anchor="center")

    frame_label_dir_proj = ctk.CTkFrame(card, fg_color="transparent")
    frame_label_dir_proj.pack(pady=0, padx=20, fill="x")
    label_proj = ctk.CTkLabel(frame_label_dir_proj, text="Nenhum diretório de projeto selecionado", fg_color="transparent") # texto alterado com a função selecionar_diretorio
    label_proj.pack(anchor="center")

    frame_processo = ctk.CTkFrame(card, fg_color="transparent")
    frame_processo.pack(pady=3, padx=20, fill="x")
    lbl_processo = ctk.CTkLabel(frame_processo, text="Processo:")
    lbl_processo.pack(side="left", padx=(0, 10))
    nm_processo = ctk.CTkEntry(frame_processo, placeholder_text="Processo de análise", width=150, border_width=0, fg_color="transparent")
    nm_processo.pack(side="left", fill="x", expand=True)

    frame_edital = ctk.CTkFrame(card, fg_color="transparent")
    frame_edital.pack(pady=3, padx=20, fill="x")
    lbl_edital = ctk.CTkLabel(frame_edital, text="Edital:")
    lbl_edital.pack(side="left", padx=(0, 10))
    nm_edital = ctk.CTkEntry(frame_edital, placeholder_text="Edital", width=150, border_width=0, fg_color="transparent")
    nm_edital.pack(side="left", fill="x", expand=True)

    frame_contrato = ctk.CTkFrame(card, fg_color="transparent")
    frame_contrato.pack(pady=3, padx=20, fill="x")
    lbl_contrato = ctk.CTkLabel(frame_contrato, text="Contrato:")
    lbl_contrato.pack(side="left", padx=(0, 10))
    nm_contrato = ctk.CTkEntry(frame_contrato, placeholder_text="Contrato", width=150, border_width=0, fg_color="transparent")
    nm_contrato.pack(side="left", fill="x", expand=True)

    frame_mod_contratacao = ctk.CTkFrame(card, fg_color="transparent")
    frame_mod_contratacao.pack(pady=3, padx=20, fill="x")
    lbl_mod_contratacao = ctk.CTkLabel(frame_mod_contratacao, text="Modalidade de Contratação:")
    lbl_mod_contratacao.pack(side="left", padx=(0, 10))
    nm_modalidade_contratacao = ctk.CTkEntry(frame_mod_contratacao, placeholder_text="Modalidade", width=150, border_width=0, fg_color="transparent")
    nm_modalidade_contratacao.pack(side="left", fill="x", expand=True)

    frame_BR = ctk.CTkFrame(card, fg_color="transparent")
    frame_BR.pack(pady=3, padx=20, fill="x")
    lbl_BR = ctk.CTkLabel(frame_BR, text="BR:")
    lbl_BR.pack(side="left", padx=(0, 10))
    nm_BR = ctk.CTkEntry(frame_BR, placeholder_text="BR no formato XXX/UF (ex: 123/DF)", width=150, border_width=0, fg_color="transparent")
    nm_BR.pack(side="left", fill="x", expand=True)

    frame_extensao = ctk.CTkFrame(card, fg_color="transparent")
    frame_extensao.pack(pady=3, padx=20, fill="x")
    lbl_extensao = ctk.CTkLabel(frame_extensao, text="Extensão:")
    lbl_extensao.pack(side="left", padx=(0, 10))
    nm_extensao = ctk.CTkEntry(frame_extensao, placeholder_text="Extensão", width=150, border_width=0, fg_color="transparent")
    nm_extensao.pack(side="left", fill="x", expand=True)

    frame_lote = ctk.CTkFrame(card, fg_color="transparent")
    frame_lote.pack(pady=3, padx=20, fill="x")
    lbl_lote = ctk.CTkLabel(frame_lote, text="Lote:")
    lbl_lote.pack(side="left", padx=(0, 10))
    nm_lote = ctk.CTkEntry(frame_lote, placeholder_text="Lote", width=150, border_width=0, fg_color="transparent")
    nm_lote.pack(side="left", fill="x", expand=True)

    frame_tp_proj = ctk.CTkFrame(card, fg_color="transparent")
    frame_tp_proj.pack(pady=3, padx=20, fill="x")
    lbl_tp_proj = ctk.CTkLabel(frame_tp_proj, text="Tipo de projeto:")
    lbl_tp_proj.pack(side="left", padx=(0, 10))
    opcoes_tp_proj = ["Tipo...", "Manutenção", "Implantação", "Misto", "Duplicação", "OAE", "Proarte"] # Lista de opções
    nm_tp_proj = ctk.CTkOptionMenu(frame_tp_proj, values=opcoes_tp_proj, width=150, fg_color="#ffffff", button_color="#ffffff", button_hover_color="#ffffff", dropdown_fg_color="white", dropdown_text_color="black", text_color="black")
    nm_tp_proj.set("Tipo...")  # valor inicial
    # Ajusta cor do placeholder
    nm_tp_proj.configure(text_color="gray")
    def on_change(choice):
        if choice != "Tipo...":
            nm_tp_proj.configure(text_color="black")
    nm_tp_proj.configure(command=on_change)
    nm_tp_proj.pack(side="left", fill="x", expand=True)

    frame_fase = ctk.CTkFrame(card, fg_color="transparent")
    frame_fase.pack(pady=3, padx=20, fill="x")
    lbl_fase = ctk.CTkLabel(frame_fase, text="Fase:")
    lbl_fase.pack(side="left", padx=(0, 10))
    opcoes_fase = ["Fase...", "Estudos Preliminares", "Projeto Básico", "Projeto Executivo"] # Lista de opções
    nm_fase = ctk.CTkOptionMenu(frame_fase, values=opcoes_fase, width=150, fg_color="#ffffff", button_color="#ffffff", button_hover_color="#ffffff", dropdown_fg_color="white", dropdown_text_color="black", text_color="black")
    nm_fase.set("Fase...")  # valor inicial
    # Ajusta cor do placeholder
    nm_fase.configure(text_color="gray")
    def on_change(choice):
        if choice != "Fase...":
            nm_fase.configure(text_color="black")
    nm_fase.configure(command=on_change)
    nm_fase.pack(side="left", fill="x", expand=True)

    frame_analise = ctk.CTkFrame(card, fg_color="transparent")
    frame_analise.pack(pady=3, padx=20, fill="x")
    lbl_analise = ctk.CTkLabel(frame_analise, text="Versão da análise:")
    lbl_analise.pack(side="left", padx=(0, 10))
    nm_analise = ctk.CTkEntry(frame_analise, placeholder_text="Análise (1ª, 2ª, etc)", width=150, border_width=0, fg_color="transparent")
    nm_analise.pack(side="left", fill="x", expand=True)

    frame_ult_relatorio = ctk.CTkFrame(card, fg_color="transparent")
    frame_ult_relatorio.pack(pady=3, padx=20, fill="x")
    lbl_ult_relatorio = ctk.CTkLabel(frame_ult_relatorio, text="Número do último relatório:")
    lbl_ult_relatorio.pack(side="left", padx=(0, 10))
    nm_ult_relatorio = ctk.CTkEntry(frame_ult_relatorio, placeholder_text="Número", width=150, border_width=0, fg_color="transparent")
    nm_ult_relatorio.pack(side="left", fill="x", expand=True)

    frame_analista = ctk.CTkFrame(card, fg_color="transparent")
    frame_analista.pack(pady=3, padx=20, fill="x")
    lbl_analista = ctk.CTkLabel(frame_analista, text="Nome do(a) analista:")
    lbl_analista.pack(side="left", padx=(0, 10))
    nm_analista = ctk.CTkEntry(frame_analista, placeholder_text="Analista", width=150, border_width=0, fg_color="transparent")
    nm_analista.pack(side="left", fill="x", expand=True)

    frame_label_diretorio = ctk.CTkFrame(card, fg_color="transparent")
    frame_label_diretorio.pack(pady=0, padx=20, fill="x")
    label_error = ctk.CTkLabel(frame_label_diretorio, text="", fg_color="transparent") # texto alterado com a função selecionar_diretorio
    label_error.pack(anchor="center")

    ctk.CTkButton(card, text="Continuar", command=continuar, width=260).pack(pady=4)
    app.mainloop()