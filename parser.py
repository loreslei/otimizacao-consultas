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

def parse(tokens):
    i = 0

    if tokens[i].valor != "SELECT":
        raise Exception("Esperado SELECT")
    
    # SELECT
    i += 1
    colunas = []
    while tokens[i].valor != "FROM":
        if tokens[i].valor != ",":
            colunas.append(tokens[i].valor)
        i += 1

    # FROM
    if tokens[i].valor != "FROM":
        raise Exception("Esperado FROM")
    i += 1
    tabela = tokens[i].valor
    i += 1

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

    # WHERE (opcional) c suporte a ands
    where_condicoes = []
    
    if i < len(tokens) and tokens[i].valor == "WHERE":
        i += 1

        while i < len(tokens):
            # esquerdita
            if tokens[i].tipo != TokenType.IDENTIFIER:
                raise Exception("Esperado identificador")
            left = tokens[i].valor; i += 1

            # operadorzito
            if tokens[i].tipo != TokenType.OPERATOR:
                raise Exception("Esperado operador")
            op = tokens[i].valor; i += 1

            # derecha
            if tokens[i].tipo not in (TokenType.NUMBER, TokenType.IDENTIFIER):
                raise Exception("Esperado valor")
            right = tokens[i].valor; i += 1

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

    return {
        "SELECT": colunas,
        "FROM": tabela,
        "INNER JOIN": joins,
        "WHERE": where_condicoes if where_condicoes else None
    }

