from ast import List
from collections import Counter, defaultdict
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

program_start = time_ns()

dicts: defaultdict[str, Counter[str]] = defaultdict(lambda: Counter())

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for unit in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        factory: str = 'None'
        for module in unit.value.by_member('ModulesDescriptors').value:
            module = module.value
            if isinstance(module, Object) and module.type == 'TProductionModuleDescriptor':
                factory = module.by_member('Factory').value.split('/')[1]
            if isinstance(module, Object) and module.type == 'TUnitUIModuleDescriptor':
                unit_role = module.by_member('UnitRole').value
                menu_icon = module.by_member('MenuIconTexture').value
                type_strategic_count = module.by_member('TypeStrategicCount').value
                dicts[factory][unit_role] += 1

columns = ["'tank_A'",
           "'tank_B'",
           "'tank_C'",
           "'tank_D'"]

def rows(_dict: defaultdict[str, set[str]]) -> Iterable[str]:
    for k, v in _dict.items():
        line = k
        for col in columns:
            line += f'\t{v[col]}'
        yield line
    

with open(os.path.join(FOLDER, f'factory_to_role.tsv.data'), 'w') as file:
    file.write('\n'.join(rows(dicts)))
print(time_since(program_start))