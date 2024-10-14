from collections import Counter, defaultdict
import os
from time import time_ns
from typing import Any, Iterable

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template
from ndf_parse.model.abc import CellValue

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'GeneratedDepictionVehicles'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

def summarize(value: List | str) -> str | list[str]:
    if isinstance(value, str):
        return value
    result = []
    for item in value:
        result.append(str(item.value))
    return result

# hypothesis: the X in `fx_tourelleX_tir_0*`, `weapon_effet_tagX`, `WeaponShootData_0_x`,
# and `WeaponActiveAndCanShoot_X` is the same for any given DepictionOperator_WeaponContinuousFire
def isrelevant(op: CellValue) -> bool:
    return isinstance(op, Object) and op.type == 'DepictionOperator_WeaponContinuousFire'

def hypothesis(op: Object) -> bool:
    values: list[int] = []
    values.append(int(op.by_member('FireEffectTag').value[len('"weapon_effet_tag'):-1]))
    values.append(int(op.by_member('WeaponShootDataPropertyName').value[len('"WeaponShootData_0_'):-1]))
    values.append(int(op.by_member('WeaponActiveAndCanShootPropertyName').value[len('"WeaponActiveAndCanShoot_'):-1]))
    for anchor in op.by_member('Anchors').value:
        values.append(int(anchor.value[len('"fx_tourelle'):-len('_tir_xx"')]))
    true: bool = all(x == values[0] for x in values)
    if not true:
        print(str(values))
    return true 

program_start = time_ns()

files = ['Vehicles', 'AerialUnits']


for filename in files:
    violations: int = 0
    subtypes: defaultdict[str, defaultdict[str, set[str]]] = defaultdict(lambda: defaultdict(lambda: set()))

    with mod.edit(f'GameData/Generated/Gameplay/Gfx/Depictions/GeneratedDepiction{filename}.ndf') as data:
        for row in data:
            obj: Object = row.value
            if isrelevant(obj) and not hypothesis(obj):
                print(row.namespace)
                violations += 1

    print(f'Violations in {filename}:', violations)
print(time_since(program_start))