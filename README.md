# CPD-DNIT — Conferência de Projetos e Desenvolvimento

Este aplicativo desktop foi desenvolvido em **Python** para auxiliar na **gestão e verificação de projetos e estudos**.  
Ele permite registrar informações de projeto, definir diretórios e executar rotinas automáticas de verificação técnica por meio de scripts externos.
O coração do programa está na verificação de palavras-chave em relatórios de projeto/estudo colocados nas respectivas pastas da estrutura de pastas modelo.

---

## Funcionalidades Principais

- Interface gráfica moderna (CustomTkinter)
- Seleção de diretórios de projeto e de resultados
- Registro de informações básicas:
  - Processo, edital, contrato e modalidade de contratação  
  - Rodovia (BR/UF), extensão, lote e tipo de projeto  
  - Analista responsável e fase de projeto  
- Execução de scripts automáticos de verificação:
  - Os scripts são carregados dinamicamente das pastas:
    - `checks/Estudos/` (para Estudos Preliminares)
    - `checks/Projetos/` (para Projeto Básico ou Executivo)
- Exportação e armazenamento de dados em JSON (`config.json`)
- Exibição de logs e mensagens de status

---

## Interface

A aplicação possui duas telas principais:

1. **Tela Inicial**
   - Permite selecionar o diretório do projeto e preencher informações gerais.
   - Valida os campos obrigatórios e formata a BR no padrão `XXX/UF`.

2. **Painel de Verificação**
   - Permite selecionar o diretório de exportação dos resultados e o arquivo de status do RAP.
   - Lista automaticamente os scripts Python disponíveis para execução.
   - Executa os scripts em threads separadas, com barra de progresso e mensagens de sucesso ou erro.

---

## Tecnologias Utilizadas

| Biblioteca | Função |
|-------------|--------|
| **CustomTkinter** | Interface moderna em Tkinter |
| **Pillow (PIL)** | Manipulação e redimensionamento de imagens |
| **pdfplumber** | Leitura de PDFs (para verificações automatizadas) |
| **ReportLab** | Geração de relatórios PDF |
| **Pandas** | Leitura e manipulação de dados tabulares |
| **Threading** | Execução paralela de scripts |
| **JSON** | Armazenamento de parâmetros e configurações |
| **importlib** | Carregamento dinâmico de módulos Python |
| **pyinstaller** | Geração de arquivo executável a partir do projeto |

---
A geração do arquivo executável utilizando o pyinstaller se deu por meio do seguinte comando:

--onefile --noconsole app.py --add-data "checks;checks" --add-data "config.json;." --add-data "funcs;funcs" --add-data "figs;figs"
## Estrutura do Programa

cpd-dnit/
├── app.py
├── funcs/
│ └── common_functions.py
├── checks/
│ ├── Estudos/
│ │ └── E04-Topografico.py
│ └── Projetos/
│ │ └── P01-Geometrico.py
│ └── Templates/
│ │ └── fonts/
│ │ └── Template_pdf_estudo.py
│ │ └── Template_pdf_projeto.py
├── figs/
│ ├── logo_dnit_scan.jpeg
│ └── logo_dnit_scan-1x1.ico
├── bkp/
└── config.json

Descrição:

- app.py: é o script que contém o código para ativação da interface e que também ativa os scripts de verificação de projetos/estudos;
- funcs/common_functions.py: contém as funções comuns que se aplicam em cada verificação
- checks/: contém os scripts de verificação separados por pastas
- checks/Templates: contém os templates usados como modelo para a elaboração dos relatórios em PDF
- figs/: contém as imagens usadas na interface do programa
bkp/: contém os scripts usados em versões anteriores do programa. Esses scripts podem ser revisados para a recuperação de alguma lógica de programação usada anteriormente e, portanto, foram armazenados na pasta como um backup. 
- config.json: é o arquivo gerado durante a execução do script app.py e contém os dados de entrada fornecidos pelo usurário. Esses dados salvos no arquivo são utilizados posteriormente para a geração dos relatórios em PDF.

--- 
## Próximos passos:

Há uma necessidade evidente de elaboração das verificações das demais disciplinas, bem como a consolidação das palavras-chave buscadas nos relatórios de projeto/estudo.