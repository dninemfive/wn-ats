import os
from time import time_ns

from ndf_parse import Mod
from ndf_parse.model import Object

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'.rjust(9)

program_start = time_ns()
unique_operators: set[str] = set()
with mod.edit('GameData/Generated/Gameplay/Gfx/Infanterie/GeneratedDepictionInfantry.ndf') as file:
    for row in file:
        value = row.value
        if isinstance(value, Object) and value.type == 'TemplateInfantryDepictionSquad':
            unique_operators.add(value.by_member('SoundOperator').value)
with open('sound_operators.txt', 'w') as file:
    file.write('\n'.join(sorted(unique_operators)))
print(f"Found {len(unique_operators)} sound operators in", time_since(program_start))