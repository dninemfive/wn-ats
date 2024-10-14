from collections import Counter, defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'unite_literals'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

dicts: defaultdict[str, Counter[str]] = defaultdict(lambda: Counter())

def has_module(modules_descriptors: List, module: str) -> bool:
    try:
        modules_descriptors.find_by_cond(lambda x: isinstance(x.value, Object) and x.value.type == module).value
        return True
    except:
        return False
    
def has_module_by_n(modules_descriptors: List, module: str) -> bool:
    try:
        modules_descriptors.by_name(module).value
        return True
    except:
        return False

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    print(time_since(program_start))
    for row in file:
        # name: str = unit.value.by_member('ClassNameForDebug').value
        # print(name)
        unit: Object = row.value
        modules_descriptors: List = unit.by_member('ModulesDescriptors').value
        if has_module(modules_descriptors, 'TInfantrySquadWeaponAssignmentModuleDescriptor') and has_module_by_n(modules_descriptors, 'MissileCarriage'):
            print(unit.by_member('ClassNameForDebug').value)