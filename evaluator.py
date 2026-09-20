# evaluator.py
from ast_nodes import (
    NumberLiteral, BooleanLiteral, Identifier, BinaryOp, Call,
    LetStatement, AssignStatement, ExpressionStatement, IfStatement,
    WhileStatement, FunctionDeclaration, ReturnStatement,
)


class Environment:
    # Guarda las variables de un "scope" (alcance). parent apunta al
    # scope de afuera — así una función puede LEER variables globales
    # aunque tenga sus propias variables locales.
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name, value):
        # 'let' siempre crea la variable en el scope ACTUAL.
        self.vars[name] = value

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"Variable no definida: '{name}'")

    def assign(self, name, value):
        # A diferencia de define(), assign() busca en qué scope YA
        # existe la variable (puede ser uno de los padres) y la
        # actualiza ahí — no crea una nueva. Así es como 'x = x + 1'
        # modifica la 'x' que ya existía, en vez de tapar otra encima.
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        raise NameError(f"No se puede asignar, variable no definida: '{name}'")


class ReturnSignal(Exception):
    # Un 'return' dentro de una función puede estar anidado varios
    # niveles adentro (dentro de un if, dentro de un while...).
    # Usar una excepción es la forma más simple de "saltar" fuera de
    # todos esos niveles de golpe hasta donde se llamó la función.
    def __init__(self, value):
        self.value = value


class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}  # nombre de función -> su FunctionDeclaration

    def run(self, statements):
        for statement in statements:
            self._execute(statement, self.global_env)

    # _execute maneja STATEMENTS (acciones, no producen valor)
    def _execute(self, node, env):
        if isinstance(node, LetStatement):
            value = self._evaluate(node.value, env)
            env.define(node.name, value)

        elif isinstance(node, AssignStatement):
            value = self._evaluate(node.value, env)
            env.assign(node.name, value)

        elif isinstance(node, ExpressionStatement):
            self._evaluate(node.expr, env)

        elif isinstance(node, IfStatement):
            if self._evaluate(node.condition, env):
                for stmt in node.then_body:
                    self._execute(stmt, env)
            elif node.else_body is not None:
                for stmt in node.else_body:
                    self._execute(stmt, env)

        elif isinstance(node, WhileStatement):
            while self._evaluate(node.condition, env):
                for stmt in node.body:
                    self._execute(stmt, env)

        elif isinstance(node, FunctionDeclaration):
            # Declarar una función no la ejecuta, solo la "registra"
            # para poder llamarla después.
            self.functions[node.name] = node

        elif isinstance(node, ReturnStatement):
            value = self._evaluate(node.value, env)
            raise ReturnSignal(value)

        else:
            raise RuntimeError(f"Statement desconocido: {node}")

    # _evaluate maneja EXPRESIONES (producen un valor)
    def _evaluate(self, node, env):
        if isinstance(node, NumberLiteral):
            return node.value

        if isinstance(node, BooleanLiteral):
            return node.value

        if isinstance(node, Identifier):
            return env.get(node.name)

        if isinstance(node, BinaryOp):
            left = self._evaluate(node.left, env)
            right = self._evaluate(node.right, env)
            if node.operator == "+":
                return left + right
            if node.operator == "-":
                return left - right
            if node.operator == "*":
                return left * right
            if node.operator == "/":
                return left / right
            if node.operator == "<":
                return left < right
            if node.operator == ">":
                return left > right
            if node.operator == "==":
                return left == right
            raise RuntimeError(f"Operador desconocido: {node.operator}")

        if isinstance(node, Call):
            if node.callee == "print":
                args = [self._evaluate(arg, env) for arg in node.args]
                print(*args)
                return None
            return self._call_function(node, env)

        raise RuntimeError(f"Expresión desconocida: {node}")

    def _call_function(self, node, env):
        if node.callee not in self.functions:
            raise NameError(f"Función no definida: '{node.callee}'")
        func = self.functions[node.callee]

        if len(node.args) != len(func.params):
            raise TypeError(
                f"'{func.name}' espera {len(func.params)} argumento(s), recibió {len(node.args)}"
            )

        # Cada llamada arranca con SU PROPIO scope, con el global como
        # respaldo de lectura — así los parámetros no se pisan entre
        # llamadas distintas.
        call_env = Environment(parent=self.global_env)
        for param_name, arg_expr in zip(func.params, node.args):
            call_env.define(param_name, self._evaluate(arg_expr, env))

        try:
            for stmt in func.body:
                self._execute(stmt, call_env)
        except ReturnSignal as signal:
            return signal.value

        return None  # función sin 'return' explícito


if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    tests = [
        "let x = 10 let y = 20 if x < y { print(x + y) }",
        "let i = 0 while i < 5 { print(i) i = i + 1 }",
        "function add(a, b) { return a + b } print(add(3, 4))",
        "let a = 5 let b = 5 print(a == b)",
    ]

    for source in tests:
        print(f"--- {source}")
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        Evaluator().run(ast)
        print()