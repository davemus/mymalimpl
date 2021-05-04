from mal_types import (
    is_number,
    is_symbol,
    is_string,
    is_keyword,
    is_function,
    is_list,
    is_vector,
    is_hashmap,
    is_atom,
    deref,
    is_nil,
    is_bool,
    TRUE,
    FALSE,
    MalException,
)


def pr_str(entity, print_readably=True):
    if isinstance(entity, MalException):
        return f'{pr_str(entity.value)}'
    if isinstance(entity, Exception):
        return entity.args[0]
    elif is_function(entity):
        return '#function'
    elif is_nil(entity):
        return 'nil'
    elif is_bool(entity):
        return {
            TRUE: 'true',
            FALSE: 'false',
        }[entity]
    elif is_number(entity):
        return str(entity)
    elif is_symbol(entity):
        return str(entity, 'utf-8')
    elif is_keyword(entity):
        return ':' + entity[1:]
    elif is_string(entity):
        if print_readably:
            return '"' + entity.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
        return entity
    elif is_atom(entity):
        return f'(atom {deref(entity)})'
    elif is_list(entity):
        return '(' + ' '.join(pr_str(inner, print_readably) for inner in entity) + ')'
    elif is_vector(entity):
        return '[' + ' '.join(pr_str(inner, print_readably) for inner in entity) + ']'
    elif is_hashmap(entity):
        return (
            '{'
            + ' '.join(f'{pr_str(k, print_readably)} {pr_str(v, print_readably)}' for k, v in entity.items())
            + '}'
        )
    raise RuntimeError(f'pr_str: unknown type {type(entity)}')
