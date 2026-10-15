import argparse
import csv
import hashlib
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "transactions": "Transaction_ID Booking_ID Transaction_Date Route_ID Transaction_Type Membership_Tier Booking_Channel Payment_Method Amount".split(),
    "costs": "Cost_ID Cost_Date Cost_Type Route_ID From To Amount".split(),
    "gates": "City Gate_Number Route_ID Year Annual_Gate_Cost".split(),
}
AIRPORTS = dict(
    zip(
        "YVR YYC YYZ YUL YYJ YLW YXX YXS YEG YXE YQR YWG YOW YXU YQB YHZ YQM YYT YXY YZF".split(),
        [
            "Vancouver",
            "Calgary",
            "Toronto",
            "Montreal",
            "Victoria",
            "Kelowna",
            "Abbotsford",
            "Prince George",
            "Edmonton",
            "Saskatoon",
            "Regina",
            "Winnipeg",
            "Ottawa",
            "London",
            "Quebec City",
            "Halifax",
            "Moncton",
            "St. John's",
            "Whitehorse",
            "Yellowknife",
        ],
    )
)
LABELS = {
    "transaction_type": [
        "Ticket",
        "Extra Baggage",
        "Seat Upgrade",
        "Change Fee",
        "Food & Onboard",
        "Refund",
    ],
    "membership_tier": ["Non-Member", "Blue", "Silver", "Gold", "Platinum"],
    "booking_channel": [
        "Direct Web",
        "Corporate Portal",
        "Online Travel Agency",
        "Mobile App",
    ],
    "payment_method": ["Credit Card", "Points + Cash", "Debit", "Travel Voucher"],
    "cost_type": ["Fuel", "Crew", "Maintenance", "Food"],
}
ALIASES = {
    "website": "Direct Web",
    "web": "Direct Web",
    "corp portal": "Corporate Portal",
    "corporate": "Corporate Portal",
    "online travel agcy": "Online Travel Agency",
    "ota": "Online Travel Agency",
    "app": "Mobile App",
    "mobile": "Mobile App",
}
MISSING = {"", "n/a", "none", "unknown"}


def parse_date(value):
    """Return valid interpretations for duplicate matching before date assumptions."""
    formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M"]
    if re.match(r"^\d{2}/\d{2}/\d{4} ", value):
        formats = ["%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"]
    candidates = set()
    for fmt in formats:
        try:
            candidates.add(datetime.strptime(value, fmt).isoformat(sep=" "))
        except ValueError:
            pass
    return candidates


def normalize_row(name, source):
    row = {k.lower(): source[k].strip() for k in SCHEMAS[name]}
    for key in row:
        if key in LABELS:
            value = row[key].casefold()
            if value in MISSING and key in {"membership_tier", "payment_method"}:
                row[key] = ""
            else:
                choices = {s.casefold(): s for s in LABELS[key]}
                if key == "booking_channel":
                    choices.update(ALIASES)
                if value not in choices:
                    raise ValueError(f"Unknown {key}: {row[key]!r}")
                row[key] = choices[value]
        elif not row[key] and not (name == "gates" and key == "route_id"):
            raise ValueError(f"Missing required field {key}")

    route = re.sub(r"[-\s]", "", row["route_id"]).upper()
    if route and (
        len(route) != 6 or route[:3] not in AIRPORTS or route[3:] not in AIRPORTS
    ):
        raise ValueError(f"Invalid route: {row['route_id']!r}")
    row["route_id"] = route
    row["departure_airport"] = route[:3]
    row["arrival_airport"] = route[3:]
    money_key = "annual_gate_cost" if name == "gates" else "amount"
    try:
        amount = Decimal(row[money_key])
        if not amount.is_finite() or amount != amount.quantize(Decimal("0.01")):
            raise ValueError(f"Invalid CAD amount: {row[money_key]!r}")
        row[money_key] = f"{amount:.2f}"
    except InvalidOperation as exc:
        raise ValueError(f"Invalid CAD amount: {row[money_key]!r}") from exc
    if name == "transactions":
        if (row["transaction_type"] == "Refund" and amount >= 0) or (
            row["transaction_type"] != "Refund" and amount < 0
        ):
            raise ValueError("Unexpected transaction amount sign")
    elif amount < 0:
        raise ValueError("Negative operating or gate cost")
    if name == "costs" and (
        row["from"] != AIRPORTS[route[:3]] or row["to"] != AIRPORTS[route[3:]]
    ):
        raise ValueError("Route and departure/arrival cities disagree")
    if name == "gates":
        if row["city"] not in AIRPORTS.values() or (
            route and row["city"] != AIRPORTS[route[:3]]
        ):
            raise ValueError("Gate city and departure airport disagree")
        row["departure_airport"] = next(
            k for k, v in AIRPORTS.items() if v == row["city"]
        )
        if row["year"] not in {"2024-2025", "2025-2026"}:
            raise ValueError(f"Unexpected lease year: {row['year']}")
        row["lease_start"] = row["year"][:4] + "-01-01"
        row["lease_end"] = row["year"][5:] + "-01-01"
    return row


def clean_records(name, source_rows):
    """Clean one table; collapse agreeing IDs and fail on conflicting duplicates."""
    stats = Counter(input_rows=0, blank_rows_removed=0, duplicate_rows_removed=0)
    records = {}
    input_total = Decimal(0)
    date_key = {"transactions": "transaction_date", "costs": "cost_date"}.get(name)
    money_key = "annual_gate_cost" if name == "gates" else "amount"
    for line, source in enumerate(source_rows, 2):
        stats["input_rows"] += 1
        if not any(v and v.strip() for v in source.values()):
            stats["blank_rows_removed"] += 1
            continue
        try:
            if any(
                v and v.strip() for k, v in source.items() if k not in SCHEMAS[name]
            ):
                raise ValueError("Unexpected populated column")
            row = normalize_row(name, source)
            input_total += Decimal(row[money_key])
            candidates = parse_date(row[date_key]) if date_key else set()
            if date_key:
                row[date_key + "_raw"] = row.pop(date_key)
                if not candidates:
                    raise ValueError(f"Invalid date: {row[date_key + '_raw']!r}")
            key = (
                (row["city"], row["gate_number"], row["year"], row["route_id"])
                if name == "gates"
                else row["transaction_id" if name == "transactions" else "cost_id"]
            )
            if key in records:
                previous, previous_dates, had_ambiguity = records[key]
                comparable = lambda r: {
                    k: v
                    for k, v in r.items()
                    if k != (date_key + "_raw" if date_key else "")
                }
                intersection = previous_dates & candidates
                if comparable(row) != comparable(previous) or (
                    date_key and not intersection
                ):
                    raise ValueError(f"Conflicting duplicate {key}")
                records[key] = (
                    previous,
                    intersection,
                    had_ambiguity or len(candidates) > 1,
                )
                stats["duplicate_rows_removed"] += 1
            else:
                records[key] = (row, candidates, len(candidates) > 1)
        except (ValueError, KeyError, AttributeError) as exc:
            raise ValueError(f"{name}, CSV row {line}: {exc}") from exc

    result = []
    for row, candidates, had_ambiguity in records.values():
        if date_key:
            if len(candidates) > 1:
                row[date_key] = datetime.strptime(
                    row[date_key + "_raw"], "%d/%m/%Y %H:%M"
                ).isoformat(sep=" ")
                row["date_status"] = "assumed_day_first"
            else:
                row[date_key] = next(iter(candidates))
                row["date_status"] = "resolved_duplicate" if had_ambiguity else "parsed"
        result.append(row)
    stats["output_rows"] = len(result)
    stats["input_amount_total"] = f"{input_total:.2f}"
    output_total = sum((Decimal(r[money_key]) for r in result), Decimal(0))
    stats["output_amount_total"] = f"{output_total:.2f}"
    stats["duplicate_amount_removed"] = f"{input_total - output_total:.2f}"
    stats["missing_values"] = (
        {k: sum(r[k] == "" for r in result) for k in result[0]} if result else {}
    )
    if date_key:
        stats["date_status"] = dict(Counter(r["date_status"] for r in result))
        dates = [r[date_key] for r in result if r[date_key]]
        stats["resolved_date_range"] = [min(dates), max(dates)] if dates else []
    return result, dict(stats)


def gate_leases(rows):
    """One cost per airport/gate/lease year, including gates without routes."""
    leases = {}
    routes = {}
    for row in rows:
        key = (row["city"], row["gate_number"], row["year"])
        if key in leases and leases[key]["annual_gate_cost"] != row["annual_gate_cost"]:
            raise ValueError(f"Conflicting annual gate costs: {key}")
        leases[key] = {
            k: v for k, v in row.items() if k not in {"route_id", "arrival_airport"}
        }
        routes.setdefault(key, set())
        if row["route_id"]:
            routes[key].add(row["route_id"])
    return [
        row | {"assigned_route_count": len(routes[key])}
        for key, row in sorted(leases.items())
    ]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def prepare_data(raw_dir):
    """Return cleaned tables and quality checks without writing any files."""
    tables, report = {}, {"sources": {}, "tables": {}}
    for name, columns in SCHEMAS.items():
        source = raw_dir / f"{name}.csv"
        with source.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if not set(columns).issubset(reader.fieldnames or []):
                raise ValueError(f"Missing required columns in {source}")
            tables[name], report["tables"][name] = clean_records(name, reader)
        report["sources"][name] = {
            "file": source.name,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        }
    route_sets = {
        k: {r["route_id"] for r in rows if r["route_id"]} for k, rows in tables.items()
    }
    report["route_coverage"] = {
        "transactions_without_cost_route": sorted(
            route_sets["transactions"] - route_sets["costs"]
        ),
        "cost_routes_without_gate_assignment": sorted(
            route_sets["costs"] - route_sets["gates"]
        ),
    }
    leases = gate_leases(tables["gates"])
    report["gate_leases"] = {
        "rows": len(leases),
        "unassigned_gate_years": sum(r["assigned_route_count"] == 0 for r in leases),
        "annual_cost_by_lease_year": {
            year: f"{sum((Decimal(r['annual_gate_cost']) for r in leases if r['year'] == year), Decimal(0)):.2f}"
            for year in sorted({r["year"] for r in leases})
        },
    }
    tables["gate_leases"] = leases
    tables["routes"] = [
        dict(
            route_id=r,
            departure_airport=r[:3],
            arrival_airport=r[3:],
            departure_city=AIRPORTS[r[:3]],
            arrival_city=AIRPORTS[r[3:]],
        )
        for r in sorted(set.union(*route_sets.values()))
    ]
    return tables, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    args = parser.parse_args()
    if args.raw_dir.resolve() == args.output_dir.resolve():
        parser.error("Output directory must differ from the raw directory")
    tables, report = prepare_data(args.raw_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        write_csv(args.output_dir / f"{name}.csv", rows)
    for name, stats in report["tables"].items():
        print(
            f"{name}: {stats['output_rows']:,} rows; removed {stats['blank_rows_removed']:,} blank and {stats['duplicate_rows_removed']:,} duplicate rows"
        )
    print(
        f"Wrote {len(tables['gate_leases'])} gate leases and {len(tables['routes'])} routes to {args.output_dir}"
    )


if __name__ == "__main__":
    main()
