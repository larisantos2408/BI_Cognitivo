from openai import OpenAI
import pandas as pd
import requests  # Adicionado para verificação de conexão


from dotenv import load_dotenv
import os

load_dotenv()

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

# Configuração do cliente DeepSeek
client = OpenAI(
    api_key= deepseek_api_key,  # Substitua pela sua chave válida
    base_url="https://api.deepseek.com/v1",  # URL correta com versão da API
)

def verificar_conexao():
    try:
        # Testa conexão com um endpoint público para verificar internet
        test_url = "https://www.google.com"
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            # Testa especificamente a API DeepSeek
            api_test = requests.get("https://api.deepseek.com", timeout=5)
            return api_test.status_code in [200, 404, 403]  # 404/403 significa que o endpoint existe
        return False
    except:
        return False

def chamar_deepseek(prompt):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
            timeout=30  # Aumente o timeout se necessário
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na API: {str(e)}"


def carregar_dados():
    caminho = r"C:\Users\Gsant\Desktop\pessoal\Estudos\BI\Lab_9_Engenharia_producao_IA\Producao-2018-2023.xlsx"
    xls = pd.ExcelFile(caminho)
    df = pd.read_excel(xls, sheet_name="Producao")
    return df

def processar_dados(df):
    df['Período'] = pd.to_datetime(df['Período'])
    df['Ano'] = df['Período'].dt.year
    media_ano_turno = df.groupby(['Ano', 'Turno'])["Total Unidades Produzidas"].mean().reset_index()
    media_ano_turno.rename(columns={"Total Unidades Produzidas": "Media_Unidades_Por_Ano_Turno"}, inplace=True)
    media_ano_turno['Media_Unidades_Por_Ano_Turno'] = media_ano_turno['Media_Unidades_Por_Ano_Turno'].round(0).astype(int)
    return media_ano_turno

def criar_prompt(media_ano_turno):
    tabela_txt = media_ano_turno.to_csv(index=False)
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

3. Ao final, escreva um pequeno parágrafo (de 1 a 3 frases) explicando o que essa diferença entre o maior e o menor valor indica sobre o comportamento da produção.

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
{tabela_txt}
"""
    return prompt

def chamar_deepseek(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",  # Modelo do DeepSeek (equivalente ao GPT-3.5 Turbo)
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.3,
    )
    return response.choices[0].message.content

def main():
    print("Testando conexão com a internet...")
    if not verificar_conexao():
        print("\n❌ Falha na conexão. Verifique:")
        print("1. Sua conexão com a internet")
        print("2. Firewall/antivírus (pode estar bloqueando)")
        print("3. Proxy corporativo (se aplicável)")
        print("\nDica: Tente acessar https://api.deepseek.com no navegador")
        return

    print("\n✅ Conexão OK. Processando dados...")
    
    try:
        df = carregar_dados()
        media_ano_turno = processar_dados(df)
        prompt = criar_prompt(media_ano_turno)
        
        print("\nEnviando prompt para a API...")
        resultado = chamar_deepseek(prompt)
        print("\nResposta da API:")
        print(resultado)
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")

if __name__ == "__main__":
    main()