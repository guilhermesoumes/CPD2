def perguntas_IA(arquivo, lista_perguntas):
    import pymupdf4llm as pmp
    import re
    from collections import Counter
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings
    from langchain_chroma import Chroma
    import os
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    from pathlib import Path
    import subprocess
    import shutil
    from pathlib import Path

    # divisão do pdf em páginas md
    pages = pmp.to_markdown(arquivo, header= False, footer= False, page_chunks = True, show_progress=True)

    # coleta de todas as linhas do documento
    linhas = []
    for page in pages: # para cada pagina
        linhas_da_pagina = page["text"].splitlines() # extrai linhas da pagina
        
        for linha in linhas_da_pagina: # para cada linha da pagina
            linha = linha.strip() # remove espaços do início e final
            linhas.append(linha)

    # contagem de linhas repetidas
    contador = Counter(linha.strip() for linha in linhas if linha.strip()) # contar frequência de linhas não vazias
    limite = 2 # define um limite de frequência de linhas

    documents_langchain = []

    # limpeza de linhas repetidas, filtragem de linhas e construção de doc langchain
    for page in pages:
        # extração de linhas da pagina
        linhas_da_pagina = page["text"].splitlines()
        linhas_filtradas = []
        
        # filtragem de linhas
        for linha in linhas_da_pagina: # para cada linha da pagina
            linha = linha.strip() # remove espaços do início e final
            if linha and contador[linha] <= limite and len(linha) > 3: # filtra as linhas não repetidas e maiores que 3 caracteres
                linhas_filtradas.append(linha) # somente linhas filtradas


        if linhas_filtradas: # Se a página não ficou vazia após a limpeza, juntamos as linhas dela
            
            #limpeza de linhas 
            conteudo_pagina = "\n".join(linhas_filtradas) # Unimos as linhas da página com um único \n
            #conteudo_pagina = re.sub(r'\n{1}', '\n\n', conteudo_pagina)
            conteudo_pagina = re.sub(r'\n{3,}', '\n', conteudo_pagina)

            # construção dos chunks
            chunks = [
                chunk.strip()
                for chunk in conteudo_pagina.split("\n")
                if chunk.strip()
            ]

            # construção dos doc langchain
            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "page": page['metadata']['page_number']
                    }
                )
                documents_langchain.append(doc) # documents_langchain é uma lista de documentos, onde cada documento é um chunk

    # iniciar o LM Studio
    '''
    possiveis_caminhos = [
        Path.home() / "AppData/Local/Programs/LM Studio/LM Studio.exe",
        Path("C:/Program Files/LM Studio/LM Studio.exe"),
    ]

    import psutil
    def lmstudio_rodando():

        for proc in psutil.process_iter(['name']):

            try:
                if proc.info['name'] and "LM Studio" in proc.info['name']:
                    return True

            except:
                pass

        return False

    for caminho in possiveis_caminhos:
        if caminho.exists():
            if not lmstudio_rodando():

                subprocess.Popen([str(caminho)])

                print('\n\n\n\n\n')

                print("LM Studio iniciado")
            break
        else:
            print("LM Studio não encontrado")

    import time
    time.sleep(10)
    
    import requests

    try:
        r = requests.get(
            "http://127.0.0.1:1234/v1/models",
            timeout=5
        )

        #print(r.status_code)
        #print(r.text)

    except Exception as e:
        print(e)
    '''

    # Configuração dos Embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-qwen3-embedding-0.6b",
        openai_api_base="http://127.0.0.1:1234/v1",
        openai_api_key="lm-studio",
        check_embedding_ctx_length=False
    )

    # nome do arquivo sem extensão
    #nome_arquivo = Path(arquivo).stem

    import re

    nome_arquivo = Path(arquivo).stem

    nome_arquivo = re.sub(
        r'[^a-zA-Z0-9_-]',
        '_',
        nome_arquivo
    )

    #print("nome_arquivo =", nome_arquivo)

    #print("\nCriando Chroma...")
    #print("Persist:", "./" + nome_arquivo)
    #print("Qtd docs:", len(documents_langchain))


    persist_directory = Path("vectorstores") / "temp_db"

    # Apagar a collection antes de recriar
    shutil.rmtree(
        persist_directory,
        ignore_errors=True
        )

    persist_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    #print(persist_directory)

    #print("persist_directory =", persist_directory)
    #print("persist_directory absoluto =", persist_directory.resolve())
    #print("existe =", persist_directory.exists())

    print("Gerando embeddings...")
    # Criação do Vector Store no Chroma
    vector_store = Chroma.from_documents(
        documents=documents_langchain,
        embedding=embeddings,
        persist_directory=str(persist_directory)
    )

    # Configuração do Retriever com MMR
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 20,
            "fetch_k": 40,
            "lambda_mult": 0.9
        }
    )
    print("Embeddings gerados")

    # Teste de consulta do documento
    #query = "Qual a largura das faixas de aceleração no projeto geométrico?"

    prompt = ChatPromptTemplate.from_template("""
        Você é um especialista em análise de documentos técnicos de engenharia.

        Utilize EXCLUSIVAMENTE as informações presentes no contexto abaixo.

        CONTEXTO:
        {contexto}

        PERGUNTA:
        {pergunta}

        INSTRUÇÕES:
        - Não invente informações.
        - Não utilize conhecimento externo.
        - Se a informação não estiver claramente presente, responda que ela não foi encontrada.
        - Considere equivalências semânticas e terminologias técnicas relacionadas.

        FORMATO DA RESPOSTA:

        1. Informação encontrada?
        Responda apenas: SIM ou NÃO

        2. Trechos comprobatórios:
        Apresente os trechos EXATOS e a página encontrados no documento no formato:

        '''
        O trecho onde a informação foi encontrada: (trecho), na página: (página)
        '''

        3. Conclusão:
        Responda apenas:
        SIM
        ou
        NÃO
        """)
    
    llm = ChatOpenAI(
        model="google/gemma-3n-e4b",
        openai_api_base="http://127.0.0.1:1234/v1",
        openai_api_key="lm-studio",
        temperature=0
        )

    chain = (
        prompt
        | llm
        | StrOutputParser()
        )

    respostas = []
    for pergunta in lista_perguntas:
        #print("Pergunta:", pergunta)

        #teste = embeddings.embed_query(pergunta)
        #print(teste)

        #print("Embedding da pergunta OK")

        resultados = retriever.invoke(pergunta)

        contexto = ''

        for resultado in resultados:
            contexto = contexto + "Página: {" + str(resultado.metadata['page']) + "}, Conteúdo do chunk: {" + resultado.page_content + "}.\n\n"

        #print(contexto)

        resposta = chain.invoke({
            "contexto": contexto,
            "pergunta": pergunta
        })
        respostas.append(resposta)

    return respostas