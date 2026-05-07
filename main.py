from parser import tokenize, parse_multiplas_queries as parse, validar_schema, gerar_grafo_networkx,gerar_algebra_relacional
from data import bd
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
import json

if __name__ == "__main__":
    queries_para_testar = (
        "SELECT idCategoria FROM Categoria;"
        
        "SELECT Nome FROM Produto "
        "WHERE idProduto = 2 AND idProduto = 3;"
        
        "SELECT Nome, Email FROM Cliente INNER JOIN Endereco ON Cliente.idCliente = Endereco.Cliente_idCliente INNER JOIN TipoCliente ON Cliente.TipoCliente_idTipoCliente = TipoCliente.idTipoCliente WHERE TipoCliente.idTipoCliente = 2 INNER JOIN ;"
    )

    try:
        tokens = tokenize(queries_para_testar)
        lista_de_queries = parse(tokens)
        
        validar_schema(lista_de_queries, bd)
        
        # print("✅ Sucesso: Todas as colunas e tabelas existem no banco de dados!")
        
        print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))
        for idx, query_data in enumerate(lista_de_queries):
                G, plano = gerar_grafo_networkx(query_data, bd)
                
                for i, passo in enumerate(plano, 1):
                  print(f"{i}. {passo}")

                
                for node in G.nodes():

                    G.nodes[node]['shape'] = 'box'

                    G.nodes[node]['color'] = {
                        'background': '#dbeafe', 
                        'border': '#38bdf8',
                    }
                    
                    # Fonte e tamanho mínimo
                    G.nodes[node]['font'] = {'size': 16, 'face': 'Segoe UI','multi': 'html'}
                    texto_atual = G.nodes[node].get('label', str(node))
                    G.nodes[node]['label'] = f"<b>{texto_atual}"
                    G.nodes[node]['widthConstraint'] = {'minimum': 160}
                    G.nodes[node]['heightConstraint'] = {'minimum': 60}
                    G.nodes[node]['margin'] = 15 
                    G.nodes[node]['borderWidth'] = 2
                
                net = Network(height="800px", width="100%", directed=True)

                net.from_nx(G)
                
                net.set_options("""
                var options = {
                "interaction": {
                    "selectable": false,
                    "dragNodes": false,
                    "dragView": true,
                    "zoomView": true
                },              
                "edges": {
                    "smooth": {
                    "type": "cubicBezier",
                    "forceDirection": "vertical",
                    "roundness": 0.4
                    }
                },
                "layout": {
                    "hierarchical": {
                    "enabled": true,
                    "direction": "DU",
                    "sortMethod": "directed",
                    "levelSeparation": 200,
                    "nodeSpacing": 300
                    }
                },
                "physics": {
                    "enabled": false
                }
                }
                """)
                
                # Salva e abre o ficheiro HTML
                ficheiro_saida = f"grafo_query_{idx + 1}.html"
                net.show(ficheiro_saida, notebook=False)
                print(f"✅ Grafo atualizado: {ficheiro_saida}")
       
    except Exception as e:
        print(f"❌ Erro de validação: {e}")