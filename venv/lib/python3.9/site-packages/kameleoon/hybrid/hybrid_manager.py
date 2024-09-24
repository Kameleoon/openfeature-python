"""Hybrid"""
from typing import Dict, Optional
from kameleoon.data.manager.assigned_variation import AssignedVariation


class HybridManager:
    """Abstract hybrid manager"""
    def get_engine_tracking_code(self, visitor_variations: Optional[Dict[int, AssignedVariation]]) -> str:
        """Generates the engine tracking code based on the provided visitor variations."""
        raise NotImplementedError()
