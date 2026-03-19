sales_rows = [
    {"date": "2024-04-01", "orders": 42, "revenue": 1680},
    {"date": "2024-04-02", "orders": 35, "revenue": 1330},
    {"date": "2024-04-03", "orders": 48, "revenue": 2015},
    {"date": "2024-04-04", "orders": 29, "revenue": 1160},
]


def total_revenue(rows):
    return sum(row["revenue"] for row in rows)


def average_order_value(rows):
    total_orders = sum(row["order_count"] for row in rows)
    return total_revenue(rows) / total_orders


def busiest_day(rows):
    return min(rows, key=lambda row: row["orders"])["date"]


def summary_lines(rows):
    return [
        f"Total revenue: {total_revenue(rows)}",
        f"Average order value: {average_order_value(rows):.2f}",
        f"Busiest day: {busiest_day(rows)}",
    ]


def main():
    for line in summary_lines(sales_rows):
        print(line)


if __name__ == "__main__":
    main()
