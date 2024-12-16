list: list
REAL: [0-9]+\.[0-9]+([eE][+-]?[0-9]+)?
INT: [0-9]+
VAR: [a-zA-Z_][a-zA-Z0-9_]*
ASSIGN: =
+: \+
-: -
*: \*
/: /
%: %
POW: \^
!=: !=
==: ==
>: >
<: <
>=: >=
<=: <=
(: LPAREN
): RPAREN
[: LBRACKET
]: RBRACKET
WHITESPACE: \s+