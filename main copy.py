from parser import tokenize, parse_multiplas_queries as parse
from data import bd
import networkx as nx
import json

if __name__ == "__main__":
    queries_para_testar ="SELECT idCategoria FROM Categoria;" \
    "SELECT Nome FROM Produto WHERE idade >= 18 AND idade <= 20;" \
    "SELECT Nome, Email FROM Cliente INNER JOIN posts ON Cliente.TipoCliente_idTipoCliente = TipoCliente.idTipoCliente;"
    try:
        tokens = tokenize(queries_para_testar)
        i = 0
        lista_de_queries = parse(tokens)
        while i < len(lista_de_queries):
            tabela = lista_de_queries[i]["FROM"]
            # print(tabela)
            lista_tabelas = [tabela["name"] for tabela in bd["tables"]]
            # print(lista_tabelas)
            if tabela not in lista_tabelas:
                raise Exception("Tabela não está no BD")
            j=0
            k=0
            while j < len(lista_de_queries[i]["SELECT"]):
                coluna = lista_de_queries[i]["SELECT"][k]
                # print(coluna)
                lista_colunas = []
                for t in bd["tables"]:
                    if t["name"] == tabela:
                        lista_colunas = [c["name"] for c in t["columns"]]
                        k+=1
                
                # print(lista_colunas)
                if coluna not in lista_colunas:
                    raise Exception("Coluna não está no BD")
                j+=1
            j=0
            lista_tabelas2 = []
            while  j < len(lista_de_queries[i]["INNER JOIN"]):    
                join = lista_de_queries[i]["INNER JOIN"]
                valor_tabela_left = join[0]['on']['left'].split('.')[0]
                valor_coluna_left = join[0]['on']['left'].split('.')[1]
                valor_tabela_right= join[0]['on']['right'].split('.')[0]
                valor_coluna_right= join[0]['on']['right'].split('.')[0]
                # print(valor_tabela_left)
                # print(valor_coluna_left)
                for t in bd["tables"]:
                    lista_tabelas2.append(t["name"])
                    if t["name"] == valor_tabela_left :
                        lista_colunas_left = [c["name"] for c in t["columns"]]
                    if t["name"] == valor_tabela_right :
                        lista_colunas_right = [c["name"] for c in t["columns"]]
                if valor_tabela_left not in lista_tabelas2:
                    raise Exception("Tabela do INNER JOIN não está no BD")
                if valor_tabela_right not in lista_tabelas2:
                    raise Exception("Tabela do INNER JOIN não está no BD")
                if valor_coluna_left not in lista_colunas_left:
                    raise Exception("Coluna do INNER JOIN não está no BD")
                if valor_coluna_right not in lista_colunas_right:
                    raise Exception("Coluna do INNER JOIN não está no BD")
                
                j+=1
            i+=1
        print("Colunas e tabelas existem")
        


        # print(lista_de_queries[0]["SELECT"])
        # print("\nResultado do Parse (lista_de_queries):")
        # print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"Erro ao processar: {e}")
            
        print("-" * 50)