from collections import defaultdict
from enum import member
import os
from time import time_ns
from typing import Any, Callable, Iterable, Literal, Self

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'UniteDescriptor'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def is_object_of_type(item: Any, type: str) -> bool:
    return isinstance(item, Object) and item.type == type

program_start = time_ns()

def quote(s: str) -> str:
    return f"'{s}'"

def unquote(s: str) -> str:
    if s.startswith("'"):
        s = s[1:]
    if s.endswith("'"):
        s = s[:-1]
    return s

def strip_prefix(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        print(f"{s} does not start with {prefix}!")

def strip_prefix_and_quotes(s: str, prefix: str | None) -> str:
    if prefix is not None:
        return strip_prefix(unquote(s), prefix)
    else:
        return unquote(s)

PREFIX, QUOTES = 'NdfEnum.with_path', 'NdfEnum.literals'
CONSTRUCTOR_LEN = max(len(PREFIX), len(QUOTES))
PREFIX, QUOTES = PREFIX.rjust(CONSTRUCTOR_LEN), QUOTES.rjust(CONSTRUCTOR_LEN)
MEMBER_LEN = 40
ENUM_INDENT = "".rjust(CONSTRUCTOR_LEN + MEMBER_LEN + len('= ('))
LITERAL_INDENT = "".rjust(MEMBER_LEN + len('= Literal['))

class MemberDef(object):
    def __init__(self: Self, member_name: str, prefix: str | None = None, is_list_type: bool = False):
        self.member_name = member_name
        self.prefix = prefix
        self.values: set[str] = set()
        self.is_list_type = is_list_type

    def add(self: Self, row: ListRow) -> None:
        if not self.is_list_type:
            self.values.add(strip_prefix_and_quotes(row.value, self.prefix))
        else:
            for item in row.value:
                item: ListRow
                self.values.add(strip_prefix_and_quotes(item.value, self.prefix))

    def enum_line(self: Self) -> str:
        constructor: str = PREFIX if self.prefix is not None else QUOTES
        items = [quote(x) for x in sorted(self.values)]
        if self.prefix is not None:
            items.insert(0, quote(self.prefix))
        return f'{self.member_name.ljust(MEMBER_LEN)}= {constructor}({f',\n{ENUM_INDENT}'.join(items)})'
    
    def literal_line(self: Self) -> str:
        items = [quote(x) for x in sorted(self.values)]
        return f'{self.member_name.ljust(MEMBER_LEN)}= Literal[{f',\n{LITERAL_INDENT}'.join(items)}]'


targets: dict[str, list[MemberDef]] = {
    'TTypeUnitModuleDescriptor': [
        MemberDef('Nationalite', 'ENationalite/'),
        MemberDef('MotherCountry'),
        MemberDef('AcknowUnitType', '~/TAcknowUnitType_'),
        MemberDef('TypeUnitFormation')
    ],
    'TProductionModuleDescriptor': [
        MemberDef('Factory', 'EDefaultFactories/')
    ],
    'TUnitUIModuleDescriptor': [
        MemberDef('UnitRole'),
        MemberDef('InfoPanelConfigurationToken'),
        MemberDef('TypeStrategicCount', 'ETypeStrategicDetailedCount/'),
        MemberDef('MenuIconTexture', 'Texture_RTS_H_'),
        MemberDef('SpecialtiesList', is_list_type=True)
    ]
}

def add(unit: ListRow) -> str:
    for module_row in unit.value.by_member('ModulesDescriptors').value:
        module = module_row.value
        if isinstance(module, Object) and module.type in targets:
            for member_def in targets[module.type]:
                member_def.add(module.by_member(member_def.member_name))

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for unit in file:
        add(unit)

def tolines(line_selector: Callable[[MemberDef], str]) -> Iterable[str]:
    for v in targets.values():
        for m in sorted(v, key=lambda x: x.member_name):
            yield line_selector(m)

def write(name: str, selector: Callable[[MemberDef], str]) -> None:
    with open(os.path.join(FOLDER, f'{name}.py.data'), 'w') as file:
        file.write('\n\n'.join(tolines(selector)))

write('enums', MemberDef.enum_line)
write('literals', MemberDef.literal_line)
print(time_since(program_start))