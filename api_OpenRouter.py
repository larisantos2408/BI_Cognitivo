from flask import Flask, Response
import requests
import pandas as pd
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Cria a instância do Flask
app = Flask(__name__)

# Carrega as variáveis do arquivo .env
load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Obtém a chave da variável de ambiente
OPENROUTER_API_KEY = openrouter_api_key
OPENROUTER_REFERER = "https://localhost"
OPENROUTER_TITLE = "Power BI Integration"

@app.route('/analise', methods=['GET'])
def gerar_analise():
    try:
        # Carrega e processa os dados
        caminho = r"C:\Users\Gsant\Desktop\pessoal\Estudos\BI\Lab_9_Engenharia_producao_IA\Producao-2018-2023.xlsx"
        df = pd.read_excel(caminho, sheet_name="Producao")
        df['Período'] = pd.to_datetime(df['Período'])
        df['Ano'] = df['Período'].dt.year
        media_ano_turno = df.groupby(['Ano', 'Turno'])["Total Unidades Produzidas"].mean().reset_index()
        media_ano_turno.rename(columns={"Total Unidades Produzidas": "Media_Unidades_Por_Ano_Turno"}, inplace=True)
        media_ano_turno['Media_Unidades_Por_Ano_Turno'] = media_ano_turno['Media_Unidades_Por_Ano_Turno'].round(0).astype(int)

        # Cria o prompt
        prompt = f"""
        Você é um analista de dados.

        Abaixo estão dados agregados de produção, representados pela tabela 'dados'.

        Sua tarefa é analisar somente os dados da tabela, seguindo exatamente os passos abaixo:

        1. Observe a coluna "Media_Unidades_Por_Ano_Turno" e identifique o maior valor numérico presente nela.
        - Depois de identificar o valor, localize qual é o "Turno" e o "Ano" que aparecem na mesma linha desse valor.
        - Escreva esse valor, o ano e o turno exatos, e em seguida diga brevemente (em até 3 frases) o que esse dado indica.
        - Não cite o nome da coluna na resposta.
        - Mantenha o ano exatamente como está nos dados.

        2. Em seguida, observe novamente a mesma coluna e identifique o menor valor numérico.
        - Depois de identificar esse valor, localize qual é o "Turno" e o "Ano" da mesma linha.
        - Escreva esse valor, o ano e o turno exatos, e diga em até 3 frases o que esse dado indica.
        - Não cite o nome da coluna na resposta.
        - Mantenha o ano exatamente como está nos dados.

        3. Ao final, escreva um pequeno parágrafo (de 2 a 5 frases) explicando o que essa diferença entre o maior e o menor valor indica sobre o comportamento da produção, e quais as posíveis causas e de dicas mais detalhada do que pode ser feito e como fazer, exemplos do que fazer de até no maxímo 5 frases.

        ⚠️ Restrições obrigatórias:
        - Analise apenas os dados fornecidos. Não invente, corrija ou ignore linhas.
        - Use somente os valores e turnos que estiverem na tabela.
        - Nunca troque os turnos ou anos. Nunca altere os valores.
        - Nunca ignore valores de anos que parecem futuros.
        - Não use a palavra "vendas". Os dados são sobre produção.
        - Use apenas os turnos "manhã" e "tarde" conforme escritos.
        - Não inclua a tabela na resposta.
        - Não use palavras difíceis ou técnicas.
        - Não use símbolos como >, < ou outros caracteres especiais.
        - Não diga onde a tabela está (ex: "acima", "abaixo", etc.).
        - Não escreva perguntas, comandos ou instruções.
        - Use exatamente os nomes das colunas "Ano", "Turno", "Media_Unidades_Por_Ano_Turno" apenas para análise, não na resposta.
        - Use português do Brasil.
        - Não use frases como "com base nos dados" ou "a análise mostra". Apenas apresente os fatos.

        Dados:
        {media_ano_turno.to_csv(index=False)}
        """

        # Chama a API do DeepSeek
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": OPENROUTER_REFERER,
            "X-Title": OPENROUTER_TITLE
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600
            }
        )

        # Extrai o texto da resposta (já decodificado)
        texto_resposta = response.json()["choices"][0]["message"]["content"]

        def formatar_resposta(texto):
            return texto.replace('\n', ' ')


        # Formata a resposta
        texto_formatado = formatar_resposta(texto_resposta)

        # Formata a resposta para evitar dupla codificação
        resposta_final = {
            "analise": texto_formatado,
            "status": "sucesso"
        }

        # Retorna como JSON sem codificação adicional
        return Response(
            json.dumps(resposta_final, ensure_ascii=False),  # 👈 ensure_ascii=False é a chave!
            mimetype='application/json; charset=utf-8'  # Força UTF-8
        )

    except Exception as e:
        return Response(
            json.dumps({"erro": str(e), "status": "falha"}, ensure_ascii=False),
            status=500,
            mimetype='application/json; charset=utf-8'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)