import argparse
import re

def parse_druid_query(druid_query: str):
    """Parses a Druid SQL query and extracts metrics, filters, and groupings."""
    match = re.search(r'SELECT\s+(.+?)\s+FROM\s+(\w+)', druid_query, re.IGNORECASE)
    if not match:
        return None, None, None
    
    metrics_raw, table = match.groups()
    metrics = [m.strip() for m in metrics_raw.split(',') if 'TIME_FLOOR' not in m and 'AS time_bucket' not in m]
    
    where_match = re.search(r'WHERE\s+(.+?)\s+(GROUP BY|ORDER BY|$)', druid_query, re.IGNORECASE)
    filters = where_match.group(1) if where_match else ""
    
    group_by_match = re.search(r'TIME_FLOOR\(([^,]+),\s*INTERVAL\s+([^)]+)\)', druid_query, re.IGNORECASE)
    interval = group_by_match.group(2) if group_by_match else ""
    
    return metrics, filters, interval

def convert_filters_to_promql(filters: str) -> str:
    """Converts SQL-style filters to PromQL filters."""
    if not filters:
        return ""
    filters = re.sub(r'=', r'==', filters)  # Convert SQL '=' to PromQL '=='
    filters = re.sub(r'IN\s*\((.*?)\)', lambda m: "=~'" + "|".join(m.group(1).replace("'", "").split(",")) + "'", filters, flags=re.IGNORECASE)  # Convert IN to regex
    filters = re.sub(r'AND', r',', filters, flags=re.IGNORECASE)  # Convert AND to ,
    filters = re.sub(r'__time\s*[><=]+\s*CURRENT_TIMESTAMP[^,}]*', '', filters, flags=re.IGNORECASE)  # Remove time-based filters
    filters = filters.strip().strip(',')  # Remove leading/trailing commas
    return f'{{{filters}}}' if filters.strip() else ""

def convert_metrics_to_promql(metrics: list, filters: str, interval: str) -> str:
    """Converts Druid SQL metrics to PromQL queries."""
    promql_queries = []
    for metric in metrics:
        agg_match = re.search(r'(SUM|AVG|MAX|MIN|COUNT)\((\w+)\)\s+AS\s+(\w+)', metric, re.IGNORECASE)
        if agg_match:
            agg_function, metric_name, alias = agg_match.groups()
            promql_agg = f"{agg_function.lower()}_over_time"
            promql_query = f'{alias}: {promql_agg}({metric_name}{filters}[{interval}])'
        else:
            raw_metric = metric.split(' AS ')[-1].strip()
            promql_query = f'{raw_metric}: {raw_metric}{filters}'
        promql_queries.append(promql_query)
    return "\n".join(promql_queries)

def druid_to_promql(druid_query: str) -> str:
    """Main function to convert a Druid SQL query to PromQL."""
    metrics, filters, interval = parse_druid_query(druid_query)
    if not metrics:
        return "Invalid query format"
    
    promql_filters = convert_filters_to_promql(filters)
    return convert_metrics_to_promql(metrics, promql_filters, interval)

def main():
    parser = argparse.ArgumentParser(description="Convert Druid SQL queries to PromQL queries.")
    parser.add_argument("query", type=str, help="Druid SQL query to convert.")
    args = parser.parse_args()
    
    promql_query = druid_to_promql(args.query)
    print("Converted PromQL Query:")
    print(promql_query)

if __name__ == "__main__":
    main()
