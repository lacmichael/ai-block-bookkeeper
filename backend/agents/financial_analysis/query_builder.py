# Query Builder for Financial Analysis Agent
# This module safely converts LLM intents into parameterized SQL queries to prevent SQL injection

from typing import Dict, Any, List, Tuple
import asyncpg

def build_sql_query(intent: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    Build SQL query based on parsed intent with proper parameterization.
    
    Args:
        intent: Dictionary containing parsed intent from LLM
        
    Returns:
        Tuple of (query_string, parameters) for safe execution
        
    Security Note: All user inputs are parameterized to prevent SQL injection
    """
    # Start with base query
    base_query = "SELECT * FROM business_events WHERE 1=1"
    parameters = []
    param_count = 0
    
    
    # Build WHERE conditions based on intent
    where_conditions = []
    
    # Vendor filtering
    if intent.get("vendor"):
        param_count += 1
        where_conditions.append(f"AND metadata->>'vendor_name' = ${param_count}")
        parameters.append(intent["vendor"])
    
    # Status filtering
    status = intent.get("status")
    if status == "UNPAID":
        where_conditions.append("AND processing->>'state' NOT IN ('RECONCILED', 'POSTED_ONCHAIN')")
    elif status == "FLAGGED":
        where_conditions.append("AND processing->>'state' = 'FLAGGED_FOR_REVIEW'")
    elif status == "PENDING":
        where_conditions.append("AND processing->>'state' = 'PENDING'")
    elif status == "MAPPED":
        where_conditions.append("AND processing->>'state' = 'MAPPED'")
    
    # Event kind filtering
    if intent.get("event_kind"):
        param_count += 1
        where_conditions.append(f"AND event_kind = ${param_count}")
        parameters.append(intent["event_kind"])
    
    # Currency filtering
    if intent.get("currency"):
        param_count += 1
        where_conditions.append(f"AND currency = ${param_count}")
        parameters.append(intent["currency"])
    
    # Date range filtering
    if intent.get("start_date"):
        param_count += 1
        where_conditions.append(f"AND occurred_at >= ${param_count}")
        parameters.append(intent["start_date"])
    
    if intent.get("end_date"):
        param_count += 1
        where_conditions.append(f"AND occurred_at <= ${param_count}")
        parameters.append(intent["end_date"])
    
    # Amount range filtering
    if intent.get("min_amount"):
        param_count += 1
        where_conditions.append(f"AND amount_minor >= ${param_count}")
        parameters.append(intent["min_amount"])
    
    if intent.get("max_amount"):
        param_count += 1
        where_conditions.append(f"AND amount_minor <= ${param_count}")
        parameters.append(intent["max_amount"])
    
    # Description search (case-insensitive)
    if intent.get("description_search"):
        param_count += 1
        where_conditions.append(f"AND LOWER(description) LIKE LOWER(${param_count})")
        parameters.append(f"%{intent['description_search']}%")
    
    # Build the final query
    query_parts = [base_query]
    query_parts.extend(where_conditions)
    
    # Handle aggregation
    aggregation = intent.get("aggregation")
    if aggregation == "SUM":
        # Replace SELECT * with aggregation
        query_parts[0] = "SELECT SUM(amount_minor) as total_amount, currency FROM business_events WHERE 1=1"
        # Add GROUP BY for currency if we're aggregating
        query_parts.append("GROUP BY currency")
    elif aggregation == "COUNT":
        query_parts[0] = "SELECT COUNT(*) as event_count FROM business_events WHERE 1=1"
    elif aggregation == "AVG":
        query_parts[0] = "SELECT AVG(amount_minor) as avg_amount, currency FROM business_events WHERE 1=1"
        query_parts.append("GROUP BY currency")
    
    # Add ordering
    order_by = intent.get("order_by", "occurred_at")
    order_direction = intent.get("order_direction", "DESC")
    query_parts.append(f"ORDER BY {order_by} {order_direction}")
    
    # Add limit
    limit = intent.get("limit", 100)
    if limit and limit > 0:
        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        parameters.append(min(limit, 1000))  # Cap at 1000 for safety
    
    # Join all parts
    final_query = " ".join(query_parts)
    
    return final_query, parameters

async def execute_query(db: asyncpg.Connection, query: str, parameters: List[Any] = None) -> List[Dict[str, Any]]:
    """
    Execute parameterized SQL query and return results.
    
    Args:
        db: Database connection
        query: SQL query string with parameter placeholders
        parameters: List of parameters for the query
        
    Returns:
        List of dictionaries representing query results
        
    Raises:
        asyncpg.PostgresError: If query execution fails
    """
    try:
        if parameters:
            rows = await db.fetch(query, *parameters)
        else:
            rows = await db.fetch(query)
        
        return [dict(row) for row in rows]
    except asyncpg.PostgresError as e:
        raise RuntimeError(f"Database query failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error executing query: {str(e)}")
