# lexer.py — versión comentada
from enum import Enum, auto
from dataclasses import dataclass


# TokenType enumera TODOS los "tipos" de token que existen en MiniLang.
# auto() le asigna un número único a cada uno automáticamente — no nos
# importa el número en sí, solo que cada tipo sea distinto de los demás.
class TokenType(Enum):
    # Literales: llevan un valor variable (el número o el nombre en sí)
    NUMBER = auto()
    IDENTIFIER = auto()

    # Palabras clave: siempre el mismo texto exacto ("let", "if", etc.)
    LET = auto()
    IF = auto()
    WHILE = auto()
    FUNCTION = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()

    # Operadores aritméticos y de comparación
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQUALS = auto()          # =  (asignación)
    EQUALS_EQUALS = auto()   # == (comparación de igualdad)
    LESS = auto()            # 
    GREATER = auto()         # >

    # Delimitadores — agrupan código o separan argumentos
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()

    # Token especial que marca "ya no queda nada más que leer"
    EOF = auto()


# Token es la unidad mínima que produce el Lexer. Cada uno guarda:
# - type: qué tipo es (de la lista de arriba)
# - value: el texto original tal como apareció en el código fuente
# - line: en qué línea del archivo apareció (para mensajes de error útiles)
@dataclass
class Token:
    type: TokenType
    value: str
    line: int


# Diccionario que traduce texto -> tipo de token, SOLO para palabras clave.
# Se usa dentro de _identifier() para decidir si lo que leíste es una
# palabra reservada del lenguaje o el nombre de una variable cualquiera.
KEYWORDS = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "while": TokenType.WHILE,
    "function": TokenType.FUNCTION,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

# Igual que KEYWORDS, pero para símbolos de UN solo carácter. Evita tener
# que escribir "elif char == '+': ..." uno por uno para cada símbolo —
# en vez de eso, buscamos el carácter en este diccionario.
SIMPLE_SYMBOLS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ",": TokenType.COMMA,
}


class Lexer:
    def __init__(self, source: str):
        self.source = source   # el código fuente completo, como string
        self.pos = 0            # índice del carácter que estamos leyendo ahora
        self.line = 1           # línea actual (para errores)
        self.tokens = []        # aquí se va acumulando la lista final de tokens

    def tokenize(self) -> list[Token]:
        # Bucle principal: se repite hasta que ya no queda nada por leer.
        while not self._at_end():
            self._skip_whitespace()  # ignora espacios/tabs/saltos de línea
            if self._at_end():
                # Es posible que _skip_whitespace() nos haya dejado justo
                # al final (ej. el archivo termina en un salto de línea).
                break

            char = self._peek()  # miramos el carácter actual sin consumirlo

            if char.isdigit():
                self._number()          # ej: "10", "42"
            elif char.isalpha() or char == "_":
                self._identifier()      # ej: "x", "let", "print"
            elif char == "=":
                # Caso especial: "=" podría ser asignación (=) o
                # comparación (==) — hay que mirar el SIGUIENTE carácter
                # antes de decidir cuál token generar.
                self._advance()  # consumimos el primer "="
                if not self._at_end() and self._peek() == "=":
                    self._advance()  # consumimos el segundo "="
                    self.tokens.append(Token(TokenType.EQUALS_EQUALS, "==", self.line))
                else:
                    self.tokens.append(Token(TokenType.EQUALS, "=", self.line))
            elif char == "<":
                self._advance()
                self.tokens.append(Token(TokenType.LESS, "<", self.line))
            elif char == ">":
                self._advance()
                self.tokens.append(Token(TokenType.GREATER, ">", self.line))
            elif char in SIMPLE_SYMBOLS:
                # Cualquier símbolo de un solo carácter que esté en el diccionario
                self._advance()
                self.tokens.append(Token(SIMPLE_SYMBOLS[char], char, self.line))
            else:
                # Si llegamos aquí, es un carácter que MiniLang no reconoce
                # (ej. "@", "#"). Mejor tronar ahora con un mensaje claro
                # que dejar que el error aparezca más adelante y confundido.
                raise SyntaxError(f"Carácter inesperado '{char}' en línea {self.line}")

        # Al salir del while, agregamos un token EOF ("end of file").
        # El Parser lo va a usar después para saber "ya no hay más tokens,
        # deja de pedir el siguiente".
        self.tokens.append(Token(TokenType.EOF, "", self.line))
        return self.tokens

    # ---- helpers de bajo nivel ----

    def _at_end(self) -> bool:
        # ¿self.pos ya se salió del rango válido del string?
        if self.pos >= len(self.source):
            return True
        else:
            return False

    def _peek(self) -> str:
        # Da el carácter actual SIN moverse — "espiar" sin consumir.
        return self.source[self.pos]

    def _advance(self) -> str:
        # Da el carácter actual Y avanza self.pos en 1 — "consumir".
        char = self.source[self.pos]
        self.pos = self.pos + 1
        return char

    def _skip_whitespace(self):
        # Mientras el carácter actual sea espacio/tab/salto de línea, avanza.
        # Si es un salto de línea, primero sube el contador de líneas.
        while self.pos < len(self.source) and self.source[self.pos] in (' ', '\t', '\n'):
            if self.source[self.pos] == '\n':
                self.line += 1
            self.pos += 1

    def _number(self):
        # Va consumiendo dígitos y pegándolos a "texto" mientras el
        # carácter actual siga siendo un dígito. Ej: '1' -> "1" -> "10".
        texto = ""
        while not self._at_end() and self._peek().isdigit():
            texto += self._advance()
        # Una vez que ya no hay más dígitos, empaquetamos lo acumulado
        # como un Token de tipo NUMBER.
        self.tokens.append(Token(TokenType.NUMBER, texto, self.line))

    def _identifier(self):
        # Mismo patrón que _number, pero acepta letras, dígitos y "_"
        # (una variable puede llamarse "x1" o "mi_variable", pero no
        # puede EMPEZAR con dígito — eso ya lo garantiza tokenize(),
        # que solo llama a _identifier() cuando el primer carácter es
        # letra o "_").
        texto = ""
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            texto += self._advance()

        # ¿Ese texto es una palabra reservada (como "let") o el nombre
        # de una variable cualquiera (como "x")? KEYWORDS.get() busca el
        # texto en el diccionario; si no lo encuentra, regresa el default
        # que le pasamos: TokenType.IDENTIFIER.
        tipo = KEYWORDS.get(texto, TokenType.IDENTIFIER)
        self.tokens.append(Token(tipo, texto, self.line))


# Este bloque SOLO corre con "python lexer.py" directamente
# (no corre si otro archivo hace "import lexer" más adelante, como
# hará el Parser). Es tu prueba rápida de humo.
if __name__ == "__main__":
    source = "let x = 10 let y = 20 if x < y { print(x + y) }"
    for token in Lexer(source).tokenize():
        print(token)