import enum
import json
from pathlib import Path
from typing import Union

_NoneType = type(None)
_AnyType = Union[_NoneType, list, dict, str, int, float, bool]
_AnyPath = Union[str, Path]

class _KeyValue:
    """Store a key-value pair, and allow it to be converted as a tuple."""

    def __init__(self, key: str, value: _AnyType):
        self.key: str = key
        self.value = value

    def asiterable(self):
        """Return the key-value pair as a tuple."""
        return (self.key, self.value)

class _Type(enum.Enum):
    """Store the type of a value."""

    NONETYPE = _NoneType
    LIST = list
    DICT = dict
    STRING = str
    INT = int
    FLOAT = float
    BOOL = bool

    def is_primitive(self) -> bool:
        """Check if the type is a primitive type."""
        return self in [_Type.STRING, _Type.INT, _Type.FLOAT, _Type.BOOL]

    def is_none(self) -> bool:
        """Check if the type is None."""
        return self == _Type.NONETYPE

class JSONDecoder:
    """Decode a JSON file into a Python object."""

    def __init__(self, path: _AnyPath):
        self.path: Path = Path(path)
        self.data = None
        self._load()

    def run(self):
        """Run the decoder."""
        return JSONDecoder._convert('root', self.data).value

    def _load(self) -> None:
        """Load the JSON file. This method is private, and automatically called by the constructor."""
        try:
            with open(self.path.as_posix(), 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print('File not found.')
            exit(1)
        except json.JSONDecodeError:
            print('Invalid JSON.')
            exit(1)
        
    def print_structure(self, indentstep: int=4) -> None:
        """Print the structure of the JSON file."""
        if indentstep < 1:
            raise ValueError('indentstep must be at least 1.')

        self.istep = indentstep
        self._print_structure('root', self.data)

    def _print_structure(self, name: str, value: _AnyType, indent: int = 0) -> None:
        """Print the structure of the JSON file. This method is private, and automatically called by the print_structure property."""

        dtype = _Type(type(value))
        
        if dtype.is_primitive():
            prefix = f"{' ' * (indent-1)}─"
            print(f'{prefix}{name:12s}/{dtype.name.lower()}/')
            return

        if name=="root":
            print(f".")
        else:
            prefix = f"{' '*(indent - self.istep)}└{'─'* (self.istep-1)}"
            print(f"{prefix}{name} /{dtype.value.__name__}/")

        if dtype == _Type.DICT:
            for key, value in value.items():
                self._print_structure(key, value, indent + self.istep)

        if dtype == _Type.LIST:
            for index, value in enumerate(value):
                self._print_structure(f"#{index}", value, indent + self.istep)

    @staticmethod
    def _convert(key: str, data: _AnyType) -> _KeyValue:
        """Convert a key-value pair into a _KeyValue object. This is done recursively to go through the whole content of a JSON file. The inputs are a key and a value. The key is describing the content's nature of the value."""
        dtype = _Type(type(data))
        
        if dtype.is_primitive() or dtype.is_none():
            return _KeyValue(key, data)

        if dtype == _Type.LIST:
            value = [JSONDecoder._convert(key, item).value for item in data]
            return _KeyValue(key, value)

        if dtype == _Type.DICT:
            value = JSONDecoder._new_class(key, data)
            return _KeyValue(key, value)

        raise TypeError(f'Unsupported type: {dtype} ({type(data)})')     

    
    @staticmethod
    def _new_class(name: str, data:dict):
        """Create a new class from a dictionary."""
        class_ = type(name.capitalize(), (), {})

        for pair in data.items():
            setattr(class_, *JSONDecoder._convert(*pair).asiterable())

        return class_