import os
from typing import Any, Self
from ndf_parse import Mod
from ndf_parse.model import List, ListRow, MemberRow, Object
import ndf_parse.model.abc as abc
import re

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

def is_type(x: Any, t: type) -> bool:
    if isinstance(x, t):
        return True
    try:
        return isinstance(t(str(x)), t)
    except:
        return False

def strip_type(type_str: str) -> str:
    return type_str.split("'")[1]

PRIMITIVE_TYPES = [int, float] #, bool : apparently bool(any_str) is a bool??

def determine_type(val: Any) -> str:
    for t in PRIMITIVE_TYPES:
        if is_type(val, t):
            return strip_type(str(t))
    # ???
    match = re.search('True', str(t))
    print(f'match: {str(match)}')
    if match is not None:
        return 'bool'
    if isinstance(val, Object):
        return val.type

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

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'

mod = Mod(MOD_PATH, MOD_PATH)

l = mod.edit(rf"GameData\Generated\Gameplay\Decks\Divisions.ndf", False).current_tree

tests = [
    "1",
    "1.0",
    "True",
    "test",
    l[0]
]
for item in tests:
    print(str(item)[:15], determine_type(item))