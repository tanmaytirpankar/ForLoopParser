from sly import Lexer
from gtokens import *

class Flexer(Lexer):

    # The tokens arranged on each line are type of input, arithmetic operators, logical operators, miscellaneous symbols,
    # Grammar specific keywords
    tokens = {INTEGER, DECIMAL,
              PLUS, MINUS, DIV, MUL, MOD, INC, DEC, \
              LT, GT, LET, GET, EQ, NEQ, AND, OR,
              LPAREN, RPAREN, CLPAREN, CRPAREN, SLPAREN, SRPAREN, SEMICOLON, COMMA, ASSIGN, \
              ID, FOR, BEGIN, END, DO, ENDFOR}

    # String characters to be ignored
    ignore = ' \t'

    ignore_comment = r'\#.*'

    # Regular expression rules for tokens
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    DECIMAL = r'\d+.\d+'
    INTEGER = r'\d+'
    DIV = r'/'
    MUL = r'\*'
    INC = r'\+\+'
    DEC = r'--'
    PLUS = r'\+'
    MINUS = r'-'
    MOD = r'\%'
    EQ = r'=='
    ASSIGN = r'='
    LT = r'<'
    GT = r'>'
    LET = r'<='
    GET = r'>='
    NEQ = r'\!='
    AND = r'&&'
    OR = r'\|\|'
    LPAREN = r'\('
    RPAREN = r'\)'
    CLPAREN = r'\{'
    CRPAREN = r'\}'
    SLPAREN = r'\['
    SRPAREN = r'\]'
    SEMICOLON = r';'
    COMMA = r','
    ID['for'] = FOR
    ID['begin'] = BEGIN
    ID['end'] = END
    ID['do'] = DO
    ID['endfor'] = ENDFOR

    pos = 0
    token_list = []
    current_token = None
    tok = None

    # Define a rule so we can track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Compute column.
    #     input is the input text string
    #     token is a token instance
    def find_column(self, text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))

    def create_token_generator(self, text):
        self.tok = self.tokenize(text)

    def get_current_token(self):
        return self.current_token

    def get_next_token(self):
        try:
            return self.tok.__next__()
        except StopIteration:
            return None

    @_(r'\d+')
    def INTEGER(self, tok):
        tok.value = int(tok.value)
        return tok

    @_(r'\d+.\d+')
    def DECIMAL(self, tok):
        tok.value = float(tok.value)
        return tok


    def show_token(self, tok):
        print('type=%r, value=%r' % (tok.type, tok.value))


if __name__ == '__main__':
    import sys
    text=open(sys.argv[1], 'r').read()
    lexer = Flexer()

    #for tok in lexer.tokenize(text):
     #   print('type=%r, value=%r' % (tok.type, tok.value))


"""
program :   BEGIN <stmts> END

stmts   :   <stmt> <stmts>*

stmt   :   <assign_expr>
        |  <forblock>
        |  empty

forblock:   FOR LPAREN <loop_assign> (COMMA <loop_assign>)* SEMICOLON <cond_expr> SEMICOLON (<op_expr> | <loop_assign>) (COMMA (<op_expr> | <loop_assign>))* RPAREN DO <stmts> ENDFOR

loop_assign: ID ASSIGN <loop_expr>

loop_expr    :   <loop_term> ((PLUS | MINUS) <loop_term>)*

loop_term    :   <loop_factor> ((MUL | DIV | MOD) <loop_factor>)*

loop_factor  :   MINUS <loop_factor>
        |   PLUS <loop_factor>
        |   LPAREN <loop_expr> RPAREN
        |   INTEGER
        |   ID

cond_expr   :   <cond_term> ( (AND | OR) <cond_term>)*

cond_term   :   <sym_expr> (LT | GT | LET | GET | EQ | NEQ) <sym_expr>

sym_expr    :   <sym_term> ((PLUS | MINUS) <sym_term>)*

sym_term    :   <sym_factor> ((MUL | DIV | MOD) <sym_factor>)*

sym_factor  :   MINUS <sym_factor>
        |   PLUS <sym_factor>
        |   LPAREN <sym_expr> RPAREN
        |   INTEGER
        |   ID

assign_expr    : ID ASSIGN <expr> SEMICOLON

op_expr :   ID  (INC | DEC)

expr    :   <term> ((PLUS | MINUS) <term>)*

term    :   <factor> ((MUL | DIV | MOD) <factor>)*

factor  :   MINUS <factor>
        |   PLUS <factor>
        |   LPAREN <expr> RPAREN
        |   INTEGER
        |   ID
        
"""
