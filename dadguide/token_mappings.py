from enum import Enum
from collections import defaultdict

class Attribute(Enum):
    """Standard 5 PAD colors in enum form. Values correspond to DadGuide values."""
    Fire = 0
    Water = 1
    Wood = 2
    Light = 3
    Dark = 4
    Unknown = 5
    Nil = 6


COLOR_MAP = {}
COLOR_MAP.update({n: Attribute.Fire for n in ('r','red','fire')})
COLOR_MAP.update({n: Attribute.Water for n in ('b','blue','water')})
COLOR_MAP.update({n: Attribute.Wood for n in ('g','green','wood')})
COLOR_MAP.update({n: Attribute.Light for n in ('l','light','yellow','white')})
COLOR_MAP.update({n: Attribute.Dark for n in ('d','dark','purple','black')})
COLOR_MAP.update({n: Attribute.Nil for n in ('x','none','null','nil')})

COLOR_MAP = {Attribute.Fire: ('r','red','fire'),
             Attribute.Water: ('b','blue','water'),
             Attribute.Wood: ('g','green','wood'),
             Attribute.Light: ('l','light','yellow','white'),
             Attribute.Dark: ('d','dark','purple','black'),
             Attribute.Nil: ('x','none','null','nil')}

SERIES_MAP = {}
SERIES_MAP.update({n: 130 for n in ('halloween', 'hw', 'h')})
SERIES_MAP.update({n: 136 for n in ('xmas', 'christmas')})
SERIES_MAP.update({n: 125 for n in ('summer', 'beach')})
SERIES_MAP.update({n: 114 for n in ('school', 'academy', 'gakuen')})
SERIES_MAP.update({n: 139 for n in ('new years', 'ny')})
SERIES_MAP.update({n: 149 for n in ('wedding', 'bride')})
SERIES_MAP.update({n: 154 for n in ('padr')})
SERIES_MAP.update({n: 175 for n in ('valentines', 'vday', 'v')})
SERIES_MAP.update({n: 183 for n in ('gh', 'gungho')})
SERIES_MAP.update({n: 117 for n in ('ghpem', 'gunghopem')}) #FIXME

SERIES_MAP.update({n: 187 for n in ('sam3', 'samurai3', 'samiii')})

SERIES_MAP = {130: ('halloween', 'hw', 'h'),
              136: ('xmas', 'christmas'),
              125: ('summer', 'beach'),
              114: ('school', 'academy', 'gakuen'),
              139: ('new years', 'ny'),
              149: ('wedding', 'bride'),
              154: ('padr'),
              175: ('valentines', 'vday', 'v'),
              183: ('gh', 'gungho'),
              117: ('ghpem', 'gunghopem'), #FIXME
              187: ('sam3', 'samurai3', 'samiii')}


class EvoTypes(Enum):
    BASE = 'base'
    EVO = 'evolved'
    UVO = 'ulimate'
    UUVO = 'super ultimate'
    TRANS = 'transform'
    AWOKEN = 'awoken'
    MEGA = 'mega awoken'
    REVO = 'reincarnated'
    SREVO = 'super reincarnated'
    PIXEL = 'pixel'
    EQUIP = 'equip'

EVO_PREFIX_MAP = {}
EVO_PREFIX_MAP.update({n: EvoTypes.BASE for n in ('base',)})
EVO_PREFIX_MAP.update({n: EvoTypes.EVO for n in ('evo', 'evolved')})
EVO_PREFIX_MAP.update({n: EvoTypes.UVO for n in ('uvo', 'ult', 'ultimate', 'uevo')})
EVO_PREFIX_MAP.update({n: EvoTypes.UUVO for n in ('uuvo', 'uult', 'uultimate', 'uuevo')})
EVO_PREFIX_MAP.update({n: EvoTypes.TRANS for n in ('trans', 'transform', 'transformed')})
EVO_PREFIX_MAP.update({n: EvoTypes.AWOKEN for n in ('awoken', 'awo', 'a')})
EVO_PREFIX_MAP.update({n: EvoTypes.MEGA for n in ('mega', 'mawoken', 'mawo', 'ma')})
EVO_PREFIX_MAP.update({n: EvoTypes.REVO for n in ('reincarnated', 'revo')})
EVO_PREFIX_MAP.update({n: EvoTypes.SREVO for n in ('srevo', 'super', 'sr')})
EVO_PREFIX_MAP.update({n: EvoTypes.PIXEL for n in ('p', 'pixel', 'dot')})
EVO_PREFIX_MAP.update({n: EvoTypes.EQUIP for n in ('equip', 'assist')})

EVO_PREFIX_MAP = {EvoTypes.BASE: ('base',),
                  EvoTypes.EVO: ('evo', 'evolved'),
                  EvoTypes.UVO: ('uvo', 'ult', 'ultimate', 'uevo'),
                  EvoTypes.UUVO: ('uuvo', 'uult', 'uultimate', 'uuevo'),
                  EvoTypes.TRANS: ('trans', 'transform', 'transformed'),
                  EvoTypes.AWOKEN: ('awoken', 'awo', 'a'),
                  EvoTypes.MEGA: ('mega', 'mawoken', 'mawo', 'ma'),
                  EvoTypes.REVO: ('reincarnated', 'revo'),
                  EvoTypes.SREVO: ('srevo', 'super', 'sr'),
                  EvoTypes.PIXEL: ('p', 'pixel', 'dot'),
                  EvoTypes.EQUIP: ('equip', 'assist')}


class MiscPrefixes(Enum):
    CHIBI = 'chibi'
    FARMABLE = 'farmable'

MISC_PREFIX_MAP = {}
MISC_PREFIX_MAP.update({n: MiscPrefixes.CHIBI for n in ('chibi', 'mini')})
MISC_PREFIX_MAP.update({n: MiscPrefixes.FARMABLE for n in ('farmable', 'nrem')})

MISC_PREFIX_MAP = {MiscPrefixes.CHIBI: ('chibi', 'mini'),
                   MiscPrefixes.FARMABLE: ('farmable', 'nrem')}


TOKEN_REPLACEMENTS = defaultdict(tuple, {
    'tamadra': ('tama',),
    'evolution': ('evo',),
})
