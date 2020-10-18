from lexer import Flexer
from SymbolTable import SymbolTable
from AST import *
from sympy import *
import sys
from gtokens import *

class Fparser(object):
    tokens = Flexer.tokens
    sym_tab = SymbolTable()

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None

    def error(self):
        raise Exception('Invalid Syntax while parsing')

    def consume(self, token_type):
        # print(self.current_token.type, token_type, self.current_token.value)
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def parse(self, text):
        self.lexer.create_token_generator(text)
        self.lexer.tok
        self.current_token = self.lexer.get_next_token()  # current_token()
        self.program()

    def program(self):
        """ program: BEGIN <stmts> END"""
        self.consume(BEGIN)
        while self.current_token.type != END:
            self.block()
        self.consume(END)

    def block(self):
        """
        block   :  <assign_expr>
                |  <forblock>
                |  empty
        """

        if self.current_token.type == ID:
            self.assign_expr()
        elif self.current_token.type == FOR:
            self.forblock()

    def forblock(self):
        """
        forblock:   FOR LPAREN <loop_assign> (COMMA <loop_assign>)* SEMICOLON <cond_expr> SEMICOLON (<op_expr> | <loop_assign>) (COMMA (<op_expr> | <loop_assign>))* RPAREN DO <block>* ENDFOR
        """

        self.consume(FOR)
        self.consume(LPAREN)

        varList=[self.loop_assign()]
        while self.current_token.type != SEMICOLON:
            self.consume(COMMA)
            varList.append(self.loop_assign())
        self.consume(SEMICOLON)

        condition=self.cond_expr()
        self.consume(SEMICOLON)

        stepper_list=[self.op_expr()]
        while self.current_token.type != RPAREN:
            self.consume(COMMA)
            stepper_list.append(self.op_expr())

        self.consume(RPAREN)
        self.consume(DO)

        token_list=[]
        while self.current_token.type!=ENDFOR:
            token_list.append(self.current_token)
            self.consume(self.current_token.type)
        a2g = lambda x: (n for n in x)
        parent_tok_generator=self.lexer.tok
        last_token=self.current_token
        # print(tok_generator)
        # for tok in tok_generator:
        #     print('type=%r, value=%r' % (tok.type, tok.value))


        value_list=[]
        x = 0
        for sym in varList:
            value_list.append([sym, self.sym_tab.lookup(sym)])
        while condition.subs(value_list):
            # print(condition.subs(value_list))
            # print("Running code in for block")
            # print(self.sym_tab.lookup(p.loop_assign[0]))
            # x = x+1
            # print(x)

            self.lexer.tok=a2g(token_list)
            self.current_token=self.lexer.tok.__next__()
            self.block()

            # sym_set=set()
            # for sym_expr in stepper_list:
            #     for sym in sym_expr.free_symbols:
            #         sym_set.add(sym)
            for sym_expr in stepper_list:
                for sym in sym_expr.free_symbols:
                    self.sym_tab.insert(str(sym), sym_expr.subs([[str(sym),self.sym_tab.lookup(str(sym))]]))
            value_list=[]
            for sym in varList:
                value_list.append([sym, self.sym_tab.lookup(sym)])
        self.lexer.tok=parent_tok_generator
        self.current_token=last_token
        self.consume(ENDFOR)

    def loop_assign(self):
        """
        loop_assign: ID ASSIGN <loop_expr>
        """
        nameToken = self.current_token
        self.consume(ID)
        self.consume(ASSIGN)
        loop_expr = self.loop_expr()
        self.sym_tab.insert(nameToken.value, loop_expr)
        return nameToken.value

    def loop_expr(self):
        """
        loop_expr    :   <loop_term> ((PLUS | MINUS) <loop_term>)*
        """
        loop_expr = self.loop_term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.consume(PLUS)
                loop_expr = loop_expr + self.loop_term()
            elif token.type == MINUS:
                self.consume(PLUS)
                loop_expr = loop_expr - self.loop_term()
        return loop_expr

    def loop_term(self):
        """
        loop_term    :   <loop_factor> ((MUL | DIV | MOD) <loop_factor>)*
        """
        loop_term = self.loop_factor()
        while self.current_token.type in (MUL, DIV, MOD):
            token = self.current_token
            if token.type == MUL:
                self.consume(MUL)
                loop_term = loop_term * self.loop_factor()
            elif token.type == DIV:
                self.consume(DIV)
                loop_term = loop_term / self.loop_factor()
            elif token.type == MOD:
                self.consume(MOD)
                loop_term = loop_term % self.loop_factor()
        return loop_term

    def loop_factor(self):
        """
        loop_factor  :   MINUS <loop_factor>
                    |   PLUS <loop_factor>
                    |   LPAREN <loop_expr> RPAREN
                    |   INTEGER
                    |   ID
        """
        token = self.current_token
        if token.type == INTEGER:
            self.consume(INTEGER)
            return token.value
        elif token.type == ID:
            value = self.sym_tab.lookup(token.value)
            self.consume(ID)
            if value != None:
                return value
            else:
                self.error()
        elif token.type == MINUS:
            self.consume(MINUS)
            return -self.loop_factor()
        elif token.type == PLUS:
            self.consume(PLUS)
            return self.loop_factor()
        elif token.type == LPAREN:
            self.consume(LPAREN)
            loop_expr = self.loop_expr()
            self.consume(RPAREN)
            return loop_expr

    def cond_expr(self):
        """
        cond_expr   :   <cond_term> ( (AND | OR) <cond_term>)*
        """
        cond_expr = self.cond_term()

        while self.current_token.type in (AND, OR):
            token = self.current_token
            if token.type == AND:
                self.consume(PLUS)
                cond_expr = cond_expr & self.cond_term()
            elif token.type == OR:
                self.consume(PLUS)
                cond_expr = cond_expr | self.cond_term()
        return cond_expr


    def cond_term(self):
        """
        cond_term   :   <sym_expr> (LT | GT | LET | GET | EQ) <sym_expr>
        """

        cond_term=self.sym_expr()
        if self.current_token.type == LT:
            self.consume(LT)
            cond_term=cond_term<self.sym_expr()
        elif self.current_token.type == GT:
            self.consume(GT)
            cond_term=cond_term>self.sym_expr()
        elif self.current_token.type == LET:
            self.consume(LET)
            cond_term=cond_term<=self.sym_expr()
        elif self.current_token.type == GET:
            self.consume(GET)
            cond_term=cond_term>=self.sym_expr()
        elif self.current_token.type == EQ:
            self.consume(EQ)
            cond_term=Eq(cond_term,self.sym_expr())
        else:
            self.error("Wrong symbol found")
        return cond_term


    def sym_expr(self):
        """
        sym_expr    :   <sym_term> ((PLUS | MINUS) <sym_term>)*
        """

        sym_expr = self.sym_term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.consume(PLUS)
                sym_expr = sym_expr + self.sym_term()
            elif token.type == MINUS:
                self.consume(PLUS)
                sym_expr = sym_expr - self.sym_term()
        return sym_expr


    def sym_term(self):
        """
         sym_term    :   <sym_factor> ((MUL | DIV | MOD) <sym_factor>)*
        """
        sym_term = self.sym_factor()
        while self.current_token.type in (MUL, DIV, MOD):
            token = self.current_token
            if token.type == MUL:
                self.consume(MUL)
                sym_term = sym_term * self.sym_factor()
            elif token.type == DIV:
                self.consume(DIV)
                sym_term = sym_term / self.sym_factor()
            elif token.type == MOD:
                self.consume(MOD)
                sym_term = sym_term % self.sym_factor()
        return sym_term


    def sym_factor(self):
        """
        sym_factor  :   MINUS <sym_factor>
                    |   PLUS <sym_factor>
                    |   LPAREN <sym_expr> RPAREN
                    |   INTEGER
                    |   ID
        """

        token = self.current_token
        if token.type == INTEGER:
            self.consume(INTEGER)
            return token.value
        elif token.type == ID:
            self.consume(ID)
            return symbols(token.value)
        elif token.type==MINUS:
            self.consume(MINUS)
            self.consume(ID)
            return -symbols(token.value)
        elif token.type==PLUS:
            self.consume(PLUS)
            self.consume(ID)
            return symbols(token.value)
        elif token.type == LPAREN:
            self.consume(LPAREN)
            expr = self.expr()
            self.consume(RPAREN)
            return expr
        else:
            self.error("Syntax error")

    def op_expr(self):
        """
        op_expr :   ID  (INC | DEC)
        """
        token = self.current_token
        self.consume(ID)
        if self.current_token.type == INC:
            self.consume(INC)
            return symbols(token.value)+1
        elif self.current_token.type == DEC:
            self.consume(DEC)
            return symbols(token.value)-1
        else:
            self.error("Syntax error")


    def assign_expr(self):
        """
        assign_expr: ID ASSIGN <expr> SEMICOLON
        """
        nameToken=self.current_token
        self.consume(ID)
        self.consume(ASSIGN)
        expr=self.expr()
        self.sym_tab.insert(nameToken.value, expr)
        self.consume(SEMICOLON)


    def expr(self):
        """
        expr    :   <term> ((PLUS | MINUS) <term>)*
        """
        expr=self.term()

        while self.current_token.type in (PLUS,MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.consume(PLUS)
                expr=expr+self.term()
            elif token.type == MINUS:
                self.consume(PLUS)
                expr=expr-self.term()
        return expr

    def term(self):
        """
        term    :   <factor> ((MUL | DIV | MOD) <factor>)*
        """

        term=self.factor()
        while self.current_token.type in (MUL,DIV,MOD):
            token = self.current_token
            if token.type == MUL:
                self.consume(MUL)
                term=term*self.factor()
            elif token.type == DIV:
                self.consume(DIV)
                term=term/self.factor()
            elif token.type == MOD:
                self.consume(MOD)
                term=term%self.factor()
        return term

    def factor(self):
        """
        factor  :   MINUS <factor>
                |   PLUS <factor>
                |   LPAREN <expr> RPAREN
                |   INTEGER
                |   ID
        """

        token=self.current_token
        if token.type==INTEGER:
            self.consume(INTEGER)
            return token.value
        elif token.type==ID:
            value = self.sym_tab.lookup(token.value)
            self.consume(ID)
            if value != None:
                return value
            else:
                self.error()
        elif token.type==LPAREN:
            self.consume(LPAREN)
            expr=self.expr()
            self.consume(RPAREN)
            return expr


if __name__ == '__main__':
    import sys
    text = open(sys.argv[1], 'r').read()
    lexer = Flexer()
    parser = Fparser(lexer)

    parser.parse(text)
    print("Parsing completed")
    print(parser.sym_tab._symTab)


"""
program :   BEGIN <block>* END

block   :   <assign_expr>
        |  <forblock>
        |  empty

forblock:   FOR LPAREN <loop_assign> (COMMA <loop_assign>)* SEMICOLON <cond_expr> SEMICOLON (<op_expr> | <loop_assign>) (COMMA (<op_expr> | <loop_assign>))* RPAREN DO <block>* ENDFOR

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