from parser import tokenize, parse_multiplas_queries as parse

if __name__ == "__main__":
    queries_para_testar ="SELECT id, nome FROM usuarios;" \
    "SELECT nome FROM clientes WHERE idade >= 18 AND idade <= 20;" \
    "SELECT u.nome, p.titulo FROM usuarios INNER JOIN posts ON u.id = p.user_id WHERE u.ativo = 1;"
    try:
        tokens = tokenize(queries_para_testar)
        
        lista_de_queries = parse(tokens)
        print("\nResultado do Parse (lista_de_queries):")
        import json
        print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"Erro ao processar: {e}")
            
        print("-" * 50)