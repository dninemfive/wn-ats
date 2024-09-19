from typing import Self
from ndf_parse import Mod
from ndf_parse.model import List
from ndf_parse.model.abc import CellValue

class TypeSet(object):
    def __init__(self: Self, type: str):
        self.types = set(type)

    def add(self: Self, type: type):
        self.types.add(type)

    def __str__(self: Self) -> str:
        return " | ".join(s for s in sorted(self.types))
    
def get_all_ndf_files(mod: Mod): # -> Generator[List]
    raise NotImplemented

def determine_types_in_list(list: List) -> set[str]:
    raise NotImplemented

def determine_type(val: CellValue) -> str:
    raise NotImplemented

def generate_class_file(type_name: str, members: dict[str, TypeSet]) -> None:
    def generate_rows():
        yield 'from dataclasses import dataclass'
        yield ''
        yield '@dataclass'
        yield f'class {type_name}(object):'
        for k, v in members:
            yield f'{k}: {str(v)}'
    with open(f'{type_name}.py', 'w') as file:
        file.write('\n'.join(generate_rows()))

seen_types: dict[str, dict[str, TypeSet]] = {}
mod = Mod("", "")

for l in get_all_ndf_files(mod):
    pass