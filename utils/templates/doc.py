def docs_template(app_name):
    return """from drf_yasg import openapi

from utils.paginator import Paginator


PAGE_PARAMETER = openapi.Parameter(
    name="page",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description="Page",
    default=Paginator.DEFAULT_PAGE
)

LIMIT_PARAMETER = openapi.Parameter(
    name="limit",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    description="Page limit",
    default=Paginator.DEFAULT_PER_PAGE
)

KEYWORD_PARAMETER = openapi.Parameter(
    name="keyword",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="Keyword search",
)

ORDER_BY_PARAMETER = openapi.Parameter(
    name="order_by",
    required=False,
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description="order_by: [asc, desc]",
)
"""