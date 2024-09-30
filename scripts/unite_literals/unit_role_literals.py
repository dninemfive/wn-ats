from ast import List
from collections import defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'unite_literals'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def is_object_of_type(item: Any, type: str) -> bool:
    return isinstance(item, Object) and item.type == type

program_start = time_ns()
values: defaultdict[str, set[str]] = defaultdict(lambda: set())
values_reverse: defaultdict[str, set[str]] = defaultdict(lambda: set())
with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for unit in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        for module in unit.value.by_member('ModulesDescriptors').value:
            module = module.value
            if isinstance(module, Object) and module.type == 'TUnitUIModuleDescriptor':
                unit_role, menu_icon = module.by_member('UnitRole').value, module.by_member('MenuIconTexture').value
                values[unit_role].add(menu_icon)
                values_reverse[menu_icon].add(unit_role)



values_reverse_unique: defaultdict[str, set[str]] = defaultdict(lambda: set())
values_reverse_all: set[str] = set()

for k, v in values_reverse.items():
    if all([x in v for x in values.keys()]):
        values_reverse_all.add(k)
    else:
        values_reverse_unique[k] = v

def lines(_dict: defaultdict[str, set[str]]) -> Iterable[str]:
    for k in sorted(_dict.keys()):
        yield k
        for v in sorted(_dict[k]):
            yield f'\t{v}'

with open(os.path.join(FOLDER, 'UnitRoles.data'), 'w') as file:
    file.write("\n".join(lines(values)))
with open(os.path.join(FOLDER, 'UnitRoles.reverse.unique.data'), 'w') as file:
    file.write('\n'.join(lines(values_reverse_unique)))
with open(os.path.join(FOLDER, 'UnitRoles.reverse.all.data'), 'w') as file:
    file.write('\n'.join(sorted(values_reverse_all)))
with open(os.path.join(FOLDER, 'UnitRole.txt'), 'w') as file:
    file.write('\n'.join(sorted(values.keys())))
print(time_since(program_start))