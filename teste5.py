import subprocess
import json

def modelo_instalado(modelo_id):
    resultado = subprocess.run(
        ["lms", "ls", "--json"],
        capture_output=True,
        text=True,
        check=True
    )

    modelos = json.loads(resultado.stdout)

    return any(
        modelo_id.lower() in str(item).lower()
        for item in modelos
    )

def garantir_modelo(modelo_id):
    if modelo_instalado(modelo_id):
        print("Modelo já instalado.")
        return

    print("Baixando modelo...")
    subprocess.run(
        ["lms", "get", modelo_id, "--yes"],
        check=True
    )

garantir_modelo("https://huggingface.co/Qwen/Qwen3-Embedding-4B-GGUF")