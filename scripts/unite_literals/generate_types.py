from collections import defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'unite_literals'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def is_object_of_type(item: Any, type: str) -> bool:
    return isinstance(item, Object) and item.type == type

program_start = time_ns()
vars: defaultdict[str, set[str]] = defaultdict(lambda: set())

def add(unit: ListRow, *targets: tuple[str, list[str]]) -> str:
    for module_row in unit.value.by_member('ModulesDescriptors').value:
        module = module_row.value
        if isinstance(module, Object):
            for type, members in targets:
                if module.type == type:
                    for member in members:
                        vars[f'{type}.{member}'].add(module.by_member(member).value)

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for unit in file:
        add(unit,  ('TTypeUnitModuleDescriptor',
                        ['Nationalite',
                         'MotherCountry',
                         'AcknowUnitType',
                         'TypeUnitFormation']),
                   ('TProductionModuleDescriptor',
                        ['Factory']),
                   ('TUnitUIModuleDescriptor',
                        ['UnitRole',
                         'InfoPanelConfigurationToken',
                         'TypeStrategicCount']))


def literal_line(name: str, values: set[str]) -> str:
    def quote(s: str) -> str:
        if "'" in s:
            return f'"{s}"'
        else:
            return f"'{s}'"
    return f'{f'type {name.split('.')[-1]}'.ljust(40)} = Literal[{', '.join([quote(s) for s in values])}]'

with open(os.path.join(FOLDER, f'literals.py.data'), 'w') as file:
    file.write('\n'.join([literal_line(k, v) for k, v in vars.items()]))
print(time_since(program_start))