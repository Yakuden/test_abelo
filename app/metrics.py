from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    "app_requests_total",
    "Total application requests",
    ["method", "endpoint", "status"],
)

PROCESS_DURATION = Histogram(
    "app_process_duration_seconds",
    "Duration of /process endpoint",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

DB_QUERY_DURATION = Histogram(
    "app_db_query_duration_seconds",
    "Duration of database queries",
    ["operation"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)
