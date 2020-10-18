# ForLoopParser
```
git clone https://github.com/tanmaytirpankar/ForLoopParser.git
```

## Requirements:
sly

```
$python3 parser1.py test_input.txt
Parsing completed
{'_caller_': None, 'x1': 10, 'x2': 8, 'x3': 2, 'x4': 1, 'h': 4.0, 'g': 36, 'y': 5, 'i': 7, 'x': 3}
```

The output above are the contents of te symbol table. 

Currently the loops can evaluate any arithmetic expression using integers and identifiers. Have not tested for nested loop yet since there is only one symbol table being used for the whole program. You can add additional statements to the loop body for checking multiple statments.

## Idea about for loops:
Following idea about loops mentioned in https://craftinginterpreters.com/control-flow.html

The loops are divided into 4 parts. assignment/initializer, condition, increment and body. These loops will be using a separate symbol table from the one used to build the computational graph since the expressions here are not part of the computational graph.

The assignment part of loop: Stores the identifier with its corresponding value in the symbol table.
The condition part of loop: Returns a symbolic expression that will fetch values of the free_symbols from the symbol table and check whether loop should be repeated or not.
The step part of loop: Returns a symbolic expression that will perform the increment/decrement operation after the body executes.
The body part of the loop: The program stores the body tokens in a list and creates a new generator for every iteration which is passed to the parser.

Before every iteration, the condition is checked and after every iteration the increment step is performed using the symbolic expressions.

## Next Task:
Adding scopes for nested loops.
Building AST for computational graph using nodes from AST.py and adding arrays.

Following is the grammar being used for building the parser. 
```
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

```
