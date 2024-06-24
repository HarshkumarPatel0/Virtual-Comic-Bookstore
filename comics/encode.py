END = 128
MASK = 127
OBJECT = 64
NEGATIVE = 32
FLOAT = 16
BITS = 7

ids = {}
tables = {}

def exists(tables, table, id):
    model = tables[table]["data"].get(id)
    if isinstance(model, bytes):
        return unpack(model)
    return model

def pack(lst):
    data = []
    for value in lst:
        if isinstance(value, float):
            flt = FLOAT
            value = int(value * 100)
        else:
            flt = 0
        if isinstance(value, str):
            # Since objects are on 16 byte boundaries we can ignore low 4 bits
            val = id(value) >> 4
            if value == '':
                val = 1
            ids[val] = value
            while True:
                low = val & MASK
                val >>= BITS
                if not val and low < OBJECT:
                    data.append(low | (END + OBJECT))
                    break
                data.append(low)
            continue
        if value is None:
            data.append(END + OBJECT)
            continue
        if value < 0:
            negative = NEGATIVE
            value = -value
        else:
            negative = 0
        while True:
            low = value & MASK
            value >>= BITS
            if not value and low < FLOAT:
                data.append(low | (END + flt + negative))
                break
            data.append(low)

    return bytes(data)

def unpack(packed):
    value = 0
    data = []
    shift = 0
    for val in packed:
        low = val & MASK
        if val & END:
            object = val & OBJECT
            negative = val & NEGATIVE
            flt = val & FLOAT
            if object:
                val &= OBJECT - 1
                value |= val << shift
                if not value:
                    value = None
                elif value == 1:
                    value = ''
                else:
                    value = ids.get(value, "**ERROR**")
            else:
                val &= FLOAT-1
                value |= val << shift
                if negative:
                    value = -value
                if flt:
                    value /= 100.0
            data.append(value)
            value = 0
            shift = 0
        else:
            value |= low << shift
            shift += BITS
    return data

