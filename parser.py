import networkx as nx
class TokenType:
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    SYMBOL = "SYMBOL"

class Token:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        return f"{self.tipo}: {self.valor}"
    
def tokenize(query):
    keywords = {"SELECT", "FROM", "WHERE", "INNER JOIN", "ON", "AND"}
    operators = {"=", ">", "<", ">=", "<=", "<>"}
    symbols = {"(", ")", ",", ";"}
    
    tokens = []
    i = 0

    while i < len(query):
        c = query[i]

        if c.isspace():
            i += 1
            continue

        if i + 1 < len(query) and query[i:i+2] in operators:
            tokens.append(Token(TokenType.OPERATOR, query[i:i+2]))
            i += 2
            continue

        if c in operators:
            tokens.append(Token(TokenType.OPERATOR, c))
            i += 1
            continue

        if c in symbols:
            tokens.append(Token(TokenType.SYMBOL, c))
            i += 1
            continue

        if c.isdigit():
            j = i
            while i < len(query) and query[i].isdigit():
                i += 1
            tokens.append(Token(TokenType.NUMBER, query[j:i]))
            continue

        if c.isalpha() or c == "_":
            j = i
            while i < len(query) and (query[i].isalnum() or query[i] in "._"):
                i += 1

            word = query[j:i]

            if word.upper() in keywords:
                tokens.append(Token(TokenType.KEYWORD, word.upper()))
            else:
                tokens.append(Token(TokenType.IDENTIFIER, word))

            continue

        raise Exception(f"Caractere inválido: {c}")

    return tokens

def parse(tokens,i):
   
    inicio_query = i

    if tokens[i].valor != "SELECT":
        raise Exception("Esperado SELECT")
    
    # SELECT
    i += 1
    colunas = []
    
    while i < len(tokens) and tokens[i].valor != "FROM":
        if tokens[i].tipo == TokenType.IDENTIFIER:
            colunas.append(tokens[i].valor)
            i += 1
        else:
            raise Exception(f"Esperado nome da coluna, mas encontrou: {tokens[i].valor}")

        
        if i < len(tokens):
            if tokens[i].valor == ",":
                i += 1
                if tokens[i].valor == "FROM":
                    raise Exception("Erro de sintaxe: vírgula extra antes do FROM")
            elif tokens[i].valor == "FROM":
                continue 
            else:
                raise Exception(f"Esperado ',' ou 'FROM', mas encontrou: {tokens[i].valor}")

    # FROM
    if tokens[i].valor != "FROM":
        raise Exception("Esperado FROM")
    i += 1
    tabela = tokens[i].valor
    i += 1
    if i > (len(tokens) -1) or tokens[i].valor not in ["INNER", "WHERE",";"]:
        raise Exception("Esperado 'INNER JOIN', 'WHERE' ou ';'")

    # INNER JOIN (opcional)
    joins = []

    while i < len(tokens) and tokens[i].valor == "INNER":
        i += 1
        
        if i < len(tokens) and tokens[i].valor == "JOIN":
            i += 1
        else:
            raise Exception("Esperado 'JOIN' após 'INNER'")

        if tokens[i].tipo != TokenType.IDENTIFIER:
            raise Exception("Esperado nome de tabela no JOIN")
        table = tokens[i].valor
        i += 1

        # ON
        if tokens[i].valor != "ON":
            raise Exception("Esperado ON")
        i += 1


        if "." not in tokens[i].valor:
            raise Exception(f"JOIN exige formato 'tabela.coluna' em: {tokens[i].valor}")
        t_left, c_left = tokens[i].valor.split(".")
        i += 1


        op_join = tokens[i].valor
        i += 1

        if "." not in tokens[i].valor:
            raise Exception(f"JOIN exige formato 'tabela.coluna' em: {tokens[i].valor}")
        t_right, c_right = tokens[i].valor.split(".")
        i += 1

        joins.append({
            "table": table,
            "on": {
                "tabela_left": t_left,
                "coluna_left": c_left,
                "op": op_join,
                "tabela_right": t_right,
                "coluna_right": c_right
            }
        })
    if i > (len(tokens) -1) or tokens[i].valor not in [ "WHERE",";"]:
        raise Exception("Esperado 'WHERE' ou ';'")

    # WHERE (opcional) c suporte a ands
    where_condicoes = []
    
    if i < len(tokens) and tokens[i].valor == "WHERE":
        i += 1

        while i < len(tokens):
           
            left_val = tokens[i].valor
            if "." in left_val:
                t_where, c_where = left_val.split(".")
            else:
                t_where, c_where = None, left_val # Será inferido na validação
            
            i += 1
            op_where = tokens[i].valor
            i += 1
            right_val = tokens[i].valor
            i += 1

            where_condicoes.append({
                "tabela": t_where,
                "coluna": c_where,
                "op": op_where,
                "valor": right_val
            })

            if i < len(tokens) and tokens[i].valor == "AND":
                where_condicoes.append("AND")
                i += 1
            else:
                break
    

    if i > (len(tokens) -1) or tokens[i].valor not in [ ";"]:
        raise Exception("Esperado ';'")
    i += 1 # Pula o ";" para estar pronto para a próxima query
    trecho_original = " ".join([t.valor for t in tokens[inicio_query:i]])

    query_data = {
        "QUERY_ORIGINAL": trecho_original,
        "SELECT": colunas,
        "FROM": tabela,
        "INNER JOIN": joins,
        "WHERE": where_condicoes if where_condicoes else None
    }

    return query_data, i

# def gerar_grafo_networkx(query_data, schema_bd):
#     G = nx.DiGraph()
    
#     # Criar um mapa do banco de dados para resolver colunas sem prefixo
#     bd_map = {t["name"]: [c["name"] for c in t["columns"]] for t in schema_bd["tables"]}
   
#     tabelas_na_query = [query_data["FROM"]]
#     for j in query_data.get("INNER JOIN", []):
#         tabelas_na_query.append(j["table"])
    
#     colunas_por_tabela = {tab: set() for tab in tabelas_na_query}

#     # 1. Mapear colunas do SELECT para suas respectivas tabelas
#     for col in query_data.get("SELECT", []):
#         for tab in tabelas_na_query:
#             if col in bd_map.get(tab, []):
#                 colunas_por_tabela[tab].add(col)
#                 break

#     # 2. Mapear colunas do WHERE para suas respectivas tabelas
#     if query_data.get("WHERE"):
#         for cond in query_data["WHERE"]:
#             if isinstance(cond, dict):
#                 tab = cond.get("tabela")
#                 col = cond.get("coluna")
                
#                 if tab:
#                     if tab in colunas_por_tabela:
#                         colunas_por_tabela[tab].add(col)
#                 else:
#                     # Inferir a tabela se não foi especificada (Ex: WHERE idProduto = 2)
#                     for t in tabelas_na_query:
#                         if col in bd_map.get(t, []):
#                             colunas_por_tabela[t].add(col)
#                             cond["tabela"] = t  # Atualiza a condição para uso no grafo
#                             break

#     # 3. Mapear colunas do JOIN
#     for join in query_data.get("INNER JOIN", []):
#         c = join["on"]
#         if c["tabela_left"] in colunas_por_tabela:
#             colunas_por_tabela[c["tabela_left"]].add(c["coluna_left"])
#         if c["tabela_right"] in colunas_por_tabela:
#             colunas_por_tabela[c["tabela_right"]].add(c["coluna_right"])

#     fluxos = {}
    
#     # restrições para fazer as outras heurísticas
#     restricoes_por_tabela = {tab: 0 for tab in tabelas_na_query} # alteracao

#     for tab in tabelas_na_query:
#         # SCAN
#         no_scan = f"SCAN_{tab}"
#         G.add_node(no_scan, label=f"SCAN: {tab}")
#         no_atual = no_scan

#         # WHERE (Pushdown de Seleção σ)
#         if query_data.get("WHERE"):
#             for i, cond in enumerate(query_data["WHERE"]):
#                 if isinstance(cond, dict) and cond.get("tabela") == tab:
#                     restricoes_por_tabela[tab] += 1
#                     no_where = f"WHERE_{tab}_{i}"
#                     label_where = f"σ: {tab}.{cond['coluna']} {cond['op']} {cond['valor']}"
#                     G.add_node(no_where, label=label_where)
#                     G.add_edge(no_atual, no_where)
#                     no_atual = no_where
        
#         # PROJEÇÃO ANTECIPADA (π) - Apenas colunas úteis desta tabela
#         cols_uteis = list(colunas_por_tabela[tab])
#         if cols_uteis:
#             no_proj_ante = f"PROJ_ANTE_{tab}"
#             label_proj = f"π: {', '.join(cols_uteis)}"
#             G.add_node(no_proj_ante, label=label_proj)
#             G.add_edge(no_atual, no_proj_ante)
#             no_atual = no_proj_ante
        
#         fluxos[tab] = no_atual

#     # 4. CONECTAR JOINS (Árvore Binária)
#     juncoes_pendentes = list(query_data.get("INNER JOIN", [])) # alteracao
    
    
#     no_acumulado = fluxos[query_data["FROM"]]

#     # if query_data.get("INNER JOIN"):
#     #     for i, join in enumerate(query_data["INNER JOIN"]):
#     #         tab_dir = join["table"]
#     #         no_join = f"JOIN_OP_{i}"
            
#     #         c = join["on"]
#     #         cond_str = f"{c['tabela_left']}.{c['coluna_left']} = {c['tabela_right']}.{c['coluna_right']}"
            
#     #         G.add_node(no_join, label=f"INNER JOIN\nON {cond_str}")
#     #         G.add_edge(no_acumulado, no_join)
#     #         G.add_edge(fluxos[tab_dir], no_join)
            
#     #         no_acumulado = no_join
    
    
#     if not juncoes_pendentes:
#         no_acumulado = fluxos[query_data["FROM"]]
#     else:
#         # Heurística b/i: Começar pela tabela mais restritiva (maior número de WHEREs)
#         tabela_inicial = max(restricoes_por_tabela, key=restricoes_por_tabela.get)
#         tabelas_processadas = {tabela_inicial}
#         no_acumulado = fluxos[tabela_inicial]
        
#         ordem_joins_realizada = 0

#         while juncoes_pendentes:
#             melhor_join_idx = -1
#             melhor_tabela_nova = None
#             maior_restricao = -1

#             # Procurar a próxima junção válida
#             for idx, join in enumerate(juncoes_pendentes):
#                 c = join["on"]
#                 tab_left, tab_right = c["tabela_left"], c["tabela_right"]

#                 # Heurística ii: Evitar produto cartesiano garantindo conectividade com o que já foi processado
#                 conecta_left = tab_left in tabelas_processadas and tab_right not in tabelas_processadas
#                 conecta_right = tab_right in tabelas_processadas and tab_left not in tabelas_processadas

#                 if conecta_left or conecta_right:
#                     tabela_nova = tab_right if conecta_left else tab_left
#                     restricao_nova = restricoes_por_tabela[tabela_nova]

#                     # Heurística b: Escolher a junção que traz a tabela mais restritiva disponível
#                     if restricao_nova > maior_restricao:
#                         maior_restricao = restricao_nova
#                         melhor_join_idx = idx
#                         melhor_tabela_nova = tabela_nova

#             if melhor_join_idx != -1:
#                 # Aplica a junção selecionada (Heurística iii: Ajustar a árvore)
#                 join_escolhido = juncoes_pendentes.pop(melhor_join_idx)
#                 c = join_escolhido["on"]
#                 cond_str = f"{c['tabela_left']}.{c['coluna_left']} = {c['tabela_right']}.{c['coluna_right']}"

#                 no_join = f"JOIN_OP_{ordem_joins_realizada}"
#                 G.add_node(no_join, label=f"INNER JOIN\nON {cond_str}")

#                 # Conecta a sub-árvore acumulada com o ramo da nova tabela
#                 G.add_edge(no_acumulado, no_join)
#                 G.add_edge(fluxos[melhor_tabela_nova], no_join)

#                 no_acumulado = no_join
#                 tabelas_processadas.add(melhor_tabela_nova)
#                 ordem_joins_realizada += 1
#             else:
#                 # Fallback de segurança (caso haja erro lógico na query ou join desconexo)
#                 join_escolhido = juncoes_pendentes.pop(0)
#                 c = join_escolhido["on"]
#                 no_join = f"JOIN_OP_{ordem_joins_realizada}_FALLBACK"
#                 G.add_node(no_join, label=f"INNER JOIN\nON {c['tabela_left']}.{c['coluna_left']} = {c['tabela_right']}.{c['coluna_right']}")
#                 G.add_edge(no_acumulado, no_join)
#                 G.add_edge(fluxos[join_escolhido["table"]], no_join)
#                 no_acumulado = no_join
#                 tabelas_processadas.add(join_escolhido["table"])
#                 ordem_joins_realizada += 1

#     # 5. PROJEÇÃO FINAL (DISPLAY)
#     no_final = "SELECT_FINAL"
#     label_final = f"DISPLAY π\n[{', '.join(query_data['SELECT'])}]"
#     G.add_node(no_final, label=label_final)
#     G.add_edge(no_acumulado, no_final)

#     return G

def selecao(G, tab, query_data, no_atual, restricoes_por_tabela,plano):
    """
    Heurística a.i: Aplicar primeiro operações de seleção - reduzem o número de tuplas.
    """
    if query_data.get("WHERE"):
        for i, cond in enumerate(query_data["WHERE"]):
            if isinstance(cond, dict) and cond.get("tabela") == tab:
                restricoes_por_tabela[tab] += 1
                no_where = f"WHERE_{tab}_{i}"
                label_where = f"σ\n {cond['coluna']} {cond['op']} {cond['valor']}"
                G.add_node(no_where, label=label_where)
                G.add_edge(no_atual, no_where)
                no_atual = no_where
                # Registro no plano de execução
                plano.append(f"Aplicando filtro (σ) em {tab}")
    return no_atual

def projecao(G, tab, cols_uteis, no_atual,plano):
    """
    Heurística a.ii: Aplicar primeiro operações de projeção - reduzem o número de atributos.
    """
    cols_uteis_list = list(cols_uteis)
    if cols_uteis_list:
        no_proj_ante = f"PROJ_ANTE_{tab}"
        label_proj = f"π\n {'\n '.join(cols_uteis_list)}"
        G.add_node(no_proj_ante, label=label_proj)
        G.add_edge(no_atual, no_proj_ante)
        no_atual = no_proj_ante
        # Registro no plano de execução
        plano.append(f"Reduzindo atributos (π) da tabela {tab}")
    return no_atual

def juncoes(G, fluxos, juncoes_pendentes, query_data, restricoes_por_tabela,plano):
    """
    Heurística b: Aplicar primeiro as operações de seleção e de junção mais restritivas.
    i. reordenar os nós folha da árvore de consulta
    ii. evitar a operação de produto cartesiano
    iii. ajustar o restante da árvore de forma apropriada
    """
    tabela_base = query_data["FROM"]
    if not juncoes_pendentes:
        return fluxos[tabela_base]

    # i. Reordenar os nós folha (começar pela tabela mais restritiva, que tem mais WHEREs)
    tabela_inicial = max(restricoes_por_tabela, key=restricoes_por_tabela.get)
    tabelas_processadas = {tabela_inicial}
    no_acumulado = fluxos[tabela_inicial]
    
    ordem_joins_realizada = 0

    while juncoes_pendentes:
        melhor_join_idx = -1
        melhor_tabela_nova = None
        maior_restricao = -1

        for idx, join in enumerate(juncoes_pendentes):
            c = join["on"]
            tab_left, tab_right = c["tabela_left"], c["tabela_right"]

            # ii. Evitar produto cartesiano (garantindo que pelo menos uma das tabelas já está na árvore)
            conecta_left = tab_left in tabelas_processadas and tab_right not in tabelas_processadas
            conecta_right = tab_right in tabelas_processadas and tab_left not in tabelas_processadas

            if conecta_left or conecta_right:
                tabela_nova = tab_right if conecta_left else tab_left
                restricao_nova = restricoes_por_tabela[tabela_nova]

                # Pegar a junção mais restritiva primeiro
                if restricao_nova > maior_restricao:
                    maior_restricao = restricao_nova
                    melhor_join_idx = idx
                    melhor_tabela_nova = tabela_nova

        if melhor_join_idx != -1:
            # iii. Ajustar o restante da árvore de forma apropriada conectando o fluxo da nova tabela
            join_escolhido = juncoes_pendentes.pop(melhor_join_idx)
            c = join_escolhido["on"]
            cond_str = f"{c['coluna_left']} = {c['coluna_right']}"

            no_join = f"JOIN_OP_{ordem_joins_realizada}"
            G.add_node(no_join, label=f"INNER JOIN\nON {cond_str}")

            # Conecta sub-árvore acumulada com ramo novo
            G.add_edge(no_acumulado, no_join)
            G.add_edge(fluxos[melhor_tabela_nova], no_join)

            # Registro no plano de execução
            plano.append(f"Realizando Junção (⋈) entre o fluxo atual e {melhor_tabela_nova} via {cond_str}")

            no_acumulado = no_join
            tabelas_processadas.add(melhor_tabela_nova)
            ordem_joins_realizada += 1
        else:
            # Fallback de segurança (caso a query force um cartesiano ou esteja desconexa)
            join_escolhido = juncoes_pendentes.pop(0)
            c = join_escolhido["on"]
            no_join = f"JOIN_OP_{ordem_joins_realizada}_FALLBACK"
            G.add_node(no_join, label=f"INNER JOIN\nON {c['coluna_left']} = {c['coluna_right']}")
            G.add_edge(no_acumulado, no_join)
            G.add_edge(fluxos[join_escolhido["table"]], no_join)
            no_acumulado = no_join
            tabelas_processadas.add(join_escolhido["table"])
            ordem_joins_realizada += 1

    return no_acumulado

def gerar_grafo_networkx(query_data, schema_bd):
    G = nx.DiGraph()
    plano_execucao = []
    
    # Criar um mapa do banco de dados para resolver colunas sem prefixo
    bd_map = {t["name"]: [c["name"] for c in t["columns"]] for t in schema_bd["tables"]}
   
    tabelas_na_query = [query_data["FROM"]]
    for j in query_data.get("INNER JOIN", []):
        tabelas_na_query.append(j["table"])
    
    colunas_por_tabela = {tab: set() for tab in tabelas_na_query}

    # 1. Mapear colunas do SELECT para suas respectivas tabelas
    for col in query_data.get("SELECT", []):
        for tab in tabelas_na_query:
            if col in bd_map.get(tab, []):
                colunas_por_tabela[tab].add(col)
                break

    # 2. Mapear colunas do WHERE para suas respectivas tabelas
    if query_data.get("WHERE"):
        for cond in query_data["WHERE"]:
            if isinstance(cond, dict):
                tab = cond.get("tabela")
                col = cond.get("coluna")
                
                if tab:
                    if tab in colunas_por_tabela:
                        colunas_por_tabela[tab].add(col)
                else:
                    # Inferir a tabela se não foi especificada
                    for t in tabelas_na_query:
                        if col in bd_map.get(t, []):
                            colunas_por_tabela[t].add(col)
                            cond["tabela"] = t
                            break

    # 3. Mapear colunas do JOIN
    for join in query_data.get("INNER JOIN", []):
        c = join["on"]
        if c["tabela_left"] in colunas_por_tabela:
            colunas_por_tabela[c["tabela_left"]].add(c["coluna_left"])
        if c["tabela_right"] in colunas_por_tabela:
            colunas_por_tabela[c["tabela_right"]].add(c["coluna_right"])

    fluxos = {}
    restricoes_por_tabela = {tab: 0 for tab in tabelas_na_query}

    # Aplicação das Heurísticas A (Pushdown de Seleção e Projeção)
    for tab in tabelas_na_query:
        no_scan = f"SCAN_{tab}"
        G.add_node(no_scan, label=f"SCAN\n {tab}")
        no_atual = no_scan
        plano_execucao.append(f"Iniciando leitura (SCAN) da tabela: {tab}")

        # Heurística a.i - Seleção
        no_atual = selecao(G, tab, query_data, no_atual, restricoes_por_tabela,plano_execucao)
        
        # Heurística a.ii - Projeção Antecipada
        cols_uteis = colunas_por_tabela[tab]
        no_atual = projecao(G, tab, cols_uteis, no_atual,plano_execucao)
        
        fluxos[tab] = no_atual

    # Aplicação da Heurística B (Junções com menor número de tuplas e prevenção de Produto Cartesiano)
    juncoes_pendentes = list(query_data.get("INNER JOIN", []))
    no_acumulado = juncoes(G, fluxos, juncoes_pendentes, query_data, restricoes_por_tabela,plano_execucao)

    # 5. PROJEÇÃO FINAL (DISPLAY)
    no_final = "SELECT_FINAL"
    label_final = f"DISPLAY π\n[{', '.join(query_data['SELECT'])}]"
    G.add_node(no_final, label=label_final)
    G.add_edge(no_acumulado, no_final)
    plano_execucao.append(f"Finalizando consulta com a projeção dos campos: {', '.join(query_data['SELECT'])}")

    return G, plano_execucao

def parse_multiplas_queries(tokens):

    todas_as_queries = []
    i = 0
    while i < len(tokens):
        # Chamamos a lógica de parse e pegamos o objeto e onde ele parou
        resultado, proximo_i = parse(tokens, i)
        todas_as_queries.append(resultado)
        i = proximo_i
    return todas_as_queries

def gerar_algebra_relacional(query_data):
    """
    Gera a expressão lógica de álgebra relacional a partir do AST (query_data).
    Símbolos utilizados:
    π (Projeção / SELECT)
    σ (Seleção / WHERE)
    ⋈ (Junção / INNER JOIN)
    ∧ (E Lógico / AND)
    """
    expressao = query_data.get("FROM", "")

    # 1. INNER JOIN (⋈)
    joins = query_data.get("INNER JOIN")
    if joins:
        for join in joins:
            on = join["on"]
            cond_join = f"{on['tabela_left']}.{on['coluna_left']} {on['op']} {on['tabela_right']}.{on['coluna_right']}"
            expressao = f"({expressao} |X|({cond_join}) {join['table']})"

    # 2. WHERE (Seleção - σ)
    where = query_data.get("WHERE")
    if where:
        conds_str = ""
        for item in where:
            if isinstance(item, dict):
                # Se a tabela foi inferida ou explícita, usa o prefixo
                prefixo = f"{item['tabela']}." if item.get('tabela') else ""
                conds_str += f"{prefixo}{item['coluna']} {item['op']} {item['valor']}"
            elif item == "AND":
                conds_str += " ∧ " # Troca a string AND pelo operador lógico matemático
        
        expressao = f"σ({conds_str})({expressao})"

    # 3. SELECT (Projeção - π)
    cols = ", ".join(query_data.get("SELECT", []))
    expressao = f"π({cols})({expressao})"

    return expressao


def validar_schema(lista_de_queries, schema_bd):
    # Mapa de busca rápida: {'nome_tabela': ['coluna1', 'coluna2']}
    bd_map = {t["name"]: [c["name"] for c in t["columns"]] for t in schema_bd["tables"]}
   
    for idx, query in enumerate(lista_de_queries):
        tabelas_na_query = set()
       
        # 1. Validar Tabela Principal (FROM)
        tabela_principal = query.get("FROM")
        if tabela_principal not in bd_map:
            raise Exception(f"Query {idx+1}: Tabela principal '{tabela_principal}' não existe.")
        tabelas_na_query.add(tabela_principal)

        # 2. Validar INNER JOINs
        for join in query.get("INNER JOIN", []):
           
            tabela_join = join.get("table")
            if tabela_join not in bd_map:
                raise Exception(f"Query {idx+1}: Tabela do JOIN '{tabela_join}' não existe no banco de dados.")
            tabelas_na_query.add(tabela_join)

            
            # Validação dos pares tabela/coluna no ON
            on_cond = join['on']
            pares_para_validar = [
                (on_cond['tabela_left'], on_cond['coluna_left']),
                (on_cond['tabela_right'], on_cond['coluna_right'])
            ]

            for tab, col in pares_para_validar:
                # Verifica se a tabela mencionada existe no BD
                if tab not in bd_map:
                    raise Exception(f"JOIN: Tabela '{tab}' mencionada na condição ON não existe.")
                # Verifica se a coluna existe nessa tabela
                if col not in bd_map[tab]:
                    raise Exception(f"JOIN: Coluna '{col}' não existe na tabela '{tab}'.")


        # 3. Validar Colunas do SELECT
        for coluna in query.get("SELECT", []):
            encontrada = False

            for t in tabelas_na_query:
                if coluna in bd_map[t]:
                    encontrada = True
                    break
            if not encontrada:
                raise Exception(f"SELECT: Coluna '{coluna}' não encontrada nas tabelas {tabelas_na_query}.")

        # 4. Validar WHERE (com suporte a Pushdown no Grafo)
        if query.get("WHERE"):
            for cond in query.get("WHERE"):
                if isinstance(cond, dict):
               
                    tab_ref = cond.get('tabela')
                    col_ref = cond.get('coluna')
                    
                    if tab_ref: # Se a tabela foi especificada
                        if tab_ref not in tabelas_na_query:
                            raise Exception(f"WHERE: Tabela '{tab_ref}' não referenciada na query.")
                        if col_ref not in bd_map.get(tab_ref, []):
                            raise Exception(f"WHERE: Coluna '{col_ref}' não existe na tabela '{tab_ref}'.")
                    else:
                        # Se a tabela for None (inferência), busca em todas as tabelas da query
                        encontrada = False
                        for t in tabelas_na_query:
                            if col_ref in bd_map.get(t, []):
                                encontrada = True
                                break

                        if not encontrada:
                            raise Exception(f"WHERE: Coluna '{col_ref}' não encontrada.")