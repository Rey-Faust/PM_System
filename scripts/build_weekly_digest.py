#!/usr/bin/env python3
import csv
from datetime import date, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "pmo_weekly_digest.md"

STATUS_RANK = {"green": 0, "yellow": 1, "red": 2}


def load_csv_rows(file_name: str):
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        return []
    with file_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def parse_date(value: str):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_int(value: str, default: int = 0) -> int:
    raw = (value or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def is_truthy(value: str) -> bool:
    return (value or "").strip().lower() in {"yes", "y", "true", "1"}


def is_open_status(value: str) -> bool:
    return (value or "").strip().lower() not in {"closed", "done", "resolved", "complete", "completed"}


def clean_cell(value: str) -> str:
    return (value or "").replace("\n", " ").replace("|", "/").strip()


def markdown_table(headers, rows):
    if not rows:
        return "_无_"
    head = "| " + " | ".join(headers) + " |"
    split = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(clean_cell(row.get(h, "")) for h in headers) + " |")
    return "\n".join([head, split, *body])


def count_by_status(rows, field):
    counters = {"Green": 0, "Yellow": 0, "Red": 0}
    for row in rows:
        normalized = normalize_status(row.get(field, ""))
        if normalized == "green":
            counters["Green"] += 1
        elif normalized == "yellow":
            counters["Yellow"] += 1
        elif normalized == "red":
            counters["Red"] += 1
    return counters


def latest_objective_row(rows):
    if not rows:
        return None
    def sort_key(row):
        return parse_date(row.get("last_updated") or "") or date(1970, 1, 1)

    return sorted(rows, key=sort_key, reverse=True)[0]


def build():
    now = datetime.now()
    today = now.date()
    within_7_days = today + timedelta(days=7)

    objectives = load_csv_rows("master_objectives.csv")
    cockpit = load_csv_rows("pmo_master_control.csv")
    weekly = load_csv_rows("weekly_progress.csv")
    risks = load_csv_rows("risk_issue_log.csv")
    procurement = load_csv_rows("procurement_tracking.csv")
    collection = load_csv_rows("collection_tracking.csv")
    decisions = load_csv_rows("meeting_decision_tracker.csv")
    interfaces = load_csv_rows("interface_register.csv")

    objective_row = latest_objective_row(objectives)
    objective_table = []
    if objective_row:
        objective_table.append(
            {
                "主项目": objective_row.get("master_project", ""),
                "总工期目标": objective_row.get("total_schedule_target", ""),
                "总预算目标": objective_row.get("total_budget_target", ""),
                "总质量目标": objective_row.get("total_quality_target", ""),
                "总回款目标": objective_row.get("total_collection_target", ""),
                "总客户关系目标": objective_row.get("total_client_target", ""),
                "状态": objective_row.get("objective_status", ""),
                "PMO负责人": objective_row.get("pmo_lead", ""),
            }
        )

    redline_rows = []
    for row in cockpit:
        redline = (row.get("current_redline") or "").strip()
        if redline and redline.lower() != "none":
            redline_rows.append(
                {
                    "子项目": row.get("subproject", ""),
                    "红线": redline,
                    "工期": row.get("schedule_status", ""),
                    "利润": row.get("cost_status", ""),
                    "回款": row.get("collection_status", ""),
                    "负责人": row.get("owner", ""),
                }
            )

    cockpit_snapshot = []
    for row in cockpit:
        cockpit_snapshot.append(
            {
                "子项目": row.get("subproject", ""),
                "范围": row.get("scope_status", ""),
                "进度": row.get("schedule_status", ""),
                "成本": row.get("cost_status", ""),
                "采购": row.get("procurement_status", ""),
                "资源": row.get("resource_status", ""),
                "风险": row.get("risk_status", ""),
                "回款": row.get("collection_status", ""),
                "当前红线": row.get("current_redline", ""),
                "负责人": row.get("owner", ""),
            }
        )

    escalation_items = []
    for row in weekly:
        if is_truthy(row.get("needs_escalation", "")) or normalize_status(row.get("schedule_status", "")) == "red":
            escalation_items.append(
                {
                    "来源": "进度",
                    "子项目": row.get("subproject", ""),
                    "事项": f"{row.get('milestone', '')} | {row.get('deviation_reason', '')}",
                    "责任人": row.get("responsible_party", ""),
                    "截止": row.get("planned_finish_date", ""),
                    "状态": row.get("schedule_status", ""),
                }
            )

    for row in risks:
        severity = (row.get("severity") or "").strip().lower()
        row_type = (row.get("type") or "").strip().lower()
        row_status = normalize_status(row.get("risk_status", ""))
        if is_open_status(row.get("status", "")) and (
            row_type == "issue" or severity in {"high", "critical"} or row_status == "red"
        ):
            escalation_items.append(
                {
                    "来源": "风险/问题",
                    "子项目": row.get("subproject", ""),
                    "事项": row.get("description", ""),
                    "责任人": row.get("owner", ""),
                    "截止": row.get("due_date", ""),
                    "状态": row.get("risk_status", ""),
                }
            )

    for row in procurement:
        critical = is_truthy(row.get("is_critical_path", ""))
        delay_days = parse_int(row.get("delay_days", "0"), default=0)
        status = normalize_status(row.get("procurement_status", ""))
        if critical and (delay_days > 0 or status == "red"):
            escalation_items.append(
                {
                    "来源": "采购",
                    "子项目": row.get("subproject", ""),
                    "事项": f"{row.get('material_or_equipment', '')} | {row.get('impact_description', '')}",
                    "责任人": row.get("responsible_party", ""),
                    "截止": row.get("required_on_site_date", ""),
                    "状态": row.get("procurement_status", ""),
                }
            )

    for row in collection:
        overdue_days = parse_int(row.get("days_overdue", "0"), default=0)
        status = normalize_status(row.get("collection_status", ""))
        if overdue_days > 0 or status == "red":
            escalation_items.append(
                {
                    "来源": "回款",
                    "子项目": row.get("subproject", ""),
                    "事项": f"{row.get('invoice_id', '')} | 应收:{row.get('amount_due', '')}",
                    "责任人": row.get("owner", ""),
                    "截止": row.get("due_date", ""),
                    "状态": row.get("collection_status", ""),
                }
            )

    def escalation_sort_key(row):
        d = parse_date(row.get("截止", ""))
        return d or date(9999, 12, 31)

    escalation_items = sorted(escalation_items, key=escalation_sort_key)

    open_decisions = []
    overdue_decisions = []
    for row in decisions:
        if not is_open_status(row.get("status", "")):
            continue
        item = {
            "会议日期": row.get("meeting_date", ""),
            "事项": row.get("item", ""),
            "决议": row.get("decision", ""),
            "责任人": row.get("owner", ""),
            "截止": row.get("due_date", ""),
            "状态": row.get("status", ""),
        }
        open_decisions.append(item)
        due = parse_date(row.get("due_date", ""))
        if due and due < today:
            overdue_decisions.append(item)

    due_soon_decisions = []
    for row in open_decisions:
        due = parse_date(row.get("截止", ""))
        if due and today <= due <= within_7_days:
            due_soon_decisions.append(row)

    blocked_interfaces = []
    for row in interfaces:
        status = normalize_status(row.get("interface_status", ""))
        if status in {"yellow", "red"}:
            blocked_interfaces.append(
                {
                    "子项目": row.get("subproject", ""),
                    "接口事项": row.get("interface_item", ""),
                    "对方": row.get("counterparty", ""),
                    "卡点": row.get("current_blocker", ""),
                    "截止": row.get("due_date", ""),
                    "负责人": row.get("owner", ""),
                    "状态": row.get("interface_status", ""),
                }
            )

    module_fields = [
        ("范围", "scope_status"),
        ("进度", "schedule_status"),
        ("成本", "cost_status"),
        ("采购", "procurement_status"),
        ("资源", "resource_status"),
        ("风险", "risk_status"),
        ("回款", "collection_status"),
    ]
    module_summary_rows = []
    for name, field in module_fields:
        counters = count_by_status(cockpit, field)
        module_summary_rows.append(
            {
                "模块": name,
                "Green": str(counters["Green"]),
                "Yellow": str(counters["Yellow"]),
                "Red": str(counters["Red"]),
            }
        )

    action_items = []
    if redline_rows:
        action_items.append(f"- 24小时内召开红线专题会，处理 {len(redline_rows)} 项红线偏差。")
    if escalation_items:
        action_items.append(f"- 本周总控会需逐项关闭 {len(escalation_items)} 条升级事项，明确责任人和截止日。")
    if overdue_decisions:
        action_items.append(f"- 先处理 {len(overdue_decisions)} 条逾期决议，避免问题跨周滚动。")
    if blocked_interfaces:
        action_items.append(f"- 对 {len(blocked_interfaces)} 条接口卡点执行对外升级，纳入接口跟踪清单。")
    if not action_items:
        action_items.append("- 当前未发现红线或逾期事项，维持既定节奏并继续每周校准。")

    lines = []
    lines.append("# PMO 周总控简报")
    lines.append("")
    lines.append(f"- 生成时间：{now.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- 子项目数量：{len(cockpit)}")
    lines.append(f"- 红线数量：{len(redline_rows)}")
    lines.append(f"- 升级事项：{len(escalation_items)}")
    lines.append("")
    lines.append("## 1. 总目标基线")
    lines.append("")
    if objective_table:
        lines.append(
            markdown_table(
                ["主项目", "总工期目标", "总预算目标", "总质量目标", "总回款目标", "总客户关系目标", "状态", "PMO负责人"],
                objective_table,
            )
        )
    else:
        lines.append("_未填写 master_objectives.csv，建议先录入总目标基线。_")
    lines.append("")
    lines.append("## 2. 驾驶舱状态概览")
    lines.append("")
    lines.append(markdown_table(["模块", "Green", "Yellow", "Red"], module_summary_rows))
    lines.append("")
    lines.append(markdown_table(["子项目", "范围", "进度", "成本", "采购", "资源", "风险", "回款", "当前红线", "负责人"], cockpit_snapshot))
    lines.append("")
    lines.append("## 3. 三条红线预警")
    lines.append("")
    lines.append(markdown_table(["子项目", "红线", "工期", "利润", "回款", "负责人"], redline_rows))
    lines.append("")
    lines.append("## 4. 本周需升级事项")
    lines.append("")
    lines.append(markdown_table(["来源", "子项目", "事项", "责任人", "截止", "状态"], escalation_items))
    lines.append("")
    lines.append("## 5. 会议决议关闭追踪")
    lines.append("")
    lines.append(f"- 逾期未关闭：{len(overdue_decisions)}")
    lines.append(f"- 7天内到期：{len(due_soon_decisions)}")
    lines.append("")
    lines.append(markdown_table(["会议日期", "事项", "决议", "责任人", "截止", "状态"], open_decisions))
    lines.append("")
    lines.append("## 6. 接口卡点")
    lines.append("")
    lines.append(markdown_table(["子项目", "接口事项", "对方", "卡点", "截止", "负责人", "状态"], blocked_interfaces))
    lines.append("")
    lines.append("## 7. 建议动作（自动生成）")
    lines.append("")
    lines.extend(action_items)
    lines.append("")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"Weekly digest built: {OUTPUT_FILE}")
    print(f"Escalation items: {len(escalation_items)}")
    print(f"Open decisions: {len(open_decisions)}")


if __name__ == "__main__":
    build()
