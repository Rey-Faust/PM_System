#!/usr/bin/env python3
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "pmo_master_control.csv"

STATUS_RANK = {"green": 0, "yellow": 1, "red": 2}
RANK_TO_STATUS = {0: "Green", 1: "Yellow", 2: "Red"}

MODULE_SPECS = {
    "scope_status": ("scope_definition.csv", "scope_status", None),
    "schedule_status": ("weekly_progress.csv", "schedule_status", None),
    "cost_status": ("cost_tracking.csv", "cost_status", None),
    "procurement_status": ("procurement_tracking.csv", "procurement_status", None),
    "resource_status": ("resource_allocation.csv", "resource_status", None),
    "risk_status": ("risk_issue_log.csv", "risk_status", "status"),
    "collection_status": ("collection_tracking.csv", "collection_status", None),
}


def normalize_status(value: str) -> str:
    if value is None:
        return ""
    val = value.strip().lower()
    if val in STATUS_RANK:
        return val
    if val in {"g", "ok", "normal"}:
        return "green"
    if val in {"y", "risk", "warning"}:
        return "yellow"
    if val in {"r", "critical", "delay"}:
        return "red"
    return ""


def load_csv_rows(file_name: str):
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        return []
    with file_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def collect_subprojects() -> set:
    subprojects = set()
    for file_name in [
        "subproject_registry.csv",
        "scope_definition.csv",
        "weekly_progress.csv",
        "cost_tracking.csv",
        "procurement_tracking.csv",
        "resource_allocation.csv",
        "risk_issue_log.csv",
        "interface_register.csv",
        "collection_tracking.csv",
    ]:
        for row in load_csv_rows(file_name):
            subproject = (row.get("subproject") or "").strip()
            if subproject:
                subprojects.add(subproject)
    return subprojects


def latest_date_string(*values):
    parsed = []
    for value in values:
        value = (value or "").strip()
        if not value:
            continue
        try:
            parsed.append(datetime.strptime(value, "%Y-%m-%d"))
        except ValueError:
            continue
    if parsed:
        return max(parsed).strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


def module_status_for_subproject(subproject: str, file_name: str, status_field: str, close_field: str):
    rows = load_csv_rows(file_name)
    worst = 0
    last_updated_candidates = []
    matched_row_count = 0

    for row in rows:
        if (row.get("subproject") or "").strip() != subproject:
            continue

        matched_row_count += 1

        if close_field:
            close_val = (row.get(close_field) or "").strip().lower()
            if close_val in {"closed", "done", "resolved"}:
                continue

        status = normalize_status(row.get(status_field) or "")
        if status:
            worst = max(worst, STATUS_RANK[status])
        last_updated_candidates.append(row.get("last_updated") or "")

    # Missing module data should not appear as Green; mark it as Yellow for follow-up.
    if matched_row_count == 0:
        return "Yellow", datetime.now().strftime("%Y-%m-%d")

    return RANK_TO_STATUS[worst], latest_date_string(*last_updated_candidates)


def owner_lookup():
    owners = {}
    for row in load_csv_rows("subproject_registry.csv"):
        subproject = (row.get("subproject") or "").strip()
        owner = (row.get("owner") or "").strip()
        if subproject and owner:
            owners[subproject] = owner
    return owners


def current_redline(schedule_status: str, cost_status: str, collection_status: str) -> str:
    redlines = []
    if schedule_status == "Red":
        redlines.append("Schedule")
    if cost_status == "Red":
        redlines.append("Profit")
    if collection_status == "Red":
        redlines.append("Collection")
    return "; ".join(redlines) if redlines else "None"


def build():
    subprojects = sorted(collect_subprojects())
    owners = owner_lookup()

    output_rows = []
    for subproject in subprojects:
        module_values = {}
        last_updated_values = []

        for module_name, spec in MODULE_SPECS.items():
            file_name, status_field, close_field = spec
            module_status, module_date = module_status_for_subproject(
                subproject, file_name, status_field, close_field
            )
            module_values[module_name] = module_status
            last_updated_values.append(module_date)

        output_rows.append(
            {
                "subproject": subproject,
                "scope_status": module_values["scope_status"],
                "schedule_status": module_values["schedule_status"],
                "cost_status": module_values["cost_status"],
                "procurement_status": module_values["procurement_status"],
                "resource_status": module_values["resource_status"],
                "risk_status": module_values["risk_status"],
                "collection_status": module_values["collection_status"],
                "current_redline": current_redline(
                    module_values["schedule_status"],
                    module_values["cost_status"],
                    module_values["collection_status"],
                ),
                "owner": owners.get(subproject, ""),
                "last_updated": latest_date_string(*last_updated_values),
            }
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "subproject",
                "scope_status",
                "schedule_status",
                "cost_status",
                "procurement_status",
                "resource_status",
                "risk_status",
                "collection_status",
                "current_redline",
                "owner",
                "last_updated",
            ],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Cockpit built: {OUTPUT_FILE}")
    print(f"Subprojects included: {len(output_rows)}")


if __name__ == "__main__":
    build()
