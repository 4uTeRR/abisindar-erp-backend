from enum import StrEnum


class ProductType(StrEnum):
    RAW_MATERIAL = "raw_material"
    FINISHED_GOOD = "finished_good"
    PACKAGING = "packaging"


class StockMovementType(StrEnum):
    PRODUCTION = "production"
    PURCHASE = "purchase"
    DELIVERY = "delivery"
    WRITE_OFF = "write_off"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
