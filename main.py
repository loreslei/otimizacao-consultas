from parser import tokenize, parse_multiplas_queries as parse, validar_e_gerar_grafos
from data import bd
import networkx as nx
import json

if __name__ == "__main__":
    queries_para_testar = (
        "SELECT idCategoria FROM Categoria;"
        "SELECT Nome FROM Produto WHERE idade >= 18 AND idade <= 20;"
        "SELECT Nome, Email FROM Cliente INNER JOIN TipoCliente ON Cliente.TipoCliente_idTipoCliente = TipoCliente.idTipoCliente;"
    )

    try:
        tokens = tokenize(queries_para_testar)
        lista_de_queries = parse(tokens)
        
        validar_e_gerar_grafos(lista_de_queries, bd)
        
        print("✅ Sucesso: Todas as colunas e tabelas existem no banco de dados!")
        # print(json.dumps(lista_de_queries, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Erro de validação: {e}")