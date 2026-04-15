from parser import tokenize, parse

if __name__ == "__main__":
    queries_para_testar = [
        "SELECT id, nome FROM usuarios",
        
        "SELECT nome FROM clientes WHERE idade >= 18 AND idade <= 20",
        
        "SELECT u.nome, p.titulo FROM usuarios INNER JOIN posts ON u.id = p.user_id WHERE u.ativo = 1"
    ]

    for sql in queries_para_testar:
        print(f"Query: {sql}")
        try:
            tokens = tokenize(sql)
            print("Tokens gerados:")
            print(tokens)
            
            ast = parse(tokens)
            print("\nResultado do Parse (AST):")
            import json
            print(json.dumps(ast, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"Erro ao processar: {e}")
            
        print("-" * 50)