from collections import Counter, defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'UniteDescriptor/TUnitUIModuleDescriptor/Fields'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

fields: dict[str, set[str]] = {x: set() for x in ['UnitRole', 'InfoPanelConfigurationToken', 'MenuIconTexture', 'CountryTexture', 'TypeStrategicCount']}

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for row in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        unit: Object = row.value
        modules_descriptors: List = unit.by_member('ModulesDescriptors').value
        ui_module: Object = modules_descriptors.find_by_cond(lambda x: isinstance(x.value, Object)
                                                     and x.value.type == 'TUnitUIModuleDescriptor').value
        for k, v in fields.items():
            v.add(ui_module.by_member(k).value)

for k, v in fields.items():
    with open(os.path.join(FOLDER, f'{k}.txt.data'), 'w') as file:
        file.write('\n'.join(sorted(v)))
print(time_since(program_start))