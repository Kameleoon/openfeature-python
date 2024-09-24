"""Kameleoon Configuration"""

from typing import Any, List, Dict, Optional

from kameleoon.configuration.rule import Rule
from kameleoon.configuration.variation import Variation
from kameleoon.helpers.string_utils import StringUtils


class FeatureFlag:
    """
    FeatureFlag is used for operating feature flags with rules
    """

    @staticmethod
    def from_array(array: List[Dict[str, Any]]) -> List["FeatureFlag"]:
        """Create a list of FeatureFlags from the json array"""
        return [FeatureFlag(item) for item in array]

    def __init__(self, dict_json: Dict[str, Any]):
        self.id_: int = dict_json.get("id", 0)
        self.feature_key: str = dict_json.get("featureKey", "")
        self.default_variation_key: str = dict_json.get("defaultVariationKey", "")
        self.variations: List[Variation] = Variation.from_array(
            dict_json.get("variations", [])
        )
        self.environment_enabled = dict_json.get("environmentEnabled", False)
        self.rules: List[Rule] = Rule.from_array(dict_json.get("rules", []))

    def get_variation(self, key: str) -> Optional[Variation]:
        """Retrun a variation for the given key"""
        return next((v for v in self.variations if v.key == key), None)

    def __str__(self):
        return (
            f"FeatureFlag{{"
            f"id:{self.id_},"
            f"feature_key:'{self.feature_key}',"
            f"environment_enabled:{self.environment_enabled},"
            f"variations:{StringUtils.object_to_string(self.variations)},"
            f"default_variation_key:'{self.default_variation_key}',"
            f"rules:{len(self.rules)}"
            f"}}"
        )
