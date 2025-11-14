from pathlib import Path
from typing import List


class Config:
    SERVICES_FILE_MAPPING: Path = Path(__file__).parent / "services.json"
    SAFE_MODE: List[str] = ["can_", "check_", "checkout_", "claim_", "compare_", "contains_", "decode_", "decrypt_", "derive_", "describe_", "detect_", "discover_", "download_", "estimate_", "evaluate_", "export_", "filter_", "get_", "group_", "head_", "import_", "is_", "list_", "poll_", "predict_", "query_", "re_", "read_", "receive_", "refresh_", "resolve_", "restore_", "retrieve_", "return_", "sample_", "scan_", "search_", "select_", "synthesize_", "validate_", "verify_", "view_"]
