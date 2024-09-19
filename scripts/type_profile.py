import os
import logging
import re
import traceback
from typing import Any, Self

import ndf_parse.model.abc as abc
from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Map, MapRow, MemberRow, Object, Template
# https://docs.python.org/3/library/logging.html
logger = logging.getLogger(__name__)


class TypeAnnotation(object):
    def __init__(self: Self, type: str | None = None):
        self.types: set[str] = set()
        if type is not None:
            self.types.add(type)        

    def add(self: Self, type: str):
        if type is None:
            raise ValueError('type must not be None')
        self.types.add(type)

    def __str__(self: Self) -> str:
        return " | ".join(s for s in sorted(self.types))
    
class Type(object):
    def __init__(self: Self, name: str, current_file: str):
        self.name = name
        self.dict: dict[str, TypeAnnotation] = {}
        self.found_in_files: set[str] = set([current_file])

    def update(self: Self, member_name: str, type: str) -> None:
        if member_name in self.dict:
            self.dict[member_name].add(type)
        else:
            self.dict[member_name] = TypeAnnotation(type)

    @property
    def members(self: Self): # -> Generator[tuple[str, TypeSet]]
        for k, v in self.dict.items():
            yield (k, v)

    @property
    def class_string(self: Self) -> str:
        def generate_rows():
            yield 'from dataclasses import dataclass'
            yield ''
            yield '@dataclass'
            yield f'class {self.name}(object):'
            for k, v in self.members:
                yield f'    {k}: {str(v)}'
        return "\n".join(generate_rows())
    
    def write(self: Self) -> None:
        with open(f'types/{self.name}.py', 'w') as file:
            file.write(self.class_string)

class TypeSet(object):
    def __init__(self: Self):
        self.types: dict[str, Type] = {}

    def add(self: Self, obj: Object | Template | str, current_file: str) -> Type:
        type_name: str
        if isinstance(obj, (Object, Template)):
            type_name = obj.type
        else:
            type_name = obj
        if type_name not in self.types:
            self.types[type_name] = Type(type_name, current_file)
        return self.types[type_name]

    def get(self: Self, type_name: str) -> Type:
        return self.types[type_name]
    
    def write_all(self: Self) -> None:
        for _, t in self.types.items():
            t.write()
    
def get_all_ndf_files(mod: Mod, root_folder: str): # -> Generator[tuple[str, List]]
    all_ndf: set[str] = set()
    # https://stackoverflow.com/a/3207973
    for _, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.ndf':
                all_ndf.add(filename)
    for path in sorted(all_ndf):
        yield (path, mod.edit(path, save=False).current_tree)

def determine_types_in_list(list: List) -> TypeAnnotation:
    result = TypeAnnotation()
    for item in list:
        result.add(determine_type(item))
    return result

def is_type(x: Any, t: type) -> bool:
    if isinstance(x, t):
        return True
    try:
        return isinstance(t(str(x)), t)
    except:
        return False

def strip_type(type: str | type) -> str:
    if not isinstance(type, str):
        type = str(type)
    return type.split("'")[1]

PRIMITIVE_TYPES = [int, float] #, bool : apparently bool(any_str) is a bool??

def is_primitive(val: Any) -> bool:
    return not isinstance(val, (abc.List, abc.Row))

def determine_type(val: Any) -> str:
    for t in PRIMITIVE_TYPES:
        if is_type(val, t):
            return strip_type(str(t))
    if re.search('^([Tt]rue|[Ff]alse)$', str(val)):
        return 'bool'
    if isinstance(val, Object):
        return val.type
    if isinstance(val, (ListRow, MapRow, MemberRow)):
        return determine_type(val.value)
    if isinstance(val, (List | Map)):
        return f'{strip_type(type(val))}[{determine_types_in_list(val)}]'
    return "str" # TODO: refptr determination?

def profile(object: Object | abc.Row | abc.List, global_types: TypeSet, current_file: str) -> None:
    if is_primitive(object):
        return
    if isinstance(object, Object):
        obj_type = global_types.add(object, current_file)
        for member in object:
            obj_type.update(member.member, determine_type(member.value))
    elif isinstance(object, (ListRow, MapRow, MemberRow)):
        profile(object.value, global_types, current_file)
    else:
        try:
            for item in object:
                profile(item, global_types, current_file)
        # https://stackoverflow.com/a/4992124
        except Exception as e:
            logger.error(f'Failed to profile {strip_type(type(object))} {str(object)}: {traceback.format_exc()}')

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'

mod = Mod(MOD_PATH, MOD_PATH)
global_types = TypeSet()

for current_dir, _, filenames in os.walk(MOD_PATH):
    for filename in filenames:
        filename = os.path.relpath(os.path.join(current_dir, filename), MOD_PATH)
        if os.path.splitext(filename)[1] == '.ndf':
            try:
                with mod.edit(filename, False, False) as cur:
                    profile(cur, global_types, filename)
            # https://stackoverflow.com/a/4992124
            except Exception as e:
                logger.error(f'Error in {filename}: {traceback.format_exc()}')
global_types.write_all()