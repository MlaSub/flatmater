from sqlalchemy import inspect


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def union(lst1: list, lst2: list) -> list:
    final_list = list(set(lst1) | set(lst2))
    return final_list
