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

    if i < len(tokens) and tokens[i].valor == "INNER":
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

        # Idificador da esquerda
        if tokens[i].tipo != TokenType.IDENTIFIER:
            raise Exception("Esperado identificador no JOIN")
        left = tokens[i].valor
        i += 1

        # Operador
        if tokens[i].tipo != TokenType.OPERATOR or tokens[i].valor != "=":
            raise Exception("JOIN deve usar operador '='")
        op = tokens[i].valor
        i += 1

        # Identificador da direita
        if tokens[i].tipo != TokenType.IDENTIFIER:
            raise Exception("Esperado identificador no JOIN")
        right = tokens[i].valor
        i += 1

        joins.append({
            "table": table,
            "on": {
                "left": left,
                "op": op,
                "right": right
            }
        })
    if i > (len(tokens) -1) or tokens[i].valor not in [ "WHERE",";"]:
        raise Exception("Esperado 'WHERE' ou ';'")

    # WHERE (opcional) c suporte a ands
    where_condicoes = []
    
    if i < len(tokens) and tokens[i].valor == "WHERE":
        i += 1

        while i < len(tokens):
            # Identificador (agora aceita "tabela.coluna" vindo do lexer)
            if tokens[i].tipo != TokenType.IDENTIFIER:
                raise Exception(f"Esperado identificador no WHERE, mas encontrou {tokens[i].valor}")
            
            left = tokens[i].valor  # Ex: "Cliente.Nome" ou "Nome"
            i += 1

            # Operador
            if tokens[i].tipo != TokenType.OPERATOR:
                raise Exception("Esperado operador")
            op = tokens[i].valor
            i += 1

            # Direita (Valor ou outra coluna)
            if tokens[i].tipo not in (TokenType.NUMBER, TokenType.IDENTIFIER):
                raise Exception("Esperado valor ou identificador no lado direito")
            right = tokens[i].valor
            i += 1

            where_condicoes.append({
                "left": left, 
                "op": op,
                "right": right
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

def gerar_grafo_networkx(query_data):
    G = nx.DiGraph()
    
    # Dicionário para rastrear onde está o fluxo de cada tabela
    # Isso permite que a gente insira o WHERE logo após o SCAN da tabela correta
    fluxos = {}

    # 1. Identificar tabelas e criar SCANS
    tabelas_envolvidas = [query_data["FROM"]]
    for j in query_data["INNER JOIN"]:
        tabelas_envolvidas.append(j["table"])

    for tab in tabelas_envolvidas:
        no_scan = f"SCAN_{tab}"
        G.add_node(no_scan, label=f"SCAN: {tab}")
        fluxos[tab] = no_scan

    # 2. Aplicar WHERE na tabela específica (Pushdown)
    if query_data["WHERE"]:
        for i, cond in enumerate(query_data["WHERE"]):
            if isinstance(cond, dict):
                left_val = cond['left']
                # Tenta descobrir de qual tabela é a coluna
                if "." in left_val:
                    tab_ref, col_ref = left_val.split(".")
                else:
                    # Se não tem ponto, assume a tabela principal (ou a primeira que encontrar)
                    tab_ref = query_data["FROM"]
                    col_ref = left_val
                
                if tab_ref in fluxos:
                    no_where = f"WHERE_{tab_ref}_{i}"
                    label_where = f"σ: {tab_ref}.{col_ref} {cond['op']} {cond['right']}"
                    G.add_node(no_where, label=label_where)
                    
                    # Conecta: SCAN -> WHERE
                    origem = fluxos[tab_ref]
                    G.add_edge(origem, no_where)
                    # Atualiza o fluxo daquela tabela: agora o ponto de saída é o WHERE
                    fluxos[tab_ref] = no_where

    # 3. Processar JOINS
    # O nó atual da tabela principal começa o encadeamento
    no_atual = fluxos[query_data["FROM"]]

    if query_data["INNER JOIN"]:
        for i, join in enumerate(query_data["INNER JOIN"]):
            tab_direita = join["table"]
            no_join = f"JOIN_OP_{i}"
            condicao = f"{join['on']['left']} = {join['on']['right']}"
            G.add_node(no_join, label=f"INNER JOIN\nON {condicao}")
            
            # Conecta a esquerda (o que já temos) e a direita (fluxo da tabela do join)
            G.add_edge(no_atual, no_join)
            G.add_edge(fluxos[tab_direita], no_join)
            
            no_atual = no_join

    # 4. Nó de SELECT (Projeção Final)
    no_select = "SELECT_OP"
    colunas = ", ".join(query_data["SELECT"])
    G.add_node(no_select, label=f"PROJECTION (π)\n[{colunas}]")
    G.add_edge(no_atual, no_select)

    return G

def parse_multiplas_queries(tokens):
    todas_as_queries = []
    i = 0
    while i < len(tokens):
        # Chamamos a lógica de parse e pegamos o objeto e onde ele parou
        resultado, proximo_i = parse(tokens, i)
        todas_as_queries.append(resultado)
        i = proximo_i
    return todas_as_queries

def validar_schema(lista_de_queries, schema_bd):
    bd_map = {t["name"]: [c["name"] for c in t["columns"]] for t in schema_bd["tables"]}
    
    for idx, query in enumerate(lista_de_queries):
        tabelas_na_query = set()
        tabelas_na_query.add(query.get("FROM"))
        for j in query.get("INNER JOIN", []):
            tabelas_na_query.add(j.get("table"))

        # ... (validações anteriores de FROM e JOIN) ...

        # 4. Validar WHERE com suporte a tabela.coluna
        if query.get("WHERE"):
            for cond in query.get("WHERE"):
                if isinstance(cond, dict):
                    col_completa = cond['left']
                    
                    if "." in col_completa:
                        tab_ref, col_ref = col_completa.split(".")
                        if tab_ref not in tabelas_na_query:
                            raise Exception(f"WHERE: Tabela '{tab_ref}' não referenciada na cláusula FROM/JOIN.")
                        if col_ref not in bd_map.get(tab_ref, []):
                            raise Exception(f"WHERE: Coluna '{col_ref}' não existe na tabela '{tab_ref}'.")
                    else:
                        # Se não tem ponto, busca em todas as tabelas da query
                        encontrada = False
                        for t in tabelas_na_query:
                            if col_completa in bd_map.get(t, []):
                                encontrada = True
                                break
                        if not encontrada:
                            raise Exception(f"WHERE: Coluna '{col_completa}' não encontrada nas tabelas da query.")