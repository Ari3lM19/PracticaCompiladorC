"""Pruebas del analizador léxico de Mini C según analizador-lexico-mini-c."""

from minic.diagnostics import diagnostic_code
from minic.diagnostics.diagnostic import Diagnostic
from minic.lexer import Lexer, Token, TokenType
from minic.output import format_diagnostic, format_token


def test_section_7_case_1() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()

    assert diagnostics == []

    expected_tokens = [
        Token(TokenType.IDENTIFIER, "int2", None, 1, 1),
        Token(TokenType.ASSIGN, "=", None, 1, 6),
        Token(TokenType.INTEGER_LITERAL, "12", 12, 1, 8),
        Token(TokenType.IDENTIFIER, "abc", None, 1, 10),
        Token(TokenType.SEMICOLON, ";", None, 1, 13),
        Token(TokenType.IDENTIFIER, "whilex", None, 2, 1),
        Token(TokenType.EQUAL_EQUAL, "==", None, 2, 8),
        Token(TokenType.MINUS, "-", None, 2, 11),
        Token(TokenType.INTEGER_LITERAL, "5", 5, 2, 12),
        Token(TokenType.EOF, "", None, 2, 13),
    ]

    assert tokens == expected_tokens
    formatted = [format_token(t) for t in tokens]
    expected_output = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    assert formatted == expected_output


def test_section_7_case_2_with_errors() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    expected_tokens = [
        Token(TokenType.KW_INT, "int", None, 1, 1),
        Token(TokenType.IDENTIFIER, "x", None, 1, 5),
        Token(TokenType.ASSIGN, "=", None, 1, 7),
        Token(TokenType.SEMICOLON, ";", None, 1, 10),
        Token(TokenType.IDENTIFIER, "x", None, 2, 1),
        Token(TokenType.ASSIGN, "=", None, 2, 5),
        Token(TokenType.INTEGER_LITERAL, "0", 0, 2, 7),
        Token(TokenType.SEMICOLON, ";", None, 2, 8),
        Token(TokenType.IDENTIFIER, "fin", None, 2, 13),
        Token(TokenType.EOF, "", None, 2, 16),
    ]

    expected_diagnostics = [
        Diagnostic("LEX001", "error", "Carácter no reconocido: '@'", 1, 9),
        Diagnostic("LEX001", "error", "Carácter no reconocido: '!'", 2, 3),
        Diagnostic("LEX001", "error", "Carácter no reconocido: '/'", 2, 10),
        Diagnostic("LEX001", "error", "Carácter no reconocido: '/'", 2, 11),
    ]

    assert tokens == expected_tokens
    assert diagnostics == expected_diagnostics

    formatted_tokens = [format_token(t) for t in tokens]
    expected_token_output = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    assert formatted_tokens == expected_token_output

    formatted_diagnostics = [format_diagnostic(d) for d in diagnostics]
    expected_diag_output = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]
    assert formatted_diagnostics == expected_diag_output


def test_keywords_vs_identifiers() -> None:
    source = "int while int_var while1 _while"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    types = [t.type for t in tokens]
    assert types == [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]


def test_integer_literals_and_values() -> None:
    source = "0 007 42 12345678901234567890"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert tokens[0] == Token(TokenType.INTEGER_LITERAL, "0", 0, 1, 1)
    assert tokens[1] == Token(TokenType.INTEGER_LITERAL, "007", 7, 1, 3)
    assert tokens[2] == Token(TokenType.INTEGER_LITERAL, "42", 42, 1, 7)
    assert tokens[3] == Token(TokenType.INTEGER_LITERAL, "12345678901234567890", 12345678901234567890, 1, 10)


def test_operators_and_delimiters() -> None:
    source = "== != = + - ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    expected_types = [
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_max_munch_equality() -> None:
    source = "=== !== =="
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    # "===" -> "==" then "="
    # "!==" -> "!=" then "="
    # "==" -> "=="
    types = [t.type for t in tokens]
    assert types == [
        TokenType.EQUAL_EQUAL,
        TokenType.ASSIGN,
        TokenType.NOT_EQUAL,
        TokenType.ASSIGN,
        TokenType.EQUAL_EQUAL,
        TokenType.EOF,
    ]


def test_whitespace_and_column_tracking() -> None:
    # \t counts as 1 col
    # \r without \n counts as 1 col
    # \n starts new line at col 1
    source = "a\tb\rc\nd"
    tokens, diagnostics = Lexer(source).scan()
    assert diagnostics == []

    assert tokens[0] == Token(TokenType.IDENTIFIER, "a", None, 1, 1)
    assert tokens[1] == Token(TokenType.IDENTIFIER, "b", None, 1, 3)
    assert tokens[2] == Token(TokenType.IDENTIFIER, "c", None, 1, 5)
    assert tokens[3] == Token(TokenType.IDENTIFIER, "d", None, 2, 1)
    assert tokens[4] == Token(TokenType.EOF, "", None, 2, 2)


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert diagnostics == []
    assert tokens == [Token(TokenType.EOF, "", None, 1, 1)]


def test_only_whitespace() -> None:
    tokens, diagnostics = Lexer("   \t  \n  ").scan()
    assert diagnostics == []
    assert tokens == [Token(TokenType.EOF, "", None, 2, 3)]


def test_unrecognized_characters_recovery() -> None:
    source = "x $ y # z"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 2
    assert diagnostics[0] == Diagnostic(diagnostic_code.LEX001, "error", "Carácter no reconocido: '$'", 1, 3)
    assert diagnostics[1] == Diagnostic(diagnostic_code.LEX001, "error", "Carácter no reconocido: '#'", 1, 7)

    assert [t.type for t in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
