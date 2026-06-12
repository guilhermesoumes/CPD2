import customtkinter as ctk
from tkinter import filedialog

def escolher_pdfs():
    arquivos = filedialog.askopenfilenames(
        title="Selecione os relatórios",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    for arquivo in arquivos:
        print(arquivo)

app = ctk.CTk()

botao = ctk.CTkButton(
    app,
    text="Selecionar PDF",
    command=escolher_pdfs
)
botao.pack(padx=20, pady=20)

app.mainloop()