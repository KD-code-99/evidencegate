"""A small integer-polynomial language. Parsing never executes source code."""
from __future__ import annotations
import ast
from itertools import product
import re


class Unsupported(ValueError):
    pass


def parse(expression, variables):
    if not isinstance(expression,str) or len(expression)>600 or not 1<=len(variables)<=4:
        raise Unsupported('Expression or variable limit exceeded')
    if len(set(variables))!=len(variables) or any(not isinstance(v,str) or not re.fullmatch(r'[a-z][a-z_0-9]{0,24}',v) for v in variables):
        raise Unsupported('Declare distinct short variable names')
    tree=ast.parse(expression,mode='eval')
    if sum(1 for _ in ast.walk(tree))>120:raise Unsupported('Syntax limit exceeded')
    def add(a,b):
        out=dict(a)
        for m,c in b.items():out[m]=out.get(m,0)+c
        return {m:c for m,c in out.items() if c}
    def mul(a,b):
        out={}
        for m,c in a.items():
            for n,d in b.items():
                k=tuple(x+y for x,y in zip(m,n));out[k]=out.get(k,0)+c*d
        if len(out)>3000 or any(abs(c).bit_length()>256 for c in out.values()) or any(max(m)>5 or sum(m)>10 for m in out):raise Unsupported('Polynomial limit exceeded')
        return {m:c for m,c in out.items() if c}
    def walk(node):
        if isinstance(node,ast.Constant) and type(node.value) is int and abs(node.value)<=10**12:
            return {(0,)*len(variables):node.value} if node.value else {}
        if isinstance(node,ast.Name) and node.id in variables:
            return {tuple(int(i==variables.index(node.id)) for i in range(len(variables))):1}
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
            p=walk(node.operand);return {m:-c for m,c in p.items()} if isinstance(node.op,ast.USub) else p
        if isinstance(node,ast.BinOp):
            if isinstance(node.op,ast.Pow):
                if not isinstance(node.right,ast.Constant) or type(node.right.value) is not int or not 0<=node.right.value<=5:raise Unsupported('Use a literal power from 0 to 5')
                base=walk(node.left);out={(0,)*len(variables):1}
                for _ in range(node.right.value):out=mul(out,base)
                return out
            a,b=walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Add):return add(a,b)
            if isinstance(node.op,ast.Sub):return add(a,{m:-c for m,c in b.items()})
            if isinstance(node.op,ast.Mult):return mul(a,b)
        raise Unsupported('Supported Python semantics: integer literals/arguments, +, -, *, and nonnegative literal powers. Division, floats, calls, branches and mutable state are unsupported.')
    return walk(tree.body)


def evaluate(poly, point):
    return sum(c*product_power(point,m) for m,c in poly.items())


def product_power(point,powers):
    value=1
    for x,k in zip(point,powers):value*=x**k
    return value


def independent_parse(expression, variables):
    """Distributive expansion using sorted variable words, not exponent vectors."""
    tree=ast.parse(expression,mode='eval')
    def combine(a,b,sign=1):
        out=dict(a)
        for word,c in b.items():out[word]=out.get(word,0)+sign*c
        return {w:c for w,c in out.items() if c}
    def multiply(a,b):
        out={}
        for w,c in a.items():
            for v,d in b.items():
                key=tuple(sorted(w+v));out[key]=out.get(key,0)+c*d
        return {w:c for w,c in out.items() if c}
    def expand(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:return {():n.value} if n.value else {}
        if isinstance(n,ast.Name) and n.id in variables:return {(n.id,):1}
        if isinstance(n,ast.UnaryOp):
            p=expand(n.operand)
            return {w:-c for w,c in p.items()} if isinstance(n.op,ast.USub) else p
        if isinstance(n,ast.BinOp):
            if isinstance(n.op,ast.Pow):
                out={():1};base=expand(n.left)
                for _ in range(n.right.value):out=multiply(out,base)
                return out
            a,b=expand(n.left),expand(n.right)
            if isinstance(n.op,ast.Add):return combine(a,b)
            if isinstance(n.op,ast.Sub):return combine(a,b,-1)
            if isinstance(n.op,ast.Mult):return multiply(a,b)
        raise Unsupported('Independent checker rejected unsupported syntax')
    return expand(tree.body)


def compare(expected, actual, variables):
    before,after=parse(expected,variables),parse(actual,variables)
    residual=dict(after)
    for m,c in before.items():residual[m]=residual.get(m,0)-c
    residual={m:c for m,c in residual.items() if c}
    independent_before,independent_after=independent_parse(expected,variables),independent_parse(actual,variables)
    independent=dict(independent_after)
    for word,c in independent_before.items():independent[word]=independent.get(word,0)-c
    independent={w:c for w,c in independent.items() if c}
    converted={tuple(sorted(v for v,k in zip(variables,m) for _ in range(k))):c for m,c in residual.items()}
    if independent!=converted:raise ValueError('Independent coefficient check disagreed')
    result={'status':'PROVED_EQUIVALENT' if not residual else 'REFUTED','domain':'All integer arguments; pure polynomial return semantics only.',
            'expected':expected,'actual':actual,'variables':variables,'residual_coefficients':[{'powers':list(m),'coefficient':str(c)} for m,c in sorted(residual.items())],
            'independent_check':'Sorted-word distributive expansion agrees with exponent-vector coefficients'}
    if residual:
        degree=[max(m[i] for m in residual) for i in range(len(variables))]
        for point in product(*(range(1,k+2) for k in degree)):
            left,right=evaluate(before,point),evaluate(after,point)
            if left!=right:
                result['counterexample']={v:x for v,x in zip(variables,point)}
                result['expected_at_counterexample']=str(left);result['actual_at_counterexample']=str(right)
                break
        if 'counterexample' not in result:raise ValueError('Nonzero polynomial witness did not materialize')
    return result


def extract(source, function_name, variables):
    tree=ast.parse(source)
    if len(tree.body)!=1 or any(not isinstance(n,ast.FunctionDef) for n in tree.body):raise Unsupported('The contracted module must contain exactly one pure function declaration')
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function_name]
    if len(functions)!=1:raise Unsupported('Expected one declared function')
    fn=functions[0]
    if fn.decorator_list or fn.returns or any(a.annotation for a in fn.args.args) or fn.args.defaults or fn.args.vararg or fn.args.kwarg or fn.args.kwonlyargs or fn.args.posonlyargs:
        raise Unsupported('Only an undecorated positional function without defaults is supported')
    if [x.arg for x in fn.args.args]!=variables:raise Unsupported('Function parameters differ from contract')
    if len(fn.body)!=1 or not isinstance(fn.body[0],ast.Return):raise Unsupported('Only a single pure return expression is supported')
    expr=ast.unparse(fn.body[0].value)
    parse(expr,variables)
    return expr
