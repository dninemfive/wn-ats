import os
from typing import Any, Self
from ndf_parse import Mod
from ndf_parse.model import List, ListRow, MemberRow, Object
import ndf_parse.model.abc as abc


class TypeAnnotation(object):
    def __init__(self: Self, type: str):
        self.types = set(type)

    def add(self: Self, type: str):
        self.types.add(type)

    def __str__(self: Self) -> str:
        return " | ".join(s for s in sorted(self.types))
    
class Type(object):
    def __init__(self: Self, name: str, current_file: str):
        self.name = name
        self.dict: dict[str, TypeAnnotation] = {}
        self.found_in_files: set[str] = set([current_file])

    def update(self: Self, member_name: str, type: str, current_file: str) -> None:
        if member_name in self.dict:
            self.dict[member_name].add(type)
        else:
            self.dict[member_name] = TypeAnnotation(type)

    def members(self: Self): # -> Generator[tuple[str, TypeSet]]
        for k, v in self.dict.items():
            yield (k, v)

class TypeSet(object):
    def __init__(self: Self):
        self.types: dict[str, Type] = {}

    def add(self: Self, type_name: str):
        if type_name not in self.types:
            self.types[type_name] = Type(type_name)

    def get(self: Self, type_name: str) -> Type:
        return self.types[type_name]
    
def get_all_ndf_files(mod: Mod, root_folder: str): # -> Generator[tuple[str, List]]
    all_ndf: set[str] = set()
    # https://stackoverflow.com/a/3207973
    for _, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.ndf':
                all_ndf.add(filename)
    for path in sorted(all_ndf):
        yield (path, mod.edit(path, save=False).current_tree)

def determine_types_in_list(list: List) -> set[str]:
    raise NotImplemented

def is_type(s: str, t: type) -> bool:
    try:
        return isinstance(t(s), t)
    except:
        return False

def determine_type(val: Any) -> str:
    raise NotImplemented

def profile_members(obj: Object) -> dict[str, TypeAnnotation]:
    result: dict[str, TypeAnnotation]
    member: MemberRow
    for member in obj:
        pass

def generate_class_file(type_name: str, members: dict[str, TypeAnnotation]) -> None:
    def generate_rows():
        yield 'from dataclasses import dataclass'
        yield ''
        yield '@dataclass'
        yield f'class {type_name}(object):'
        for k, v in members:
            yield f'{k}: {str(v)}'
    with open(f'types/{type_name}.py', 'w') as file:
        file.write('\n'.join(generate_rows()))

def list_type(list: List) -> TypeAnnotation:
    pass

seen_types = TypeSet()
# mod = Mod("", "")

s = "1.0"
print(is_type(s, int))
print(is_type(s, float))
print(is_type(s, str))