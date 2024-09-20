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
            self.add(type)     

    def add(self: Self, type: str):
        if type is None:
            raise ValueError('type must not be None')
        self.types.add(strip_type_and_model(type))

    def __str__(self: Self) -> str:
        return " | ".join(s for s in sorted(self.types))
    
class Type(object):
    def __init__(self: Self, name: str, current_file: str):
        self.name = name
        self.dict: dict[str, TypeAnnotation] = {}
        self.found_in_files: set[str] = set([current_file])

    def update(self: Self, member_name: str, type: str) -> None:
        if member_name is None:
            member_name = "None_"
        if member_name in self.dict:
            self.dict[member_name].add(type)
        else:
            self.dict[member_name] = TypeAnnotation(type)

    @property
    def unique_member_types(self: Self):
        result = set()
        for v in self.dict.values():
            for t in v.types:
                for s in re.split(r'[\[\|\]]', t):
                    result.add(s.strip())
        return sorted(result)

    @property
    def members(self: Self): # -> Generator[tuple[str, TypeSet]]
        for k, v in self.dict.items():
            yield (k, v)

    @property 
    def found_in_string(self: Self) -> str:
        return "\n# ".join(['# Found in:', *self.found_in_files])
    
    @property
    def ndf_types(self: Self):
        return [x for x in self.unique_member_types if is_ndf_type(x)]

    @property
    def ndf_type_string(self: Self) -> str:
        types = self.ndf_types
        print("types:", types)
        if len(types) < 1:
            return ''
        type_lines = [f'from ndf_types.{x} import {x}' for x in types]
        return '\n'.join(['', *type_lines, ''])

    @property
    def class_string(self: Self) -> str:
        return '\n'.join(['@dataclass',
                         f'class {self.name}(object):',
                         *[f'    {k}: {str(v)}' for k, v in self.members]])
    
    def __str__(self: Self) -> str:
        result = '\n'.join([self.found_in_string,
                           '',
                           'from dataclasses import dataclass',
                           'from ndf_parse.model import List, ListRow, Map, MapRow, MemberRow, Object, Template',
                           self.ndf_type_string,
                           self.class_string])
        return result
        
    
    def write(self: Self) -> None:
        print(f'  {self.name}')
        with open(f'ndf_types/{self.name}.py', 'w') as file:
            file.write(str(self))

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
        print("Writing all types...")
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
    try:
        return type.split("'")[1]
    except:
        return type

def strip_type_and_model(type: str | type) -> str:
    return strip_type(type).removeprefix('ndf_parse.model.')

def is_ndf_type(s: str) -> bool:
    result = len(s) > 0 and not (s in ["bool", "int", "float", "str", "List", "ListRow", "Map", "MapRow", "MemberRow", "Object", "Template"] or '[' in s or '|' in s or ']' in s)
    print(f'is_ndf_type({s}) = {result}')
    return result

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
        return f'{strip_type_and_model(type(val))}[{determine_type(val.value)}]'
    if isinstance(val, (List | Map)):
        return f'{strip_type_and_model(type(val))}[{determine_types_in_list(val)}]'
    return "str" # TODO: refptr determination?

def profile(object: Object | abc.Row | abc.List, global_types: TypeSet, current_file: str, indent: int = 0) -> None:
    # print(f'{'  ' * indent}{strip_type_and_model(type(object))}')
    if is_primitive(object):
        return
    if isinstance(object, Object):
        obj_type = global_types.add(object, current_file)
        for member in object:
            obj_type.update(member.member, determine_type(member.value))
    elif isinstance(object, (ListRow, MapRow, MemberRow)):
        profile(object.value, global_types, current_file, indent + 1)
    else:
        try:
            for item in object:
                profile(item, global_types, current_file, indent + 1)
        # https://stackoverflow.com/a/4992124
        except Exception as e:
            logger.error(f'failed to profile {strip_type_and_model(type(object))} {str(object)[:30]}: {str(e)}')

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)
global_types = TypeSet()

count = 0
for current_dir, _, filenames in os.walk(GENERATED_PATH):
    for filename in filenames:
        filename = os.path.relpath(os.path.join(current_dir, filename), MOD_PATH)        
        print(str(count).rjust(5), filename)
        count += 1
        if os.path.splitext(filename)[1] == '.ndf':
            try:
                with mod.edit(filename, False, False) as cur:
                    profile(cur, global_types, filename)
            except Exception as e:
                logger.error(f'failed to load {filename}: {str(e)}')
global_types.write_all()
imports = []
for _, _, filenames in os.walk('ndf_types'):
    for filename in filenames:
        imports.append(f'import ndf_types.{os.path.splitext(filename)[0]}')
    break
with open('ndf_types/__init__.py', 'w') as file:
    file.write('\n'.join(imports))