from collections import Counter, defaultdict
import os
import sys
from time import time_ns
from typing import Any, Iterable, Literal

from ndf_parse import Mod
from ndf_parse.model import List, Object, Template

FamilyDefinition = tuple[str, int]

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'damage_resistance'

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()

print("Loading game damage data...")

def ensure_startswith(s: str, prefix: str) -> str:
    if not s.startswith(prefix):
        return f'{prefix}{s}'
    return s

vals: list[list[float]] = []
resistances: list[FamilyDefinition] = []
damages: list[FamilyDefinition] = []

def load_vals(data: Object) -> list[list[float]]:
    result: list[list[float]] = []
    values = data.by_member("Values").value
    for row in values:
        r = []
        for col in row.value:
            r.append(float(col.value))
        result.append(r)
    return result

def load_family(data: Object, type: Literal['Resistance', 'Damage']) -> list[FamilyDefinition]:
    family_list: List = data.by_member(f'{type}FamilyDefinitionList').value
    result: list[FamilyDefinition] = []
    for row in family_list:
        family_def: Object = row.value
        result.append((family_def.by_member('Family').value, int(family_def.by_member('MaxIndex').value)))
    return result

def get_index(families: list[FamilyDefinition], family: str, type: Literal['Resistance', 'Damage'], family_index: int) -> int:
    family = ensure_startswith(family, f'{type}Family_{family}')
    result: int = 0
    for name, maxIndex in families:
        if name == family:
            if family_index >= maxIndex:
                raise Exception(f'Specified index {family_index} is greater than the MaxIndex of specified family {family}!')
            return result + family_index
        result += maxIndex
    raise Exception(f"Didn't find family {family} in specified family list!")

with mod.edit('GameData/Generated/Gameplay/Gfx/DamageResistance.ndf') as file:
    print(time_since(program_start))
    damage_resistance: Object = file[0].value
    vals = load_vals(damage_resistance)
    resistances = load_family(damage_resistance, 'Resistance')
    damages = load_family(damage_resistance, 'Damage')

    col_index = get_index(resistances, sys.argv[3], 'Resistance', int(sys.argv[4]))
    row_index = get_index(damages, sys.argv[1], 'Damage', int(sys.argv[2]))

    print(f'Calculated damage suffered by target {sys.argv[3]} {sys.argv[4]} by incoming damage {sys.argv[3]}')
    

print(time_since(program_start))