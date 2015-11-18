import re
from .numeric import NumericStringParser


# TODO make this take more than comments
# and properly match the proper input to the right function
# TODO clean up a bit
def parse(expr, inputs, funcs, colors):
    """
    Parses a mathematical expression (string)
    that can include pre-defined composition metrics (`funcs`)
    """
    expr = expr.replace(' ', '').replace('\n', '')
    nsp = NumericStringParser()

    # extract non-digits/decimals/operators
    metric_re = re.compile(r'[^\d^+\-+\/\.\(\)\*]+')
    expr_tex = expr
    exprs = [expr for _ in range(len(inputs))]
    texes = exprs.copy()
    for match in metric_re.finditer(expr):
        func = match.group(0)

        # skip predefined functions, e.g. cos
        if func in nsp.fn.keys():
            continue
        elif func not in funcs.keys():
            raise Exception(func, 'is not a recognized function')
        else:
            color = colors[func]
            expr_tex = expr_tex.replace(func, '\color{{{}}}{{\\text{{{}}}}}'.format(color, func), 1)
            for i, input in enumerate(inputs):
                val = funcs[func](input)
                exprs[i] = exprs[i].replace(func, str(val), 1)

                if isinstance(val, float):
                    val = '{:.3f}'.format(val) # so there are less crazy decimals
                texes[i] = texes[i].replace(func, '\color{{{}}}{{{}}}'.format(color, val), 1)
    return [nsp.eval(e) for e in exprs], texes, expr_tex
