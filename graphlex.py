import ply.lex as lex
import json

tokens = (
    'COMMENT',
    'SOURCE',
    'DESTINATION'
    'LBRACE',
    'RBRACE',
    'LBRACK',
    'RBRACK',
    'SEMICOLON',
    'COMMA'
)

t_COMMENT = r'###.*'
t_SOURCE = r'(?#@source=)[0-9]+'
t_DESTINATION = r'(?#@destination=)[0-9]+'
