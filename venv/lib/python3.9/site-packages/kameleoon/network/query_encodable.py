"""Network"""


class QueryEncodable:
    """Abstract query encodable type"""
    def encode_query(self) -> str:
        """Converts the object into a query string format."""
        raise NotImplementedError
