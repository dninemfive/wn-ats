# get capacites
#   TModuleSelector where Default.type = TCapaciteModuleDescriptor
# get specialties
#   SpecialtiesList on TUnitUIModuleDescriptor
# find correlations between each of these and sort by P(C|S)
from collections import defaultdict
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

def try_get_capacites(module: Object) -> set[str] | None:
    result: set[str] = set()
    if module.type != 'TModuleSelector':
        return None
    try:
        default: Object = module.by_member('Default').value
        if default.type != 'TCapaciteModuleDescriptor':
            return None
        default_skill_list: List = default.by_member('DefaultSkillList').value
        for skill_row in default_skill_list:
            value: str = skill_row.value
            result.add(value.replace('$/GFX/EffectCapacity/Capacite_', ''))
        return result
    except:
        return None
    
def try_get_specialties(module: Object) -> set[str] | None:
    result: set[str] = set()
    if module.type != 'TUnitUIModuleDescriptor':
        return None
    specialties: List = module.by_member('SpecialtiesList').value
    for specialty in specialties:
        value: str = specialty.value
        if not value.startswith("'_"):
            continue
        result.add(specialty.value.replace("'", '')[1:])
    return result

class UnitTraitSummary(object):
    def __init__(self: Self, name: str, capacites: Iterable[str], specialties: Iterable[str]):
        self.name = name
        self.capacites = capacites
        self.specialties = specialties

    @staticmethod
    def from_row(unit_row: ListRow) -> Self | None:
        unit: Object = unit_row.value
        modules: List = unit.by_member('ModulesDescriptors').value
        capacites: set[str] = set()
        specialties: set[str] = set()
        for module_row in modules:
            module = module_row.value
            if not isinstance(module, Object):
                continue
            # dog's bollocks operator is so deranged
            if (val := try_get_capacites(module)) is not None:
                capacites = val
            if (val := try_get_specialties(module)) is not None:
                specialties = val
        if not any(capacites):
            return None
        return UnitTraitSummary(unit.by_member('ClassNameForDebug').value, capacites, specialties)
    
    def __str__(self: Self) -> str:
        return f'{self.name} {self.capacites} {self.specialties}'

unit_data: list[UnitTraitSummary] = []

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for unit in file:
        unit_summary = UnitTraitSummary.from_row(unit)
        if unit_summary is not None:
            unit_data.append(UnitTraitSummary.from_row(unit))

count_unit_with_specialty: defaultdict[str, int] = defaultdict(lambda: 0)
unique_capacites: set[str] = set()
count_unit_with_specialty_and_capacite: defaultdict[tuple[str, str], int] = defaultdict(lambda: 0)
for unit in unit_data:
    for specialty in unit.specialties:
        count_unit_with_specialty[specialty] += 1
        for capacite in unit.capacites:
            unique_capacites.add(capacite)
            count_unit_with_specialty_and_capacite[(specialty, capacite)] += 1
unique_capacites: list[str] = sorted(unique_capacites)

def title_row() -> Iterable[str]:
    yield ''
    yield from unique_capacites

def row(specialty: str) -> Iterable[str]:
    yield specialty
    for capacite in unique_capacites:
        yield f'{count_unit_with_specialty_and_capacite[(specialty, capacite)] / count_unit_with_specialty[specialty]}'

def rows() -> Iterable[str]:
    yield '\t'.join(title_row())
    for specialty in sorted(count_unit_with_specialty.keys()):
        yield '\t'.join(row(specialty))

with open(os.path.join(FOLDER, f'trait_correlations.tsv.data'), 'w') as file:
    file.write('\n'.join(rows()))