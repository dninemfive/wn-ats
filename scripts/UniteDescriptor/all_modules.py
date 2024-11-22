# get capacites
#   TModuleSelector where Default.type = TCapaciteModuleDescriptor
# get specialties
#   SpecialtiesList on TUnitUIModuleDescriptor
# find correlations between each of these and sort by P(C|S)
from collections import defaultdict
from dataclasses import dataclass
from enum import member, unique
import os
from time import time_ns
from typing import Any, Callable, Iterable, Literal, Self

from ndf_parse import Mod
from ndf_parse.model import List, ListRow, Object, Template

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'
GENERATED_PATH = MOD_PATH # rf'{MOD_PATH}\GameData\Generated'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'UniteDescriptor'

class Module(object):
    def __init__(self: Self, row: ListRow):
        self.name = row.namespace
        self.type = None
        self.default_type = None
        if isinstance(row.value, Object):
            self.type = row.value.type
            if row.value.type == 'TModuleSelector':
                default = row.value.by_member('Default').value
                print(default.__class__.__name__)
                try:
                    self.default_type == default.type
                except:
                    pass
    
    @property
    def ignore(self: Self) -> bool:
        return self.type is None and self.default_type is None
    
    def __str__(self: Self) -> str:
        return '\t'.join([str(self.type),
                          '=NA()' if self.name           is None else self.name,
                          '=NA()' if self.default_type   is None else self.default_type])

    def __lt__(self: Self, other: Self):
        return str(self) < str(other)
    
    def __eq__(self: Self, other: Self):
        return str(self) == str(other)
    
    def __hash__(self: Self):
        return hash(str(self))

module_data: set[Module] = set()

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for unit in file:
        modules: List = unit.value.by_member('ModulesDescriptors').value
        for module_row in modules:
            module = Module(module_row)
            if not module.ignore:
                module_data.add(module)

with open(os.path.join(FOLDER, 'all_modules.tsv.data'), 'w') as file:
    file.write('\n'.join(str(x) for x in sorted(module_data)))