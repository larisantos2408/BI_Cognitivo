from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import datetime
from huggingface_hub import InferenceClient  # ou a lib que você estiver usando

app = FastAPI()

# Coloque seu token aqui (nunca compartilhe publicamente)
token = "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"

client = InferenceClient(token=token, model="HuggingFaceH4/zephyr-7b-beta")
# Inicializa o client do HuggingFace
#client = InferenceClient(model="HuggingFaceH4/zephyr-7b-beta")

@app.get("/analise")
def analisar_tabela():
    try:
        # 1. Carrega os dados do Excel
        caminho = r"C:\Users\Gsant\Desktop\pessoal\Estudos\BI\Lab_9_Engenharia_producao_IA\Producao-2018-2023.xlsx"
        xls = pd.ExcelFile(caminho)
        df = pd.read_excel(xls, sheet_name="Producao")

        # 2. Processa os dados
        df['Período'] = pd.to_datetime(df['Período'])
        df['Ano'] = df['Período'].dt.year
        media_ano_turno = df.groupby(['Ano', 'Turno'])["Total Unidades Produzidas"].mean().reset_index()
        media_ano_turno.rename(columns={"Total Unidades Produzidas": "Media_Unidades_Por_Ano_Turno"}, inplace=True)
        media_ano_turno['Media_Unidades_Por_Ano_Turno'] = media_ano_turno['Media_Unidades_Por_Ano_Turno'].round(0).astype(int)

        # 3. Prepara o prompt
        tabela_txt = media_ano_turno.to_string(index=False)

        prompt = f"""Você é um analista de dados.

Abaixo está uma tabela com dados agregados.

Liste de forma clara e objetiva os principais destaques:
- O maior valor, identificando onde ocorreu e o que ele indica.
- O menor valor, identificando onde ocorreu e o que ele indica.

Seja direto, com frases curtas, afirmativas e analíticas.  
Evite apenas listar números; interprete brevemente o que eles sugerem.  
Nunca escreva perguntas ou use ponto de interrogação.  
Não invente nem altere informações que não estejam visíveis nos dados.  
Não corrija ou adivinhe datas. Mesmo que o ano pareça estar no futuro, mantenha exatamente como está na tabela.  
Use português do Brasil.

Após destacar os pontos principais, escreva um parágrafo muito breve (1 ou 2 frases) explicando **o que isso pode indicar sobre o desempenho ou comportamento observado e causas**.

TABELA:

{media_ano_turno}
"""

        response = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        texto_gerado = response.choices[0].message.content

        # Substituir \n por espaço (ou outro caractere que preferir)
        #texto_gerado_limpo = texto_gerado.replace('\n', ' ')

        return {"analise": texto_gerado}


    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}