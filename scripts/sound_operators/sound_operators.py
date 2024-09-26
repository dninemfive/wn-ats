from collections import defaultdict
import os
from time import time_ns

from ndf_parse import Mod
from ndf_parse.model import Object

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

def time_since(start: int) -> str:
    return f'{(time_ns() - start) / 1e9:.3f}s'

program_start = time_ns()
operators: defaultdict[str, set[str]] = defaultdict(lambda: set())
with mod.edit('GameData/Generated/Gameplay/Gfx/Infanterie/GeneratedDepictionInfantry.ndf') as file:
    for row in file:
        value = row.value
        if isinstance(value, Object) and value.type == 'TemplateInfantryDepictionSquad':
            operators[value.by_member('SoundOperator').value].add(" ".join(row.namespace.split('_')[1:]))
result: list[str] = []
for k in sorted(operators.keys()):
    result.append(k)
    for item in sorted(operators[k]):
        result.append(f'\t{item}')
with open('sound_operators.txt', 'w') as file:
    file.write('\n'.join(result))
print(f"Found {len(operators)} sound operators in", time_since(program_start))