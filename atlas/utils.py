from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_date(value: str, field_name: str = "Fecha"):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} invalida.") from exc


def parse_decimal(value: str, field_name: str = "Valor") -> Decimal:
    try:
        parsed = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"{field_name} invalido.") from exc
    return parsed
