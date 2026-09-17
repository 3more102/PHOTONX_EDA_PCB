from dataclasses import dataclass
@dataclass(frozen=True)
class LibraryEntry: name:str; aliases:tuple[str,...]=(); notes:str=''
DEFAULT_LIBRARY={x.name:x for x in [LibraryEntry('TWO_PIN_THT',('R_Axial','LED_THT','Connector_2Pin')),LibraryEntry('TWO_PAD_SMD',('R_SMD','C_SMD','LED_SMD')),LibraryEntry('SOIC8_LIKE',('SOIC-8',)),LibraryEntry('DIP8_LIKE',('DIP-8',))]}
