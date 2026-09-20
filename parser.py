# parser.py
from lexer import TokenType
from ast_nodes import (
    NumberLiteral, BooleanLiteral, Identifier, BinaryOp, Call,
    LetStatement, ExpressionStatement, IfStatement, WhileStatement,
    FunctionDeclaration, ReturnStatement, AssignStatement
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---- helpers (mismo espíritu que los del Lexer) ----
    def _current(self):
        return self.tokens[self.pos]
    
    def _peek_token(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def _at_end(self):
        return self._current().type == TokenType.EOF

    def _check(self, token_type):
        return not self._at_end() and self._current().type == token_type

    def _advance(self):
        token = self._current()
        if not self._at_end():
            self.pos += 1
        return token

    def _expect(self, token_type, mensaje):
        # Como _advance(), pero primero valida que sea el tipo esperado.
        # Si no, truena con un mensaje útil en vez de seguir a ciegas.
        if self._check(token_type):
            return self._advance()
        raise SyntaxError(f"{mensaje} (línea {self._current().line})")

    # ---- punto de entrada ----
    def parse(self):
        statements = []
        while not self._at_end():
            statements.append(self._statement())
        return statements

    # Decide qué tipo de statement viene mirando el primer token.
    # Si no es ninguna palabra clave conocida, asumimos que es una
    # expresión suelta (ej. "print(x)" como línea independiente).
    def _statement(self):
        if self._check(TokenType.LET):
            return self._let_statement()
        if self._check(TokenType.IF):
            return self._if_statement()
        if self._check(TokenType.WHILE):
            return self._while_statement()
        if self._check(TokenType.FUNCTION):
            return self._function_declaration()
        if self._check(TokenType.RETURN):
            return self._return_statement()
        if self._check(TokenType.IDENTIFIER) and self._peek_token(1).type == TokenType.EQUALS:
            name = self._advance().value
            self._advance()  # consume '='
            value = self._expression()
            return AssignStatement(name, value)
        expr = self._expression()
        return ExpressionStatement(expr)

    def _let_statement(self):
        self._advance()  # 'let'
        name = self._expect(TokenType.IDENTIFIER, "Esperaba nombre de variable después de 'let'")
        self._expect(TokenType.EQUALS, "Esperaba '=' después del nombre de variable")
        value = self._expression()
        return LetStatement(name.value, value)

    def _block(self):
        # Un bloque es { statement* } — se usa en if/while/function.
        self._expect(TokenType.LBRACE, "Esperaba '{'")
        statements = []
        while not self._check(TokenType.RBRACE) and not self._at_end():
            statements.append(self._statement())
        self._expect(TokenType.RBRACE, "Esperaba '}' para cerrar el bloque")
        return statements

    def _if_statement(self):
        self._advance()  # 'if'
        condition = self._expression()
        then_body = self._block()
        return IfStatement(condition, then_body, None)

    def _while_statement(self):
        self._advance()  # 'while'
        condition = self._expression()
        body = self._block()
        return WhileStatement(condition, body)

    def _function_declaration(self):
        self._advance()  # 'function'
        name = self._expect(TokenType.IDENTIFIER, "Esperaba nombre de función")
        self._expect(TokenType.LPAREN, "Esperaba '(' después del nombre de función")
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(self._expect(TokenType.IDENTIFIER, "Esperaba un parámetro").value)
            while self._check(TokenType.COMMA):
                self._advance()
                params.append(self._expect(TokenType.IDENTIFIER, "Esperaba un parámetro").value)
        self._expect(TokenType.RPAREN, "Esperaba ')' después de los parámetros")
        body = self._block()
        return FunctionDeclaration(name.value, params, body)

    def _return_statement(self):
        self._advance()  # 'return'
        value = self._expression()
        return ReturnStatement(value)

    # ---- expresiones, de MENOR a MAYOR precedencia ----
    def _expression(self):
        return self._comparison()

    def _comparison(self):
        left = self._arithmetic()
        while self._check(TokenType.LESS) or self._check(TokenType.GREATER) or self._check(TokenType.EQUALS_EQUALS):
            operator = self._advance().value
            right = self._arithmetic()
            left = BinaryOp(left, operator, right)
        return left

    def _arithmetic(self):
        left = self._term()
        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator = self._advance().value
            right = self._term()
            left = BinaryOp(left, operator, right)
        return left

    def _term(self):
        left = self._factor()
        while self._check(TokenType.STAR) or self._check(TokenType.SLASH):
            operator = self._advance().value
            right = self._factor()
            left = BinaryOp(left, operator, right)
        return left

    def _factor(self):
        if self._check(TokenType.NUMBER):
            token = self._advance()
            texto = token.value
            valor = float(texto) if "." in texto else int(texto)
            return NumberLiteral(valor)
        if self._check(TokenType.TRUE):
            self._advance()
            return BooleanLiteral(True)
        if self._check(TokenType.FALSE):
            self._advance()
            return BooleanLiteral(False)
        if self._check(TokenType.LPAREN):
            self._advance()
            expr = self._expression()
            self._expect(TokenType.RPAREN, "Esperaba ')' para cerrar la expresión")
            return expr
        if self._check(TokenType.IDENTIFIER):
            name = self._advance().value
            if self._check(TokenType.LPAREN):
                self._advance()
                args = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._expression())
                    while self._check(TokenType.COMMA):
                        self._advance()
                        args.append(self._expression())
                self._expect(TokenType.RPAREN, "Esperaba ')' para cerrar los argumentos")
                return Call(name, args)
            return Identifier(name)
        raise SyntaxError(f"Token inesperado en línea {self._current().line}: {self._current().type}")


if __name__ == "__main__":
    from lexer import Lexer

    source = "let x = 10 let y = 20 if x < y { print(x + y) }"
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    for statement in ast:
        print(statement)