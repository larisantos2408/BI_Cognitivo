from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import datetime
from huggingface_hub import InferenceClient  # ou a lib que você estiver usando
from dotenv import load_dotenv
import os

load_dotenv()

hugging_face_key = os.getenv("HUGGING_FACE_API_KEY")

app = FastAPI()

# Coloque seu token aqui (nunca compartilhe publicamente)
# token = "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"

token = hugging_face_key

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

        prompt = f"""
Você é um analista de dados.

Abaixo estão dados agregados de produção, representados pela tabela 'dados'.

Sua tarefa é analisar **somente os dados da tabela**, seguindo exatamente os passos abaixo:

1. Observe a coluna "Media_Unidades_Por_Ano_Turno" e identifique **o maior valor numérico** presente nela.
   - Depois de identificar o valor, localize **qual é o "Turno" e o "Ano" que aparecem na mesma linha desse valor**.
   - Escreva esse valor, o ano e o turno exatos, ex: A menor produção foi de [menor valor econtrada na "Media_Unidades_Por_Ano_Turno"] no [Ano respectiavo ao menor valor na "Media_Unidades_Por_Ano_Turno"]  no [Turno respectivo ao [menor valor econtrada na "Media_Unidades_Por_Ano_Turno"] e [Ano respectiavo ao menor valor na "Media_Unidades_Por_Ano_Turno"] ] e em seguida diga brevemente (em até 3 frases) o que esse dado indica.
   - **Não cite o nome da coluna na resposta.**
   - **Mantenha o ano exatamente como está nos dados.**

2. Em seguida, observe novamente a mesma coluna a "Media_Unidades_Por_Ano_Turno" e identifique **o menor valor numérico**.
   - Depois de identificar esse valor, localize **qual é o "Turno" e o "Ano" da mesma linha**.
   - Escreva esse valor, o ano e o turno exatos, ex: a maior produção foi de [maior valor econtrada na "Media_Unidades_Por_Ano_Turno"] no [Ano respectiavo ao maior valor na "Media_Unidades_Por_Ano_Turno"]  no [Turno respectivo ao [maior valor econtrada na "Media_Unidades_Por_Ano_Turno"] e [Ano respectiavo ao maior valor na "Media_Unidades_Por_Ano_Turno"] ] e diga em até 3 frases o que esse dado indicam.
   - **Não cite o nome da coluna na resposta.**
   - **Mantenha o ano exatamente como está nos dados.**

3. Ao final, escreva um pequeno parágrafo (de 1 a 3 frases) explicando **o que essa diferença entre o maior e o menor valor indica sobre o comportamento da produção**.

⚠️ Restrições obrigatórias:
- Analise apenas os dados fornecidos. Não invente, corrija ou ignore linhas.
- Use somente os valores e turnos que estiverem na tabela.
- Não coloque na reposta a palavra vendas dados são sobre produção
- Nunca troque os turnos ou anos. Nunca altere os valores.
- Nunca ignore valores de anos que parecem futuros.
- Não use a palavra "vendas". Os dados são sobre produção.
- Use apenas os turnos "manhã" e "tarde" conforme escritos.
- Não inclua a tabela na resposta.
- Não use palavras difíceis ou técnicas.
- Não use símbolos como >, < ou outros caracteres especiais.
- Não diga onde a tabela está (ex: "acima", "abaixo", etc.).
- Não escreva perguntas, comandos ou instruções.
- Use exatamente os nomes das colunas: "Ano", "Turno", "Media_Unidades_Por_Ano_Turno".
- Use português do Brasil.
- Não use frases como "com base nos dados" ou "a análise mostra". Apenas apresente os fatos.

Dados:
{media_ano_turno}
"""



        response = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )

        texto_gerado = response.choices[0].message.content

        # Substituir \n por espaço (ou outro caractere que preferir)
        #texto_gerado_limpo = texto_gerado.replace('\n', ' ')

        return {"analise": texto_gerado}


    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}