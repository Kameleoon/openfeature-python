"""Kameleoon Configuration"""

from typing import Any, List, Dict, Optional
from kameleoon.configuration.rule_type import RuleType, rule_type_from_literal
from kameleoon.configuration.variation_by_exposition import VariationByExposition
from kameleoon.targeting.models import Segment


class Rule:
    """
    Rule is used for saving rule of feature flags (v2) with rules
    """

    @staticmethod
    def from_array(array: List[Dict[str, Any]]) -> List["Rule"]:
        """Create a list of Rules from the json array"""

        return [Rule(item) for item in array]

    def __init__(self, dict_json: Dict[str, Any]):
        self.id_: int = dict_json["id"]
        self.order: int = dict_json.get("order", 0)
        type_literal: str = dict_json.get("type", "")
        self.type = rule_type_from_literal(type_literal)
        self.exposition: float = dict_json.get("exposition", 0.0)
        self.experiment_id: int = dict_json.get("experimentId", 0)
        self.respool_time: Optional[int] = dict_json.get("respoolTime", None)
        self.variation_by_exposition: List[VariationByExposition] = VariationByExposition.from_array(
            dict_json.get("variationByExposition", [])
        )
        self.first_variation = self.variation_by_exposition[0] if len(self.variation_by_exposition) > 0 else None
        segment = dict_json.get("segment")
        self.targeting_segment: Optional[Segment] = Segment(segment) if segment else None
        self.segment_id: int = self.targeting_segment.id_ if self.targeting_segment else -1

    def get_variation(self, hash_double: float) -> Optional[VariationByExposition]:
        """Calculates the variation key for the given hash of visitor"""

        total = 0.0
        for var_by_exp in self.variation_by_exposition:
            total += var_by_exp.exposition
            if total >= hash_double:
                return var_by_exp
        return None

    @property
    def is_experimentation(self) -> bool:
        """Return `true` if rule is `experimentation` type"""

        return self.type == RuleType.EXPERIMENTATION

    @property
    def is_targeted_delivery(self) -> bool:
        """Return `true` if rule is `targeted delivery` type"""

        return self.type == RuleType.TARGETED_DELIVERY

    def __str__(self):
        return f"Rule{{id:{self.id_}}}"
