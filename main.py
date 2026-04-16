from parser import tokenize, parse_multiplas_queries as parse
from data import bd
import networkx as nx
import json

if __name__ == "__main__":
    queries_para_testar ="SELECT idCategoria2 FROM Categoria;" \
    "SELECT nome FROM Produto WHERE idade >= 18 AND idade <= 20;" \
    "SELECT u.nome, p.titulo FROM usuarios INNER JOIN posts ON u.id = p.user_id WHERE u.ativo = 1;"
    try:
        tokens = tokenize(queries_para_testar)
        i = 0
        lista_de_queries = parse(tokens)
        while i < len(lista_de_queries):
            tabela = lista_de_queries[i]["FROM"]
            print(tabela)
            lista_tabelas = [tabela["name"] for tabela in bd["tables"]]
            print(lista_tabelas)
            if tabela not in lista_tabelas:
                raise Exception("Tabela não está no BD")
            # while len():
            #     coluna = lista_de_queries[0]["SELECT"][0]
            #     print(coluna)
            #     lista_colunas = []
            #     for t in bd["tables"]:
            #         if t["name"] == tabela:
            #             lista_colunas = [c["name"] for c in t["columns"]]
            #             break
                
            #     print(lista_colunas)
            #     if coluna not in lista_colunas:
            #         raise Exception("Coluna não está no BD")
                
            i+=1
           
        


        # print(lista_de_queries[0]["SELECT"])
        # print("\nResultado do Parse (lista_de_queries):")
        # print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"Erro ao processar: {e}")
            
        print("-" * 50)