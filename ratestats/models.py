from dataclasses import dataclass


@dataclass
class Currency:
    code: str
    name: str
    exchange_rate: str
    nominal: str
    difference: str
