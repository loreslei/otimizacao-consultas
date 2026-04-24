from parser import tokenize, parse_multiplas_queries as parse, validar_schema, gerar_grafo_networkx
from data import bd
import matplotlib.pyplot as plt
import networkx as nx
import json

if __name__ == "__main__":
    queries_para_testar = (
        "SELECT idCategoria FROM Categoria;"
        
        "SELECT Nome FROM Produto "
        "WHERE idProduto = 2 AND idProduto = 3;"
        
        "SELECT Nome, Email FROM Cliente "
        "INNER JOIN Endereco ON Cliente.idCliente = Endereco.Cliente_idCliente "
        "INNER JOIN TipoCliente ON Cliente.TipoCliente_idTipoCliente = TipoCliente.idTipoCliente "
        "WHERE TipoCliente.idTipoCliente = 2;"
    )

    try:
        tokens = tokenize(queries_para_testar)
        lista_de_queries = parse(tokens)
        
        validar_schema(lista_de_queries, bd)
        
        # print("✅ Sucesso: Todas as colunas e tabelas existem no banco de dados!")
        
        print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))

        # Gerar e desenhar o grafo para cada query
        for idx, query_data in enumerate(lista_de_queries):
            # print(f"Gerando grafo para a Query {idx + 1}...")
            

            G = gerar_grafo_networkx(query_data, bd)
            
            plt.figure(figsize=(10, 6))
            
            pos = nx.planar_layout(G) 
            

            labels = nx.get_node_attributes(G, 'label')
            
            nx.draw(G, pos, with_labels=True, labels=labels, 
                    node_size=3000, node_color="lightgreen", 
                    font_size=6, font_weight="bold", 
                    arrows=True, edge_color="gray")
            
            plt.title(f"Grafo de Operadores - Query {idx + 1}")
            plt.show()

    except Exception as e:
        print(f"❌ Erro de validação: {e}")