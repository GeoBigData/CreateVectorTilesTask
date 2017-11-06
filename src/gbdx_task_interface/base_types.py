class Int(int):
    """Sub-classes int so that we can pass additional arguments on creation."""
    def __new__(cls, value, *args, **kwargs):
        return super(Int, cls).__new__(cls, value)

    def __init__(self, *args, **kwargs):
        super(Int, self).__init__()

    def __add__(self, other):
        return self.__class__(super(Int, self).__add__(other))

    def __sub__(self, other):
        return self.__class__(super(Int, self).__sub__(other))

    def __mul__(self, other):
        return self.__class__(super(Int, self).__mul__(other))

    def __div__(self, other):
        return self.__class__(super(Int, self).__div__(other))


class Mapping(dict):
    """Sub-classes dict so we can pass additional arguments at creation."""
    def __new__(cls, value, *args, **kwargs):
        return super(Mapping, cls).__new__(cls, value)


class Bool(int):
    def __new__(cls, value, *args, **kwargs):
        value = bool(value)
        value = 1 if value else 0
        return super(Bool, cls).__new__(cls, value)

    def __repr__(self):
        if self == 0:
            return 'False'
        else:
            return 'True'


class List(list):
    def __new__(cls, value, *args, **kwargs):
        return super(List, cls).__new__(cls, value)


class String(str):
    def __new__(cls, value,  *args, **kwargs):
        return super(String, cls).__new__(cls, value)

    def __coerce__(self, other):
        print(other)
        return self
