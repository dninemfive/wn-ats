from ast import List
from collections import defaultdict
import os
from time import time_ns
from typing import Any

from ndf_parse import Mod
from ndf_parse.model import Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def is_object_of_type(item: Any, type: str) -> bool:
    return isinstance(item, Object) and item.type == type

program_start = time_ns()
values: defaultdict[str, set[str]] = defaultdict(lambda: set())
with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for unit in file:
        name: str = unit.value.by_member('ClassNameForDebug').value
        print(name)
        for module in unit.value.by_member('ModulesDescriptors').value:
            if isinstance(module.value, Object) and module.value.type == 'TUnitUIModuleDescriptor':
                values[module.value.by_member('UnitRole').value].add(name)

lines = []
for k in sorted(values.keys()):
    lines.append(k)
    for v in sorted(values[k]):
        lines.append(f'\t{v}')

with open('UnitRoles.data', 'w') as file:
    file.write("\n".join(lines))
with open('UnitRole.txt', 'w') as file:
    file.write('\n'.join(sorted(values.keys())))
print(time_since(program_start))