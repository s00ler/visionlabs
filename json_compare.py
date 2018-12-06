import json


def load_json(path):
    """Load json obj from file."""
    with open(path, 'r') as f:
        obj = json.load(f)
    return obj


def compare_floats(f, s):
    """Compare float with 5 digits precision.

    Precision may come as an arg, may use partial here, etc.
    """
    return int(f * 100000) == int(s * 100000)


def compare_json(obj1, obj2):
    """Compare two json objects."""
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        keys = obj1.keys()
        if keys == obj2.keys():
            for key in keys:
                if not compare_json(obj1[key], obj2[key]):
                    return False
            return True
        return False
    elif isinstance(obj1, list) and isinstance(obj2, list):
        if len(obj1) == len(obj2):
            for el1, el2 in zip(obj1, obj2):
                if not compare_json(el1, el2):
                    return False
            return True
        return False
    elif isinstance(obj1, float) and isinstance(obj2, float):
        return compare_floats(obj1, obj2)
    else:
        return (obj1 is None and obj2 is None) or (obj1 == obj2)
