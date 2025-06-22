from typing import TypedDict, Optional


class PaginationQuery(TypedDict):
    p_page: Optional[int] = 0
    p_limit: Optional[int] = 50
    p_order: Optional[str] = "DESC"
