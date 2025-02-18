import argparse
import re

def druid_to_promql(druid_query: str) -> str:
    """Converts a Druid SQL query into a PromQL query."""
    # Extract metric name
    metric_match = re.search(r'SELECT\s+([\w*\s,]+)\s+FROM\s+(\w+)', druid_query, re.IGNORECASE)
    if metric_match:
        metrics, table = metric_match.groups()
        metrics = [m.strip() for m in metrics.split(',')]
    else:
        return "Invalid query format"
    
    # Handle basic aggregation functions
    aggregations = {}
    for metric in metrics:
        agg_match = re.search(r'(SUM|AVG|MAX|MIN|COUNT)\((\w+)\)', metric, re.IGNORECASE)
        if agg_match:
            agg_function, metric_name = agg_match.groups()
            aggregations[metric_name] = agg_function.lower()
        else:
            aggregations[metric] = ""
    
    # Extract filters (WHERE clause)
    where_clause = re.search(r'WHERE\s+(.+)', druid_query, re.IGNORECASE)
    filters = ""
    if where_clause:
        conditions = where_clause.group(1)
        conditions = re.sub(r'=', r'==', conditions)  # Convert SQL '=' to PromQL '=='
        conditions = re.sub(r'AND', r',', conditions, flags=re.IGNORECASE)  # Convert AND to ,
        filters = f'{{{conditions}}}'
    
    # Handle GROUP BY time bucket
    group_by_match = re.search(r'GROUP BY\s+TIME_FLOOR\(([^,]+),\s*INTERVAL\s+([^)]+)\)', druid_query, re.IGNORECASE)
    interval = ""
    if group_by_match:
        time_column, interval = group_by_match.groups()
    
    # Construct PromQL queries for multiple metrics
    promql_queries = []
    for metric_name, agg_function in aggregations.items():
        promql_agg = f"{agg_function}_over_time" if agg_function else ""
        promql_query = f'{promql_agg}({metric_name}{filters}[{interval}])' if interval else f'{promql_agg}({metric_name}{filters})'
        promql_queries.append(promql_query)
    
    return "\n".join(promql_queries)

def main():
    parser = argparse.ArgumentParser(description="Convert Druid SQL queries to PromQL queries.")
    parser.add_argument("query", type=str, help="Druid SQL query to convert.")
    args = parser.parse_args()
    
    promql_query = druid_to_promql(args.query)
    print("Converted PromQL Query:")
    print(promql_query)

if __name__ == "__main__":
    main()
