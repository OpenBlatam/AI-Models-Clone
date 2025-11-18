"""
Query helper functions

Utility functions for building common SQLAlchemy queries.
"""

from typing import Optional
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc


def apply_ordering(
    query: Query,
    order_by: Optional[str],
    order_direction: str = "desc",
    model_class: Optional[type] = None
) -> Query:
    """
    Apply ordering to a query.
    
    Args:
        query: SQLAlchemy query
        order_by: Field name to order by
        order_direction: Order direction (asc/desc)
        model_class: Model class to get field from (optional, inferred from query if not provided)
        
    Returns:
        Query with ordering applied
    """
    if not order_by:
        return query
    
    if model_class:
        order_field = getattr(model_class, order_by, None)
    else:
        try:
            entity = query.column_descriptions[0]['entity']
            order_field = getattr(entity, order_by, None)
        except (IndexError, KeyError, AttributeError):
            return query
    
    if not order_field:
        return query
    
    if order_direction.lower() == "desc":
        return query.order_by(desc(order_field))
    else:
        return query.order_by(asc(order_field))






