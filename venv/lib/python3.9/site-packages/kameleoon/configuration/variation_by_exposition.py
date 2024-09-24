"""Kameleoon Configuration"""

from typing import Any, List, Dict, Optional


class VariationByExposition:
    """
    Variation is used for saving variations of feature flags (v2) with rules
    """

    @staticmethod
    def from_array(array: List[Dict[str, Any]]) -> List["VariationByExposition"]:
        """Creates a list of VariationByExposition from array of dictionaries"""
        return [VariationByExposition(item) for item in array]

    def __init__(self, dict_json: Dict[str, Any]):
        self.variation_key: str = dict_json.get("variationKey", "")
        self.variation_id: Optional[int] = dict_json.get("variationId")
        self.exposition: float = dict_json.get("exposition", 0.0)

    def __str__(self):
        return (
            f"VariationByExposition{{exposition:{self.exposition},"
            f"variation_key:'{self.variation_key}',"
            f"variation_id:{self.variation_id}}}"
        )
