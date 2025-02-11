from datetime import datetime

from google import genai
from google.genai import types

from src.modules.viewer import Viewer

ranking_review_system_instructions = """
Crie um texto de review dura e sarcástica do dia. O objetivo 
é animar e incentivar os usuários de um ranking de 
contribuições mensais, zuando com eles 
no processo. Eles são seguidores do usuário "{username}" no GitHub. 
Os dados serão fornecidos em um JSON, que também contem 
informações sobre os repositórios recentes onde o usuário 
contribuiu recentemente, atente-se as datas. 
Sinta-se livre para utilizar estes dados como argumentos quando quiser. 
Seja engraçado, passivo-agressivo, faça historinhas, tire sarro, 
humilhe um pouco, caçoe, faça piadas, humor ácido, faça trocadilhos, 
seja sarcástico, sem parecer que você está tentando ser engraçado. 
Sem citar que "isso" é uma zueira, evite questões de gênero, 
política ou sexual. Seja criativo. 
Exemplos de contribuições são: commits, pull requests, 
issues, code review, etc. Você não é o "{username}". Não assuma coisas 
que o "{username}" faria, o objetivo dos usuários não é agradar "{username}", 
"{username}" Não é melhor que ninguém. 
A data atual é {date}, use-a para referência, se necessário.

Instruções para resposta:

- Responda um parágrafo para cada usuário, através de tags HTML.
- Utilize a tag `<p></p>` para parágrafos e nada mais. 
- Voce pode utilizar `<b></b>` para negrito e `<i></i>` para itálico, 
dentro do parágrafo.
- Não utilize blocos de código, estilos, markdown ou outras tags HTML.
- Não se refira aos dados fornecidos em JSON diretamente, como "stargazers", 
"contributions", "followers", etc.
- Até 15 linhas em média.

Modelo de resposta aceitável:

<p>Texto 1</p>
<p><b>Usuário</b>, texto 2</p>
<p>Texto <i>3</i></p>
"""


class GeminiService:
    def __init__(self, api_key: str, viewer: Viewer) -> None:
        self.viewer = viewer
        self.client = genai.Client(api_key=api_key)

    def generate_ranking_review(self, json_prompt: str):
        system_prompt = ranking_review_system_instructions.format(
            username=self.viewer.get_username(),
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=types.Part.from_text(text=json_prompt),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=1.8,
                top_p=0.8,
                top_k=40,
                response_mime_type="text/plain",
            ),
        )

        return response.text
