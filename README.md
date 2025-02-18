# Druid to PromQL Converter

This CLI tool converts **Druid SQL queries** into **Prometheus Query Language (PromQL)** queries, enabling users to transition between time-series databases more effectively.

## Features
- Converts **SELECT** queries with basic and complex aggregations.
- Translates **WHERE** conditions into PromQL filter expressions.
- Supports **GROUP BY TIME_FLOOR** conversions for PromQL time intervals.
- Handles **COUNT, SUM, AVG, MIN, MAX** functions.
- Works with multiple metrics in a single query.

## Installation

Ensure you have **Python 3.7+** installed. Clone the repository and install dependencies if needed:

```sh
# Clone the repository
git clone https://github.com/your-repo/druid-to-promql.git
cd druid-to-promql

# Install dependencies (if required)
pip install -r requirements.txt  # If a requirements file is added later
```

## Usage

Run the script with a Druid SQL query as an argument:

```sh
python druid2promql.py "SELECT SUM(cpu_usage) FROM metrics WHERE region='us-east' GROUP BY TIME_FLOOR(__time, INTERVAL '5m')"
```

### Example Queries

#### Basic Aggregation
**Druid SQL:**
```sql
SELECT SUM(cpu_usage) FROM metrics
```
**PromQL Output:**
```promql
sum(cpu_usage)
```

#### Filtering with WHERE Clause
**Druid SQL:**
```sql
SELECT AVG(memory_usage) FROM system_metrics WHERE region='us-west'
```
**PromQL Output:**
```promql
avg(memory_usage{region=='us-west'})
```

#### Time-Bucketed Aggregation
**Druid SQL:**
```sql
SELECT MAX(disk_io) FROM storage WHERE node='server-1' GROUP BY TIME_FLOOR(__time, INTERVAL '10m')
```
**PromQL Output:**
```promql
max_over_time(disk_io{node=='server-1'}[10m])
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to enhance the tool's capabilities.

## License
This project is open-source and available under the **MIT License**.

