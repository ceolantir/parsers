from dataclasses import dataclass


@dataclass
class CourtCase:
    case_number: str
    parties: str
    status: str
    judge: str
    article: str
    case_category: str
    cases: str
