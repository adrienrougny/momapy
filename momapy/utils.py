import frozendict
import collections.abc


def str_obj(o, limit=30):
    def str_dict(d, limit=30):
        s = ""
        l = []
        for key in d:
            l.append(f"{str_obj(key, limit)}: {str_obj(d[key], limit)}")
        nl = "\n"
        return f"{nl.join(l)}"

    def str_set(s, limit=30):
        return f"{{{', '.join([str_obj(e, limit) for e in s])}}}"

    def str_tuple(t, limit=30):
        return f"({', '.join([str_obj(e, limit) for e in t])})"

    if isinstance(o, (collections.abc.Mapping)):
        return str_dict(o, limit)
    elif isinstance(o, (collections.abc.Set)):
        return str_set(o, limit)
    elif isinstance(o, (tuple)):
        return str_tuple(o, limit)
    s = str(o)
    if len(s) >= limit:
        s = f"{s[:limit]}..."
    return s
