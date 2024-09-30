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
dicts: defaultdict[str, defaultdict[str, set[str]]] = defaultdict(lambda: defaultdict(lambda: set()))
# dicts_reverse: defaultdict[str, defaultdict[str, set[str]]] = defaultdict(lambda: defaultdict(lambda: set()))

def add(dict: str, k: str, v: str):
    dicts[dict][v].add(k)
    # dicts_reverse[dict][v].add(k)

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for unit in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        for module in unit.value.by_member('ModulesDescriptors').value:
            module = module.value
            if isinstance(module, Object) and module.type == 'TUnitUIModuleDescriptor':
                unit_role = module.by_member('UnitRole').value
                menu_icon = module.by_member('MenuIconTexture').value
                type_strategic_count = module.by_member('TypeStrategicCount').value
                add('UnitRoles_to_MenuIconTextures', unit_role, menu_icon)
                add('UnitRoles_to_TypeStrategicCounts', unit_role, type_strategic_count)

def summarize(_dict: defaultdict[str, set[str]]) -> Iterable[str]:
    asdf: defaultdict[str, set[str]] = defaultdict(lambda: set())
    for k, v in _dict.items():
        new_key = ', '.join(sorted(v))
        asdf[new_key].add(k)

    for k in sorted(asdf.keys()):
        yield f'{k}: {', '.join(sorted(asdf[k]))}'


for name, dict in dicts.items():
    with open(os.path.join(FOLDER, f'{name}.data'), 'w') as file:
        file.write('\n'.join(summarize(dict)))
print(time_since(program_start))