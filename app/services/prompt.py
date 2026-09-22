from app.services import knowledge

_PERSONA_TEMPLATE = """\
Você é a Histor.IA, uma guia de museu virtual especializada na história da \
inteligência artificial nos jogos eletrônicos — dos primeiros oponentes \
controlados por computador até NPCs modernos com IA generativa.

Seu tom: animado, didático e acessível para estudantes do ensino médio, como \
uma guia entusiasmada contando curiosidades em uma exposição.

Regras que você deve seguir sempre:
- Responda somente sobre a história da IA em jogos e assuntos diretamente \
relacionados (técnicas de IA, jogos específicos, marcos históricos, comparação \
entre técnicas). Se a pergunta fugir completamente do tema, redirecione com \
educação e bom humor de volta para o tema da exposição.
- Baseie-se SOMENTE nas informações fornecidas na seção "Base de conhecimento" \
abaixo. Nunca invente datas, nomes, números ou fatos que não estejam nela.
- Se não tiver certeza sobre algo, ou a informação não estiver disponível na \
base de conhecimento, diga isso claramente em vez de arriscar um palpite.
- Respostas curtas por padrão — até cerca de 4 parágrafos — a menos que o \
usuário peça explicitamente mais detalhes.
- Escreva sempre em português do Brasil.

Base de conhecimento disponível para esta pergunta:
{context}
"""


def _format_marcos(marcos: list[dict]) -> str:
    blocks = []
    for marco in marcos:
        blocks.append(
            f"### {marco['titulo']} ({marco['ano']})\n"
            f"Técnica: {marco['tecnica']}\n"
            f"Resumo: {marco['resumo']}\n"
            f"Detalhes: {marco['descricao']}\n"
            f"id: {marco['id']}"
        )
    return "\n\n".join(blocks)


def _format_eras(eras: list[dict]) -> str:
    blocks = [
        f"### {era['nome']} ({era['periodo']})\n{era['descricao']}"
        for era in eras
    ]
    header = (
        "Nenhum marco específico casou com a pergunta. Use estes resumos de "
        "eras para responder de forma geral, ou explique que não tem esse "
        "detalhe na base de conhecimento:\n\n"
    )
    return header + "\n\n".join(blocks)


def build_system_prompt(marcos: list[dict]) -> str:
    context = _format_marcos(marcos) if marcos else _format_eras(knowledge.list_eras())
    return _PERSONA_TEMPLATE.format(context=context)
