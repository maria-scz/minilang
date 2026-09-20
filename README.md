# MiniLang

Un intérprete de un lenguaje de programación pequeño, escrito desde cero en Python — sin frameworks externos, sin librerías de parsing. El objetivo no era construir un lenguaje "útil", sino entender de verdad cómo funciona uno: cómo un compilador o intérprete convierte texto plano en ejecución real.

## Recurso guía

Basado en el diseño de [Crafting Interpreters](https://craftinginterpreters.com) de Bob Nystrom, portado de Java a Python.

## Ejemplo

```minilang
let x = 10
let y = 20
if x < y {
    print(x + y)
}
```
Output: `30`

## Cómo funciona

El intérprete tiene tres etapas, cada una en su propio archivo:

1. **Lexer** (`lexer.py`) — convierte el código fuente (texto plano) en una lista de tokens: `LET`, `IDENTIFIER`, `NUMBER`, `PLUS`, etc.
2. **Parser** (`parser.py`) — toma esos tokens y construye un AST (Abstract Syntax Tree) usando recursive descent parsing con precedencia de operadores (`*`/`/` antes que `+`/`-`, comparaciones al final).
3. **Evaluator** (`evaluator.py`) — recorre el AST recursivamente y lo ejecuta de verdad, manteniendo el estado de las variables en un `Environment`.

## Features soportadas

| Fase | Ejemplo |
|---|---|
| Aritmética | `5 + 3 * 2` |
| Variables | `let x = 10` |
| Comparaciones y booleanos | `x > 5`, `x == 10` |
| Condicionales | `if x > 5 { print(x) }` |
| Loops | `while x < 10 { x = x + 1 }` |
| Funciones | `function add(a, b) { return a + b }` |

## Cómo correrlo
```
python3 evaluator.py
```