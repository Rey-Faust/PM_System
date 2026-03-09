# 字段口径字典（统一填报）

统一状态值：`Green` / `Yellow` / `Red`

- `Green`：正常
- `Yellow`：有风险/待跟进
- `Red`：已偏差/需升级

## 0) `master_objectives.csv`（总目标基线）

- `master_project`：总项目名称/编号
- `baseline_date`：目标基线日期（`YYYY-MM-DD`）
- `total_schedule_target`：总工期目标
- `total_budget_target`：总预算目标
- `total_quality_target`：总质量目标
- `total_collection_target`：总回款目标
- `total_client_target`：总客户关系目标
- `pmo_lead`：PMO 总负责人
- `objective_status`：目标状态

## 0.5) `escalation_matrix.csv`（决策升级矩阵）

- `decision_level`：决策层级（Site/Subproject/PMO）
- `can_decide_items`：该层级可决策事项
- `cannot_decide_items`：该层级不可决策事项
- `escalation_trigger`：触发升级条件
- `sla_hours`：升级响应时限（小时）
- `decision_owner`：该层级责任人
- `report_to`：升级汇报对象

## 1) `subproject_registry.csv`（子项目名录）

- `subproject`：子项目唯一名称
- `owner`：子项目负责人
- `project_manager`：现场项目经理
- `start_date`：开始日期（`YYYY-MM-DD`）
- `target_finish_date`：目标完成日期
- `contract_value`：合同额
- `target_gross_margin_pct`：目标毛利率（0~1）

## 2) `scope_definition.csv`（范围定义）

- `scope_in`：合同范围内工作
- `scope_out`：明确不含范围
- `owner_provided_items`：业主提供项
- `contractor_provided_items`：我方提供项
- `pending_confirmation`：待确认边界
- `scope_status`：范围状态

## 3) `weekly_progress.csv`（周计划与进度）

- `week_start`：本周起始日期
- `milestone`：里程碑
- `planned_finish_date`：计划完成
- `actual_finish_date`：实际完成
- `deviation_days`：偏差天数（正数表示延误）
- `deviation_reason`：偏差原因
- `next_week_plan`：下周动作
- `schedule_status`：进度状态
- `needs_escalation`：是否需升级（Yes/No）

## 4) `cost_tracking.csv`（成本跟踪）

- `contract_value`：合同额
- `target_cost`：目标成本
- `actual_cost_to_date`：已发生成本
- `forecast_final_cost`：预计完工成本
- `cost_variance`：成本偏差（预计完工 - 目标成本）
- `gross_margin_status`：毛利状态
- `cost_status`：成本状态

## 5) `procurement_tracking.csv`（关键采购）

- `material_or_equipment`：关键材料/设备
- `po_date`：下单时间
- `required_on_site_date`：必须到场时间
- `current_status`：当前状态（ordered/in transit/delayed 等）
- `is_critical_path`：是否关键路径（Yes/No）
- `delay_days`：延误天数
- `procurement_status`：采购状态

## 6) `resource_allocation.csv`（资源分配）

- `resource_type`：资源类别（工人/设备/分包等）
- `current_subproject`：当前所在工地
- `next_week_required_subproject`：下周需求工地
- `conflict_flag`：是否冲突（Yes/No）
- `adjustment_plan`：调整方案
- `resource_status`：资源状态

## 7) `risk_issue_log.csv`（风险与问题）

- `id`：编号
- `type`：`Risk` 或 `Issue`
- `description`：描述
- `severity`：严重度（High/Medium/Low）
- `due_date`：关闭目标时间
- `status`：Open/Closed
- `mitigation_or_action`：应对动作
- `risk_status`：风险状态

## 8) `interface_register.csv`（接口清单）

- `interface_item`：接口事项
- `counterparty`：接口对方（业主/顾问/设计/审批等）
- `required_output`：需对方给出的结果
- `current_blocker`：当前卡点
- `interface_status`：接口状态

## 9) `collection_tracking.csv`（回款跟踪）

- `invoice_id`：发票或请款编号
- `amount_due`：应收金额
- `amount_received`：已收金额
- `due_date`：应回款日期
- `days_overdue`：逾期天数
- `collection_status`：回款状态

## 10) `meeting_decision_tracker.csv`（会议决议追踪）

- `item`：决议事项
- `decision`：决议内容
- `due_date`：完成时间
- `status`：Open/Closed
- `close_note`：关闭说明

## 驾驶舱生成规则（`pmo_master_control.csv`）

- 脚本自动汇总每个子项目在 7 个维度的状态：范围/进度/成本/采购/资源/风险/回款。
- 三条红线自动输出在 `current_redline`：
  - `Schedule`（工期）
  - `Profit`（利润）
  - `Collection`（回款）
- 某模块若完全无数据，系统自动标记 `Yellow`，避免“缺报即假绿”。

## 周总控简报（`pmo_weekly_digest.md`）

- 脚本自动汇总：
  - 红线预警（工期/利润/回款）
  - 本周需升级事项（进度、风险问题、采购、回款）
  - 会议决议逾期项
  - 接口卡点
- 生成命令：
  - `cd pmo && make weekly-pack`
