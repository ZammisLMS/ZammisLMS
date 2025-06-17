categorias = {
    "alimentação": ["picolé", "lanche", "mercado", "pizza", "almoço", "jantar", "restaurante", "comida", "bebida", "padaria", "sorvete", "doce"],
    "transporte": ["uber", "ônibus", "gasolina", "combustível", "passagem", "táxi", "99", "metrô", "trem", "estacionamento"],
    "moradia": ["aluguel", "luz", "água", "condomínio", "internet", "gás", "iptu", "manutenção casa"],
    "lazer": ["cinema", "bar", "parque", "show", "festa", "viagem", "jogo", "livro", "streaming", "hobby"],
    "saúde": ["farmácia", "remédio", "consulta", "médico", "hospital", "plano de saúde"],
    "educação": ["curso", "livros", "material escolar", "faculdade", "escola"],
    "vestuário": ["roupa", "calçado", "acessório", "camisa"],
    "outros": [] # Default category
}

def categorizar_gasto(descricao: str) -> str:
    if not descricao:
        return "outros"

    descricao_lower = descricao.lower()
    for categoria, palavras_chave in categorias.items():
        for palavra in palavras_chave:
            if palavra.lower() in descricao_lower: # ensure keyword is also lowercased for comparison
                return categoria
    return "outros"

if __name__ == '__main__':
    # Test cases
    testes = {
        "Compra de picolé na esquina": "alimentação",
        "Gasolina para o carro": "transporte",
        "Aluguel do apartamento": "moradia",
        "Cinema com amigos": "lazer",
        "Remédio para dor de cabeça": "saúde",
        "Curso de Python": "educação",
        "Camisa nova": "vestuário",
        "Conta de luz": "moradia", # Test specific keyword
        "Pagamento do IPTU": "moradia",
        "Viagem para a praia": "lazer",
        "Consulta médica": "saúde",
        "Livro de receitas": "lazer", # "livro" is in "lazer"
        "Lanche da tarde": "alimentação",
        "Corrida de Uber": "transporte",
        "Supermercado do mês": "alimentação",
        "Show do U2": "lazer",
        "Streaming de música": "lazer",
        "Manutenção do PC": "outros",
        "Investimento em ações": "outros",
        "": "outros",
        "Café da manhã na padaria": "alimentação",
        "manutenção casa": "moradia" # Test "manutenção casa"
    }

    print("Executando testes para categorizar_gasto...")
    all_passed = True
    for desc, cat_esperada in testes.items():
        cat_obtida = categorizar_gasto(desc)
        print(f"Descrição: '{desc}'")
        print(f"Categoria Esperada: '{cat_esperada}', Categoria Obtida: '{cat_obtida}'")
        if cat_obtida != cat_esperada:
            print(f"!!!!!! FALHA: Esperado '{cat_esperada}', Obtido '{cat_obtida}' !!!!!!")
            all_passed = False
        # assert cat_obtida == cat_esperada, f"Falha para '{desc}': Esperado '{cat_esperada}', Obtido '{cat_obtida}'"
        print("-" * 30)

    if all_passed:
        print("Todos os testes de categorizar_gasto passaram!")
    else:
        print("!!!!!! Alguns testes de categorizar_gasto FALHARAM! !!!!!!")
