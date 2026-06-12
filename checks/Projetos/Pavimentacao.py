# -*- coding: utf-8 -*-
def main():
    import os
    import re
    from datetime import datetime
    from pathlib import Path
    import pandas as pd
    import pdfplumber
    import funcs.common_functions as fc
    import checks.Templates.Template_pdf_projeto as Template_pdf_projeto
    #import teste_com_IA.Template_pdf_projeto as Template_pdf_projeto
    import teste_com_IA.PDF_to_MD as pdf2md
    import teste_com_IA.Perguntas_IA as issuesIA
    
    CONFIG_FILE = fc.resource_path("config.json") # Arquivo com informações do projeto

    caminho_dir = fc.get_info(CONFIG_FILE, "diretorio-proj")
    fase = fc.get_info(CONFIG_FILE, "fase-de-projeto")
    br = fc.get_info(CONFIG_FILE, "br")
    br = br.replace("/", "-")
    lote = fc.get_info(CONFIG_FILE, "lote")

    # dado o texto da fase de projeto, pega o número da pasta e o nome da fase
    if fase == "Projeto Básico":
        fase_num = 3
        fase_txt = "Basico"
    elif fase == "Projeto Executivo":
        fase_num = 4
        fase_txt = "Executivo"

    # Caminho para saída dos relatórios
    PATH_OUTPUT_DIR = fc.get_info(CONFIG_FILE, "diretorio-resultados")

    disciplina = os.path.splitext(os.path.basename(__file__))[0]
    PATH_OUTPUT_DIR = PATH_OUTPUT_DIR + "/" + br + "_LT" + lote + "/" + disciplina
    fc.ensure_output_dirs(PATH_OUTPUT_DIR)

    print(f"[INFO] PATH_OUTPUT_DIR localizado em: {PATH_OUTPUT_DIR}")
    PATH_DIR_PROJ = caminho_dir + f"/{fase_num}.{fase_txt}/{fase_num}.1.Geometrico/"

    # Caminho dos arquivos de template
    PATH_TEMPLATE_DIR = fc.resource_path("checks/Templates")
    print(f"[INFO] Template localizado em: {PATH_TEMPLATE_DIR}")

    # ===== Leitura do RAP (Etapa 01) =====
    # Lê o arquivo RAP e retorna o status para preenchimento do excel
    def _etapa_01(rap_path: str):
        tabela = pd.read_excel(rap_path, sheet_name='GERAL')
        tabela = tabela[tabela['DISCIPLINA'].isin(['Estudo de Tráfego', 'Estudo Geotécnico', 'Projeto Geométrico', 'Projeto Terraplenagem'])]
        tabela = tabela[['DISCIPLINA', 'CONDIÇÃO']]
        tabela['STATUS'] = tabela['CONDIÇÃO'].apply(fc.classificar_status)
        print(f"[INFO] Fim da etapa 1")
        return tabela

    # ===== ETAPA 02 — checagem de arquivos ===== Confere se há os arquivos nas pastas e retorna os status correspondentes
    def _etapa_02(path_input_proj: str):
        publicado = Path(path_input_proj)

        vol1_dir = publicado / f"{fase_num}.1.1.Volume-1_Relatorio-do-Projeto-e-Documentos-de-Licitacao"
        ok_e2_v1 = fc.exists_file_with_ext(vol1_dir, (".pdf", ".docx", ".doc"))

        vol2_dir = publicado / f"{fase_num}.1.2.Volume-2_Projeto-de-Execucao"
        ok_e2_v2 = fc.exists_file_with_ext(vol2_dir, (".pdf"))
        ok_e2_v3 = fc.exists_file_with_ext(vol2_dir, (".dwg"))

        vol3_dir = publicado / f"{fase_num}.1.3.Volume-3_Memoria-Justificativa"
        ok_e2_v4 = fc.exists_file_with_ext(vol3_dir, (".pdf", ".docx", ".doc"))

        vol5_dir = publicado / f"{fase_num}.1.3.Volume-5_Cadernno-resposta"
        ok_e2_v5 = fc.exists_file_with_ext(vol5_dir, (".pdf", ".docx", ".doc"))

        tabela = pd.DataFrame({
            'VERIFICAÇÃO': ['Relatório Descritivo (Vol.1)', 'Pranchas .pdf (Vol.2)', 'Arquivos Editáveis .dwg (Vol.2)', 'Relatório Justificativo (Vol.3)', 'Caderno Resposta (Vol.5)'],
            'STATUS': [ok_e2_v1, ok_e2_v2, ok_e2_v3, ok_e2_v4, ok_e2_v5]
        })

        tabela['STATUS'] = tabela['STATUS'].apply(fc.truefalse_to_vx)

        print(f"[INFO] Fim da etapa 2")
        return tabela

    # ===== ETAPA 03/04 — extração de texto e checks =====
    def _etapa_03_etapa_04(path_input_proj: str, perguntas_IA) -> dict:

        publicado = Path(path_input_proj)

        vol1_dir = publicado / f"{fase_num}.1.1.Volume-1_Relatorio-do-Projeto-e-Documentos-de-Licitacao"
        vol2_dir = publicado / f"{fase_num}.1.2.Volume-2_Projeto-de-Execucao"
        vol3_dir = publicado / f"{fase_num}.1.3.Volume-3_Memoria-Justificativa"

        arquivos_pdf = [p.stem for p in vol1_dir.glob("*.pdf")]
        print(arquivos_pdf)

        respostas = {}

        # --- Análise volume 1:
        if arquivos_pdf:
            for arquivo in arquivos_pdf:
                arquivo_md = pdf2md.pdf_to_md(vol1_dir, arquivo, PATH_OUTPUT_DIR)
                print(f"[INFO] Fim da exportação para md")
                respostas[arquivo] = issuesIA.perguntas_IA(PATH_OUTPUT_DIR, arquivo_md, perguntas_IA)
                print(f"[INFO] Fim das perguntas de IA")
        
        print(f"[INFO] Fim da etapa 3")
        return respostas
    
    # ===== Main =====
    def principal():
        rap_path = fc.get_info(CONFIG_FILE, "arquivo-rap")

        print(f"[INFO] RAP utilizado: {rap_path}")

        # Cálculo de índices

        # etapa 1
        e1_tabela = _etapa_01(rap_path)
        e1_tot= len(e1_tabela)
        e1_ap= list(e1_tabela['CONDIÇÃO']).count("Aprovado")
        e1_rs= list(e1_tabela['CONDIÇÃO']).count("Aprovado com Ressalva")
        e1_rp= list(e1_tabela['CONDIÇÃO']).count("Reprovado")
        e1_pct = round(100 * (e1_ap + e1_rs) / e1_tot, 1)

        e2_tabela = _etapa_02(PATH_DIR_PROJ)
        e2_tot= len(e2_tabela)
        e2_ap= list(e2_tabela['STATUS']).count("✔")
        e2_rp= list(e2_tabela['STATUS']).count("✖")
        e2_pct = round(100 * (e2_ap) / e2_tot, 1)

        perguntas_IA = [
            "O mapa de localização da obra foi apresentado?",
            "O documento possui Anotação de Responsabilidade Técnica (ART)?",
            "Foi apresentado o quadro resumo das composições e das quantidades de serviço?",
            "Dimensionamento do pavimento feito pelo Método da Resistência, Método da Resiliência ou Análises Mecanísticas?",
            "Foi apresentado o nome e caraterísticas principais do software utilizado para o dimensionamento do pavimento?"
        ]
        respostas_IA = _etapa_03_etapa_04(PATH_DIR_PROJ, perguntas_IA)
    
        conf_geral = round((e1_pct + e2_pct) / 2, 1)
        print(conf_geral)
        for relatorio in respostas_IA.keys():
            nome_saida = fc.prox_versao(PATH_OUTPUT_DIR, str(datetime.now().year), br, "PGMT", lote)
            print(nome_saida)

            pdf_path = os.path.join(PATH_OUTPUT_DIR, nome_saida + '.pdf')
            print(pdf_path)

            print(perguntas_IA)
            print(respostas_IA)


            Template_pdf_projeto.gerar_pdf(
                pdf_path = pdf_path, 
                disciplina = 'Pavimentação', 
                relatorio_de_analise = relatorio,
                conf_geral=str(conf_geral) + "%",

                e1_tabela = e1_tabela,
                e1_ap=e1_ap,
                e1_tot=e1_tot,
                e1_rs=e1_rs,
                e1_rp=e1_rp,
                e1_pct=e1_pct,

                e2_tabela = e2_tabela,
                e2_ap = e2_ap,
                e2_tot = e2_tot,
                e2_rp = e2_rp,
                e2_pct = e2_pct,

                e3_perguntas = perguntas_IA,
                e3_respostas = respostas_IA[relatorio]
                )
    principal()