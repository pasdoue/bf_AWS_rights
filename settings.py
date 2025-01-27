
from pathlib import Path

class Config:
    SERVICES_FILE_MAPPING: Path = Path(__file__).parent / "services.json"
