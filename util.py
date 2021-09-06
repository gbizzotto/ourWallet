
def to_dict(obj):
    if isinstance(obj, (int,bool,str)) or obj is None:
        return obj
    elif isinstance(obj, (bytes,bytearray)):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k:to_dict(v) for k,v in obj.items()}
    elif isinstance(obj, list):
        return [to_dict(o) for o in obj]
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return {k:to_dict(v) for k,v in obj.__dict__.items()}
    else:
        return obj.__repr__()

def int_to_bytes(i: int, *, signed: bool = False) -> bytes:
    length = ((i + ((i * signed) < 0)).bit_length() + 7 + signed) // 8
    return i.to_bytes(length, byteorder='big', signed=signed)

