from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def dia_de_referencia(agora: datetime | None = None) -> str:
    agora = agora or datetime.now(timezone.utc)
    return (agora.astimezone(FUSO).date() - timedelta(days=1)).isoformat()
