"""Targeting Tree"""
from typing import Optional

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.tree_condition_factory import TreeConditionFactory

__all__ = ["Tree", "create_tree"]


class Tree:
    """Targeting tree for checking visitors for targeting"""

    def __init__(self, or_operator=None, left_child=None, right_child=None, condition=None) -> None:
        self.or_operator = or_operator
        self.left_child = left_child
        self.right_child = right_child
        self.condition = condition

    # pylint: disable=R0912
    def check(self, get_targeting_data) -> bool:
        """Check targeting data on targeting tree"""
        if self.condition is not None:
            is_targeted = self._check_condition(get_targeting_data)
        else:
            if self.left_child is None:
                is_left_child_targeted: Optional[bool] = True
            else:
                is_left_child_targeted = self.left_child.check(get_targeting_data)

            if is_left_child_targeted is None:
                has_to_compute_right_child = True
            else:
                has_to_compute_right_child = is_left_child_targeted is not self.or_operator

            # Compute right child tree
            is_right_child_targeted: Optional[bool] = None
            if has_to_compute_right_child:
                if self.right_child is None:
                    is_right_child_targeted = True
                else:
                    is_right_child_targeted = self.right_child.check(get_targeting_data)

            # Computing results
            if is_left_child_targeted is None:
                if is_right_child_targeted == self.or_operator:
                    is_targeted = self.or_operator
                else:
                    is_targeted = None
            else:
                if is_left_child_targeted == self.or_operator:
                    is_targeted = self.or_operator
                else:
                    if is_right_child_targeted is True:
                        is_targeted = True
                    elif is_right_child_targeted is False:
                        is_targeted = False
                    else:
                        is_targeted = None
        return is_targeted if is_targeted is not None else True

    def _check_condition(self, get_targeting_data) -> bool:
        is_targeted = self.condition.check(get_targeting_data(self.condition.type))

        if not self.condition.include:
            return not is_targeted
        return is_targeted


def _create_second_level(conditions_data_json) -> Optional[Tree]:
    if conditions_data_json is not None and conditions_data_json["conditions"]:
        left_child = Tree()
        left_child.condition = TreeConditionFactory.get_condition(conditions_data_json["conditions"].pop(0))

        if "conditions" in conditions_data_json and conditions_data_json["conditions"]:
            or_operator = conditions_data_json["orOperators"].pop(0)
            if or_operator:
                return Tree(or_operator, left_child, _create_second_level(conditions_data_json))

            right_child = Tree()
            if conditions_data_json["conditions"]:
                right_child.condition = TreeConditionFactory.get_condition(conditions_data_json["conditions"].pop(0))
            tree = Tree(or_operator, left_child, right_child)
            if conditions_data_json["conditions"]:
                return Tree(
                    conditions_data_json["orOperators"].pop(0),
                    tree,
                    _create_second_level(conditions_data_json),
                )
            return tree
        return left_child
    return None


def _create_first_level(conditions_data_json) -> Optional[Tree]:
    if conditions_data_json["firstLevel"]:
        left_first_level = conditions_data_json["firstLevel"].pop(0)
        left_child = _create_second_level(left_first_level)
        if conditions_data_json["firstLevel"]:
            or_operator = None
            if conditions_data_json["firstLevelOrOperators"]:
                or_operator = conditions_data_json["firstLevelOrOperators"].pop(0)
            if or_operator:
                return Tree(or_operator, left_child, _create_first_level(conditions_data_json))

            right_first_level = conditions_data_json["firstLevel"].pop(0)
            right_child = _create_second_level(right_first_level)
            tree = Tree(or_operator, left_child, right_child)

            if conditions_data_json["firstLevel"]:
                first_level_or_operators = None
                if conditions_data_json["firstLevelOrOperators"]:
                    first_level_or_operators = conditions_data_json["firstLevelOrOperators"].pop(0)
                return Tree(
                    first_level_or_operators,
                    tree,
                    _create_first_level(conditions_data_json),
                )
            return tree
        return left_child
    return None


def create_tree(conditions_data_json) -> Optional[Tree]:
    """Create a targeting tree from json"""
    if conditions_data_json is None:
        return None
    KameleoonLogger.debug('CALL: TreeBuilder.create_tree(conditions_data_json: %s)',
                          conditions_data_json)
    if not conditions_data_json["firstLevel"]:
        conditions_data_json["firstLevelOrOperators"] = []
    tree = _create_first_level(conditions_data_json)
    KameleoonLogger.debug('RETURN: TreeBuilder.create_tree(conditions_data_json: %s) -> (tree)',
                          conditions_data_json)
    return tree
