from parser import tokenize, parse_multiplas_queries as parse
from data import bd
import networkx as nx
import json

if __name__ == "__main__":
    queries_para_testar ="SELECT id, nome FROM usuarios;" \
    "SELECT nome FROM clientes WHERE idade >= 18 AND idade <= 20;" \
    "SELECT u.nome, p.titulo FROM usuarios INNER JOIN posts ON u.id = p.user_id WHERE u.ativo = 1;"
    try:
        tokens = tokenize(queries_para_testar)

        lista_de_queries = parse(tokens)
        tabela = lista_de_queries[0]["FROM"]
        print(tabela)
        lista_tabelas = [tabela["name"] for tabela in bd["tables"]]
        print(lista_tabelas)
        if tabela not in lista_tabelas:
           print('erro, não está no bd')
        # print(lista_de_queries[0]["SELECT"])
        # print("\nResultado do Parse (lista_de_queries):")
        # print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"Erro ao processar: {e}")
            
        print("-" * 50)