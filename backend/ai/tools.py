"""Claude tool definitions for database queries and chart generation."""

TOOLS = [
    {
        "name": "query_database",
        "description": "Execute a read-only SQL SELECT query against the mine database. Use this to look up reports, gas readings, production data, hazards, incidents, and any other mine data. Always use get_schema_info first if you're unsure about table structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "A SQL SELECT query. Must be read-only (no INSERT/UPDATE/DELETE). Use JOINs with the reports table to connect sub-reports with dates and locations.",
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Maximum rows to return (default 100, max 500)",
                    "default": 100,
                },
            },
            "required": ["sql"],
        },
    },
    {
        "name": "generate_chart",
        "description": "Generate a chart from data. Provide the data and chart configuration. Returns a base64-encoded PNG image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["line", "bar", "scatter", "pie"],
                    "description": "Type of chart to generate",
                },
                "title": {
                    "type": "string",
                    "description": "Chart title",
                },
                "x_label": {
                    "type": "string",
                    "description": "X-axis label",
                },
                "y_label": {
                    "type": "string",
                    "description": "Y-axis label",
                },
                "data": {
                    "type": "object",
                    "description": "Chart data with 'labels' (list of x-values) and 'datasets' (list of {label, values} objects)",
                    "properties": {
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "datasets": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "label": {"type": "string"},
                                    "values": {"type": "array", "items": {"type": "number"}},
                                },
                                "required": ["label", "values"],
                            },
                        },
                    },
                    "required": ["labels", "datasets"],
                },
            },
            "required": ["chart_type", "title", "data"],
        },
    },
    {
        "name": "get_schema_info",
        "description": "Get database schema information. Call with no table_name to list all tables, or with a table_name to see its columns and types.",
        "input_schema": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Optional table name to get column details for. Omit to list all tables.",
                },
            },
        },
    },
    {
        "name": "get_recent_reports_summary",
        "description": "Get a quick summary of recent reports in the database. Useful for understanding what data is available before writing specific queries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look back (default 7)",
                    "default": 7,
                },
            },
        },
    },
]
