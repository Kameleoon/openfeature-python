"""Targeting Segment"""

from typing import Optional
from kameleoon.exceptions import NotFoundError
from kameleoon.targeting.tree_builder import create_tree


class Segment:
    """Segment with targeting data"""

    def __init__(self, *args) -> None:
        if args:
            if len(args) == 1:
                if args[0] is None:
                    raise NotFoundError("arguments for segment")
                if "id" not in args[0]:
                    raise NotFoundError("id")
                self.id_ = int(args[0]["id"])
                if "conditionsData" not in args[0]:
                    raise NotFoundError("conditionsData")

                self.tree = create_tree(args[0]["conditionsData"])
            elif len(args) == 2:
                self.id_ = args[0]
                self.tree = args[1]

    def check_tree(self, get_targeting_data) -> Optional[bool]:
        """Checks the targeting throught targeting tree"""
        return self.tree.check(get_targeting_data) if self.tree else True
