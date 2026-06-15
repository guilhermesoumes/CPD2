# -*- coding: utf-8 -*-
def main():
    # =========================================================
    # IMPORT DE BIBLIOTECAS
    # =========================================================
    import pandas as pd
    import funcs.common_functions as fc
    import os
    from pathlib import Path
    import teste_com_IA.Perguntas_IA as issuesIA
    from datetime import datetime
    import checks.Templates.Template_pdf_estudo as Template_pdf_estudo

    # =========================================================
    # IMPORT DE DADOS DE CONFIGURAÇÃO
    # =========================================================
    CONFIG_FILE = fc.resource_path("config.json")

    arquivos = fc.get_info(CONFIG_FILE, "arquivos-para-analisar")
    rap_path = fc.get_info(CONFIG_FILE, "arquivo-rap")
    fase = fc.get_info(CONFIG_FILE, "fase-de-projeto")
    br = fc.get_info(CONFIG_FILE, "rodovia")
    br = br.replace("/", "-")
    lote = fc.get_info(CONFIG_FILE, "lote")
    disciplina = os.path.splitext(os.path.basename(__file__))[0]


    # Caminho para saída dos relatórios
    PATH_OUTPUT_DIR = fc.get_info(CONFIG_FILE, "diretorio-resultados")

    PATH_OUTPUT_DIR = PATH_OUTPUT_DIR + "/" + br + "_LT" + lote + "/" + disciplina
    
    # =========================================================
    # DEFINIÇÃO DE PARÂMETROS
    # =========================================================
    if fase == "Projeto Básico":
        fase_num = 3
        fase_txt = "Basico"
    elif fase == "Projeto Executivo":
        fase_num = 4
        fase_txt = "Executivo"

    fc.ensure_output_dirs(PATH_OUTPUT_DIR)

    #etapa = os.path.basename(caminho_dir)[0]

    #print(f"[INFO] PATH_OUTPUT_DIR localizado em: {PATH_OUTPUT_DIR}")
    #PATH_DIR_PROJ = caminho_dir + f"/{etapa}.{fase_num}.{fase_txt}/{etapa}.{fase_num}.02.Geometrico/"
    #print(PATH_DIR_PROJ)

    # Caminho dos arquivos de template
    PATH_TEMPLATE_DIR = fc.resource_path("checks/Templates")
    #print(f"[INFO] Template localizado em: {PATH_TEMPLATE_DIR}")

    # =========================================================
    # ETAPA 1 — checagem de relatório de aprovação de projeto
    # =========================================================
    
    def _etapa_01(rap_path: str): # Lê o arquivo RAP e retorna o status para preenchimento do excel
        tabela = pd.read_excel(rap_path, sheet_name='GERAL')
        tabela = tabela[tabela['DISCIPLINA'].isin(['Estudo Geológico', 'Estudo Topográfico', 'Estudo de Tráfego'])]
        tabela = tabela[['DISCIPLINA', 'CONDIÇÃO']]
        tabela['STATUS'] = tabela['CONDIÇÃO'].apply(fc.classificar_status)
        print(f"[INFO] Fim da etapa 1")
        return tabela

    # =========================================================
    # ETAPA 2 — checagem de arquivos
    # =========================================================
    '''
    def _etapa_02(path_arquivos: str): # Confere se há os arquivos nas pastas e retorna os status correspondentes
        arquivos = path_arquivos
        
        tabela = pd.DataFrame({
            'VERIFICAÇÃO': ['Relatório Descritivo (Vol.1)', 'Pranchas .pdf (Vol.2)', 'Arquivos Editáveis .dwg (Vol.2)', 'Relatório Justificativo (Vol.3)', 'Caderno Resposta (Vol.5)'],
            'STATUS': [ok_e2_v1, ok_e2_v2, ok_e2_v3, ok_e2_v4, ok_e2_v5]
        })

        tabela['STATUS'] = tabela['STATUS'].apply(fc.truefalse_to_vx)
        print(pasta_projeto)
        print(vol1_dir)
        print(vol2_dir)
        print(vol3_dir)
        print(vol5_dir)
        print(f"[INFO] Fim da etapa 2")
        return tabela
    '''

    # =========================================================
    # ETAPA 3 — checagem de conteúdo de relatórios
    # =========================================================
    def _etapa_03_etapa_04(arquivos: str, lista_perguntas: list) -> dict:
        '''
        etapa = os.path.basename(pasta_projeto)[0:7]

        vol1_dir = pasta_projeto / f"{etapa}1.Relatorio-do-Projeto-e-Documentos-de-Licitacao"
        vol2_dir = pasta_projeto / f"{etapa}2.Projeto-de-Execucao"
        vol3_dir = pasta_projeto / f"{etapa}3.Memoria-Justificativa"

        arquivos_pdf = [p.stem for p in vol1_dir.glob("*.pdf")]
        print(pasta_projeto)
        print(vol1_dir)
        print(arquivos_pdf)
        '''

        respostas = {}

        if arquivos:
            for arquivo in arquivos:
                respostas[arquivo] = issuesIA.perguntas_IA(arquivo, lista_perguntas)
                print(f"[INFO] Fim das perguntas de IA")
        
        print(f"[INFO] Fim da etapa 3")
        return respostas

    # ===== Main =====
    def principal():
        print(f"[INFO] RAP utilizado: {rap_path}")

        # Cálculo de índices

        # etapa 1
        e1_tabela = _etapa_01(rap_path)
        e1_tot= len(e1_tabela)
        e1_ap= list(e1_tabela['CONDIÇÃO']).count("Aprovado")
        e1_rs= list(e1_tabela['CONDIÇÃO']).count("Aprovado com Ressalva")
        e1_rp= list(e1_tabela['CONDIÇÃO']).count("Reprovado")
        e1_pct = round(100 * (e1_ap + e1_rs) / e1_tot, 1)

        '''
        e2_tabela = _etapa_02(PATH_DIR_PROJ)
        e2_tot= len(e2_tabela)
        e2_ap= list(e2_tabela['STATUS']).count("✔")
        e2_rp= list(e2_tabela['STATUS']).count("✖")
        e2_pct = round(100 * (e2_ap) / e2_tot, 1)
        '''

        perguntas_IA = [
            "O documento apresenta informações sobre seção transversal tipo?",
            "O documento apresenta um Mapa de Situação?",
            "O documento possui Anotação de Responsabilidade Técnica (ART)?",
            "O documento apresenta quadro de características técnicas e operacionais?",
            "O projeto planimétrico, ou em planta, está na escala de 1:2000?"
        ]
        respostas_IA = _etapa_03_etapa_04(arquivos, perguntas_IA)
    
        conf_geral = round((e1_pct) / 1, 1)
        print('conf_geral: ' + conf_geral)

        for relatorio in respostas_IA.keys():
            nome_saida = fc.prox_versao(PATH_OUTPUT_DIR, str(datetime.now().year), br, "ETRC", lote)
            print('nome de saída: ' + nome_saida)

            pdf_path = os.path.join(PATH_OUTPUT_DIR, nome_saida + '.pdf')
            print('pdf path: ' + pdf_path)

            # print(perguntas_IA)
            print('respostas: \n' + respostas_IA)

            print('Dados para relatório pdf \n\n')
            print('pdf_path: ' + pdf_path)
            print('relatório: ' + relatorio)
            print('e1_tabela: ' + e1_tabela)
            print('e1_ap: ' + e1_ap)
            print('e1_tot: ' + e1_tot)
            print('e1_rs: ' + e1_rs)
            print('e1_rp: ' + e1_rp)
            print('e1_pct: ' + e1_pct)
            print('e3_perguntas: ' + perguntas_IA)
            print('e3_respostas: ' + respostas_IA)
            Template_pdf_estudo.gerar_pdf(
                pdf_path = pdf_path, 
                disciplina = 'Estudo de Traçado', 
                relatorio_de_analise = relatorio,
                conf_geral=str(conf_geral) + "%",

                e1_tabela = e1_tabela,
                e1_ap=e1_ap,
                e1_tot=e1_tot,
                e1_rs=e1_rs,
                e1_rp=e1_rp,
                e1_pct=e1_pct,

                e3_perguntas = perguntas_IA,
                e3_respostas = respostas_IA[relatorio]
                )
    principal()