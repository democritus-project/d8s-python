import ast
from typing import Iterable, List, Optional, Tuple, Union

import more_itertools
from d8s_lists import iterable_replace, truthy_items

# TODO: all of these functions where code_text is given should also be able to read a file at a given path (?)


def _python_ast_exception_name(node: Union[ast.Raise, ast.ExceptHandler]) -> str:
    """."""
    if hasattr(node, 'exc') and node.exc:  # this handles ast.Raise nodes
        if hasattr(
            node.exc, 'id'
        ):  # this handles ast.Raise nodes where the exception being raised is an ast.Name (e.g. "e" or "ValueError")
            return node.exc.id
        elif hasattr(
            node.exc.func, 'id'
        ):  # handles ast.Raise nodes where the exception being raised is an ast.Call (e.g. "ValueError('Foo Bar')")
            return node.exc.func.id
        elif hasattr(
            node.exc.func, 'attr'
        ):  # this handles ast.Raise nodes raising a non-built-in error (e.g. "pint.UndefinedUnitError")
            return f'{node.exc.func.value.id}.{node.exc.func.attr}'
    elif hasattr(node, 'type') and node.type:  # this handles ast.ExceptHandler nodes
        if hasattr(
            node.type, 'id'
        ):  # this handles ast.ExceptHandler nodes raising a built-in error (e.g. "RuntimeError")
            return node.type.id
        elif hasattr(
            node.type, 'attr'
        ):  # this handles ast.ExceptHandler nodes raising a non-built-in error (e.g. "pint.UndefinedUnitError")
            return f'{node.type.value.id}.{node.type.attr}'
    elif hasattr(
        node, 'attr'
    ):  # this handles situations where the exception being raised is an ast.Attribute (e.g. "pint.UndefinedUnitError")
        return f'{node.value.id}.{node.attr}'
    elif hasattr(node, 'id'):  # this handles situations where the exception being raised is an ast.Name (e.g. "e")
        return node.id


def python_ast_raise_name(node: ast.Raise) -> Optional[str]:
    """Get the name of the exception raise by the given ast.Raise object."""
    if isinstance(node, ast.Raise):
        return _python_ast_exception_name(node)


def python_ast_exception_handler_exceptions_handled(handler: ast.ExceptHandler) -> Optional[Iterable[str]]:
    """Return all of the exceptions handled by the given exception handler."""
    if isinstance(handler, ast.ExceptHandler):
        handler_has_multiple_exceptions = handler.type and hasattr(handler.type, 'elts')
        if handler_has_multiple_exceptions:
            yield from (_python_ast_exception_name(i) for i in handler.type.elts)
        else:
            exception_name = _python_ast_exception_name(handler)
            if exception_name:
                yield exception_name


def python_ast_exception_handler_exceptions_raised(handler: ast.ExceptHandler) -> Optional[Iterable[str]]:
    """Return the exception raised by the given exception handler."""
    if isinstance(handler, ast.ExceptHandler):
        raise_nodes = list(python_ast_objects_of_type(handler, ast.Raise))
        if any(raise_nodes):
            exceptions_names = list(map(python_ast_raise_name, raise_nodes))
            for name in exceptions_names:
                if name and name == handler.name:
                    exceptions_names = iterable_replace(
                        exceptions_names, name, python_ast_exception_handler_exceptions_handled(handler)
                    )
                elif name is None:
                    exceptions_names = iterable_replace(
                        exceptions_names, name, python_ast_exception_handler_exceptions_handled(handler)
                    )
            yield from more_itertools.collapse(exceptions_names, base_type=str)


def python_exceptions_handled(code_text: str) -> Iterable[str]:
    """Return a list of all exceptions handled in the given code."""
    ast_except_handlers = python_ast_objects_of_type(code_text, ast.ExceptHandler)
    yield from more_itertools.collapse(
        list(map(python_ast_exception_handler_exceptions_handled, ast_except_handlers)), base_type=str
    )


def python_exceptions_raised(code_text: str) -> Iterable[str]:
    """Return a list of all exceptions raised in the given code."""
    parsed_code = python_ast_parse(code_text)

    ast_except_handlers = python_ast_objects_of_type(parsed_code, ast.ExceptHandler)
    exceptions = list(map(python_ast_exception_handler_exceptions_raised, ast_except_handlers))

    # remove all of the ast.ExceptHandlers so exceptions are not parsed twice...
    # (once from the code above and once in the code below)
    nodes = python_ast_objects_not_of_type(parsed_code, ast.ExceptHandler)
    exceptions.extend(list(map(python_ast_raise_name, (node for node in nodes if isinstance(node, ast.Raise)))))

    yield from more_itertools.collapse(exceptions, base_type=str)


def python_functions_as_import_string(code_text: str, module_name: str) -> str:
    """."""
    import jinja2

    function_names = python_function_names(code_text)
    template = '''from {{ module_name }} import (
{%- for name in function_names %}
    {{ name }},
{%- endfor %}
)'''
    template = jinja2.Template(template)
    result = template.render(module_name=module_name, function_names=function_names)
    return result


def python_ast_object_line_number(ast_object: object) -> Optional[int]:
    """."""
    if hasattr(ast_object, 'lineno'):
        return ast_object.lineno
    else:
        return None


def python_ast_object_line_numbers(ast_object: object) -> Tuple[int, int]:
    """."""
    from d8s_algorithms import depth_first_traverse

    line_numbers = tuple(
        truthy_items(
            list(
                depth_first_traverse(
                    ast_object, ast.iter_child_nodes, collect_items_function=python_ast_object_line_number
                )
            )
        )
    )
    return min(line_numbers), max(line_numbers)


def _python_ast_clean(code_text: str) -> str:
    """."""
    import re

    return re.sub('\n', '\\\\n', code_text)


# TODO: have a decorator to parse a first argument that is a string
def python_ast_objects_of_type(
    code_text_or_ast_object: Union[str, object], ast_type: type, *, recursive_search: bool = True
) -> Iterable[object]:
    """Return all of the ast objects of the given ast_type in the code_text_or_ast_object."""
    if isinstance(code_text_or_ast_object, str):
        parsed_code = python_ast_parse(code_text_or_ast_object)
    else:
        parsed_code = code_text_or_ast_object

    if recursive_search:
        yield from (node for node in ast.walk(parsed_code) if isinstance(node, ast_type))
    else:
        if isinstance(parsed_code, ast_type):
            yield parsed_code

        if hasattr(parsed_code, 'body'):
            yield from (node for node in parsed_code.body if isinstance(node, ast_type))


def python_ast_objects_not_of_type(code_text_or_ast_object: Union[str, object], ast_type: type) -> Iterable[object]:
    """Return all of the ast objects which are not of the given ast_type in the code_text_or_ast_object."""
    from d8s_algorithms import depth_first_traverse

    if isinstance(code_text_or_ast_object, str):
        parsed_code = python_ast_parse(code_text_or_ast_object)
    else:
        parsed_code = code_text_or_ast_object

    ast_objects_not_of_type = truthy_items(
        list(
            depth_first_traverse(
                parsed_code,
                lambda x: ast.iter_child_nodes(x) if not isinstance(x, ast_type) else [],
                collect_items_function=lambda x: x,
            )
        )
    )
    return ast_objects_not_of_type

    # ast_objects_not_of_type = (node for node in ast.walk(parsed_code) if not isinstance(node, ast_type))
    # for node in ast.walk(parsed_code):
    #     if not isinstance(node, ast_type):
    #         yield node
    #     else:
    #         break

    # return ast_objects_not_of_type


def python_ast_parse(code_text: str) -> ast.Module:
    """."""
    try:
        parsed_code = ast.parse(code_text)
    except Exception:  # pylint: disable=W0703
        code_text = _python_ast_clean(code_text)
        parsed_code = ast.parse(code_text)
    return parsed_code


def python_ast_function_defs(code_text: str, recursive_search: bool = True) -> Iterable[ast.FunctionDef]:
    """."""
    yield from python_ast_objects_of_type(code_text, ast.FunctionDef, recursive_search=recursive_search)
    yield from python_ast_objects_of_type(code_text, ast.AsyncFunctionDef, recursive_search=recursive_search)


def python_function_arguments(function_text: str) -> List[ast.arg]:
    """."""
    parsed_code = python_ast_parse(function_text)
    args = parsed_code.body[0].args.args
    return args


def python_function_argument_names(function_text: str) -> Iterable[str]:
    """."""
    argument_names = (arg.arg for arg in python_function_arguments(function_text))
    return argument_names


def python_function_argument_defaults(function_text: str) -> List[str]:
    """."""
    # TODO: this function does not return defaults for keyword args
    parsed_code = python_ast_parse(function_text)
    return parsed_code.body[0].args.defaults


def python_function_argument_annotations(function_text: str) -> List[str]:
    """."""
    annotations = []
    args = python_function_arguments(function_text)
    for arg in args:
        if arg.annotation:
            annotations.append(arg.annotation.id)
        else:
            annotations.append(None)
    return annotations


def python_function_names(
    code_text: str, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False
) -> List[str]:
    """."""
    function_objects = python_ast_function_defs(code_text, recursive_search=not ignore_nested_functions)
    function_names = [f.name for f in function_objects]
    if ignore_private_functions:
        function_names = [name for name in function_names if not name.startswith('_')]
    return function_names


def python_function_docstrings(
    code_text: str, *, ignore_private_functions: bool = False, ignore_nested_functions: bool = False
) -> List[str]:
    """Get docstrings for all of the functions in the given text."""
    function_objects = python_ast_function_defs(code_text, recursive_search=not ignore_nested_functions)
    docstrings = [
        ast.get_docstring(f) for f in function_objects if not (ignore_private_functions and f.name.startswith('_'))
    ]
    return docstrings


def python_variable_names(code_text: str) -> List[str]:
    """Get all of the variables names in the code_text."""
    # TODO: add a caveat that this function will only find *stored* variables and not those which are referenced or...
    # loaded. E.g., given "x = y + 1", this function will return ["x"]; note that "y" is not included
    parsed_code = python_ast_parse(code_text)
    variable_names = [
        node.id for node in ast.walk(parsed_code) if isinstance(node, ast.Name) and (isinstance(node.ctx, ast.Store))
    ]
    return variable_names


def python_constants(code_text: str) -> List[str]:
    """Get all constants in the code_text."""
    # TODO: add a caveat that this function will only find *stored* variables which are uppercased
    variables = python_variable_names(code_text)
    constants = [var for var in variables if var.isupper()]
    return constants
