import checks.Templates.Template_pdf_estudo as Template_pdf_estudo

pdf_path = "C:/Users/guilherme.smesquita/Desktop/Export_RAC/345-DF_LT345/Tracado\RAC-001-2026_BR-345-DF_ETRC_LT-345.pdf"
relatorio = 'C:/Users/guilherme.smesquita/Desktop/Volume 2 Estudos de Traçado Lote 1.pdf'
e1_tabela = []
conf_geral = 0

e1_ap = 1
e1_tot = 3
e1_rs = 1
e1_rp = 1
e1_pct = 66.7
perguntas_IA = ['O documento apresenta informações sobre seção transversal tipo?', 'O documento apresenta um Mapa de Situação?', 'O documento possui Anotação de Responsabilidade Técnica (ART)?', 'O documento apresenta quadro de características técnicas e operacionais?', 'O projeto planimétrico, ou em planta, está na escala de 1:2000?']

respostas_IA = {'C:/Users/guilherme.smesquita/Desktop/Anexo Relatório de Estudo de Traçado Lote 1 (6119364).pdf': ['1. Informação encontrada?\nNÃO\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: Não foi encontrada informação sobre seção transversal tipo, na página: Nenhuma\n\n3. Conclusão:\nNÃO\n', '1. Informação encontrada?\nNÃO\n\n2. Trechos comprobatórios:\nNÃO foi encontrada nenhuma informação relacionada a um Mapa de Situação nos trechos fornecidos.\n\n3. Conclusão:\nNÃO\n', '1. Informação encontrada?\nNÃO\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: Não foi encontrada, na página: N/A\n\n3. Conclusão:\nNÃO\n', '1. Informação encontrada?\nNÃO\n\n2. Trechos comprobatórios:\nNÃO foi encontrada informação sobre quadro de características técnicas e operacionais nos trechos fornecidos.\n\n3. Conclusão:\nNÃO\n', '1. Informação encontrada?\nNÃO\n\n2. Trechos comprobatórios:\nNÃO foi encontrada informação sobre a escala do projeto planimétrico nos trechos fornecidos.\n\n3. Conclusão:\nNÃO\n'], 'C:/Users/guilherme.smesquita/Desktop/Volume 2 Estudos de Traçado Lote 1.pdf': ['1. Informação encontrada?\nSIM\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: (Seção Tranversal Típica Rural - BR 156 Estaca 201+3,59 à 3.037(Implantação) 3,50m 3,50m DR. DR. 2,00m 2,00m 1 1 1,5 1 11,00m 40m 40m 80m FAIXA DE DOMÍNIO OBSERVAÇÕES: SR/AP DEPARTAMENTO NACIONAL DE INFRAESTRUTURA DE TRANSPORTESMINISTÉRIO DA INFRAESTRUTURA DNIT RODOVIA: BR-156/AP FOLHA: TRECHO: Cachoeira Santo Antônio – Front. Brasil/Guiana Francesa SUB-TRECHO: Beiradão (Laranjal do Jari) – Igarapé Água Branca ST-01 SEGMENTO: km 27,00 a km 87,10 EXTENSÃO: 60,10 Km ASSUNTO: ESCALA: ESTUDO DE TRAÇADO H=1/4000V=1/4000 3% 3%) , na página: 11\nO trecho onde a informação foi encontrada: (Seção Tranversal Típica Urbana - BR 156 Estaca 72+4,10 à 201+3,59(Implantação)), na página: 15\nO trecho onde a informação foi encontrada: (Seção Tranversal Típica Urbana - BR 156 Estaca 0 à 72+4,10 (Restauração)), na página: 14\nO trecho onde a informação foi encontrada: (Seção Tranversal Típica Urbana - BR 156), na página: 73\n\n3. Conclusão:\nSIM\n', '1. Informação encontrada?\nSIM\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: (MAPA DE SITUAÇÃO), na página: (7)\n\n3. Conclusão:\nSIM\n', '1. Informação encontrada?\nNÃO\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: Não foi encontrada menção à Anotação de Responsabilidade Técnica (ART), na página: N/A\n\n3. Conclusão:\nNÃO\n', '1. Informação encontrada?\nSIM\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: CARACTERÍTICAS PLANIMÉTRICAS<br>FREQUÊNCIA Extensão Extensão<br>RAIO (m)<br>ABSOLUTO RELATIVO (%) espiral (m) circular (m)<br>R ≤ 50 0 0,0% 0 0<br>50 < R ≤ 100 1 1,6% 40 78,768<br>100 < R ≤ 200 3 4,8% 270 300,375<br>200 < R ≤ 300 11 17,7% 1395 1558,051<br>300 < R ≤ 400 11 17,7% 1480 1925,326<br>400 < R ≤ 500 4 6,5% 560 820,866<br>500 < R ≤ 600 6 9,7% 880 1238,962<br>600 < R ≤ 700 4 6,5% 600 1621,463<br>700 < R ≤ 800 3 4,8% 445 544,89<br>800 < R ≤ 900 0 0,0% 0 0<br>900 < R ≤ 1000 1 1,6% 160 209,137<br>1000 < R ≤ 2000 17 27,4% 200 4531,569<br>R ≥ 2000 1 1,6% 0 891,255<br>TOTAL EM CURVA (m) 62 100,0% 6030 13720,662<br>, na página: 74\nO trecho onde a informação foi encontrada: CARACTERÍTICAS PLANIMÉTRICAS<br>FREQUÊNCIA Extensão Extensão<br>RAIO (m)<br>ABSOLUTO RELATIVO (%) espiral (m) circular (m)<br>R ≤ 50 0 0,0% 0 0<br>50 < R ≤ 100 0 0,0% 0 0<br>100 < R ≤ 200 1 1,7% 330,0 454,656<br>200 < R ≤ 300 10 16,9% 1395,0 1554,82<br>300 < R ≤ 400 11 18,6% 1480,0 1925,326<br>400 < R ≤ 500 4 6,8% 560,0 820,866<br>500 < R ≤ 600 7 11,9% 880,0 1238,961<br>600 < R ≤ 700 4 6,8% 600,0 1621,463<br>700 < R ≤ 800 3 5,1% 445,0 544,89<br>800 < R ≤ 900 0 0,0% 0,0 0<br>900 < R ≤ 1000 1 1,7% 160,0 209,137<br>1000 < R ≤ 2000 17 28,8% 200,0 4531,569<br>R ≥ 2000 1 1,7% 0,0 891,255<br>TOTAL EM CURVA (m) 59 100,0% 6050 13792,943<br>, na página: 76\nO trecho onde a informação foi encontrada: CARACTERÍSTICAS DA SEÇÃO TRANSVERSAL URBANA<br>CARACTERÍCIAS VALORES<br>PISTA DE ROLAMENTO ( 2 X 3,50 ) 7,00 m<br>DISPOSITIVO DE DRENAGEM ( 2 X 1,00 ) 2,00 m<br>LARGURA ACOSTAMENTO ( 2 X 2,00 ) 4,00 m<br>PLATAFORMA TOTAL ( 2 X 6,50 ) 13,00 m<br>FAIXA DE DOMÍNIO ( 2 X 40 ) 80,00 m<br>TALUDE DE CORTE (H/V) 1/1<br>TALUDE DE ATERRO (H/V) 1/1,5<br>INCLINAÇÃO TALUDE DE ROCHA (H/V) 1/8<br>ABAULAMENTO DA PISTA DE ROLAMENTO -3%<br>SUPERELEVAÇÃO MÁXIMA 8%<br>, na página: 73\n\n3. Conclusão:\nSIM\n', '1. Informação encontrada?\nSIM\n\n2. Trechos comprobatórios:\nO trecho onde a informação foi encontrada: (ESTUDO DE TRAÇADO H=1/4000V=1/400), na página: (79)\n\n3. Conclusão:\nSIM']}


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