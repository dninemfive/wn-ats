from typing import Iterable, Self
from type_profile.ndf_types.TScannerConfigurationDescriptor import TScannerConfigurationDescriptor as Scanner
from type_profile.ndf_types.TReverseScannerWithIdentificationDescriptor import TReverseScannerWithIdentificationDescriptor as ReverseScanner
from type_profile.ndf_types.TModernWarfareVisibilityRollRule import TModernWarfareVisibilityRollRule as VisibilityRollRule
from type_profile.ndf_types.TModernWarfareDistanceMultiplierRollRuleDescriptor import TModernWarfareDistanceMultiplierRollRuleDescriptor as DistanceMultiplier

from ndf_parse import Mod
from ndf_parse.model import List, Map, Object

SCANNER_ATTRS: dict[str, type] = {
        'PorteeVisionTBAGRU':       float,
        'DetectionTBAGRU':          float,
        'PorteeVisionGRU':          float,
        'PorteeIdentification':     float,
        'OpticalStrength':          float,
        'OpticsAltitudeConfig':     str,
        'OpticalStrengthAltitude':  int
    }

def kvps(map: Map) -> Iterable[tuple[str, float]]:
    for row in map:
        yield (row.key, float(row.value))

def frozen_ordered_kvps(map: Map) -> tuple[tuple[str, float]]:
    return tuple(sorted(kvps(map), key=lambda x: x[0]))

def to_scanner(object: Object) -> Scanner:
    """    
    PorteeVisionTBAGRU: float | int
    DetectionTBAGRU: float | int
    PorteeVisionGRU: float | int
    PorteeIdentification: float | int
    OpticalStrength: float | int
    OpticsAltitudeConfig: str
    PorteeVisionFOWGRU: float
    OpticalStrengthAltitude: int
    SpecializedDetectionsGRU: Map[MapRow[float]]
    SpecializedOpticalStrengths: Map[MapRow[float]]
    """
    result = Scanner()
    for attr, type in SCANNER_ATTRS:
        setattr(result, attr, type(object.by_member(attr).value))
    result.SpecializedDetectionsGRU = frozen_ordered_kvps(object.by_member('SpecializedDetectionsGRU').value)
    result.SpecializedOpticalStrengths = frozen_ordered_kvps(object.by_member('SpecializedOpticalStrengths').value)

VISIBILITY_ROLL_RULE_ATTRS: dict[str, type] = {
    'VisibilityRuleDescriptor': str,    
    'IdentifyBaseProbability': float,
    'TimeBetweenEachIdentifyRoll': float
}
DISTANCE_MULTIPLIER_ATTRS: dict[str, type] = {
    "MultiplicateurAPorteeMaximale": str,
    'MultiplicateurAPorteeMinimale': str,
    'Exposant': str,
    'MultiplicateurAPorteeMaximaleEnMouvement': str,
    'MultiplicateurAPorteeMinimaleEnMouvement': str,
    'ExposantEnMouvement': str
}

def to_reverse_scanner(object: Object) -> ReverseScanner:
    result = ReverseScanner()
    result.VisibilityRollRule = VisibilityRollRule()
    visibility: Object = object.by_member('VisibilityRollRule').value
    for attr, type in VISIBILITY_ROLL_RULE_ATTRS:
        setattr(result.VisibilityRollRule, attr, type(visibility.by_member(attr).value))
    result.VisibilityRollRule.DistanceMultiplierRule = DistanceMultiplier()
    distance: Object = visibility.by_member('DistanceMultiplierRule').value
    for attr, type in DISTANCE_MULTIPLIER_ATTRS:
        setattr(result.VisibilityRollRule.DistanceMultiplierRule, attr, type(distance.by_member(attr).value))

def get_scanners(unit: Object) -> tuple[Scanner, ReverseScanner]:
    modules: List = unit.by_member('ModulesDescriptors').value
    return (
        to_scanner(modules.find_by_cond(lambda x: x.value.type == 'TScannerConfigurationDescriptor')),
        to_reverse_scanner(modules.find_by_cond(lambda x: x.value.type == 'TReverseScannerWithIdentificationDescriptor'))
    )

MOD_PATH = rf'C:\Program Files (x86)\Steam\steamapps\common\WARNO\Mods\default'

mod = Mod(MOD_PATH, MOD_PATH)

FOLDER = 'UniteDescriptor/vision'

with mod.edit('GameData/Generated/Gameplay/Gfx/UniteDescriptor.ndf') as file:
    for row in file:
        print(repr(get_scanners(row.value)))
        break