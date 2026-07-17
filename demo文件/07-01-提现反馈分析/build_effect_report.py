import json
from pathlib import Path

base = Path('/Users/zncu/Downloads/zncu-cursor workplace/demo文件/07-01-提现反馈分析')
with open(base / 'data.json', encoding='utf-8') as f:
    data = json.load(f)

before_stage = data['stage_before']
after_stage = data['stage_after']
before_total = data['before']['total']
after_total = data['after']['total']


def pct(label, stage):
    count = data['stage_cat'][stage].get(label, 0)
    total = before_total if stage == before_stage else after_total
    return round(count / total * 100, 1) if total else 0


def pct_text(label):
    return f"{pct(label, before_stage)}%→{pct(label, after_stage)}%"


def daily_series(label):
    return [data['daily_by_category'][label][d] for d in data['date_labels']]


def cases_for(label, stage=None, limit=2):
    rows = [r for r in data['records'] if r['问题分类'] == label]
    if stage:
        rows = [r for r in rows if r['阶段'] == stage]
    rows = sorted(rows, key=lambda r: r['日期'], reverse=True)
    return rows[:limit]


def cases_by_ids(ids):
    by_id = {r['反馈ID']: r for r in data['records']}
    return [by_id[i] for i in ids if i in by_id]


labels = [
    {
        'label': '提现失败/退回',
        'problem': '用户反馈集中在提现失败后不知道资金是否退回、能否重新提现、失败原因是什么。典型 case：用户问“提现失败后资金会重新返回余额吗？可以重新提现吗？”；另有用户反馈微信提现卡住后“不知道怎么退回钱重新发起”。',
        'strategy': '通过优化提现通知的完备性，补齐提现成功/失败的信息；明确告知失败原因和对应解决方案；配合超时未到账自动排查和补偿机制，减少用户因“不知道失败后怎么办”产生的反馈。',
        'case_stage': before_stage,
        'case_ids': [15197643106, 15258410365],
    },
    {
        'label': '提现未到账/处理中',
        'problem': '用户核心疑问是提现长期停留在“处理中”、不知道是否还会到账，也不知道是否需要人工处理。典型 case：用户反馈“为什么一直显示提现中”“提现了但是没到账，想了解是什么原因以及该如何处理”。',
        'strategy': '通过优化提现状态流程和状态同步流程，减少“处理中”状态停留时间；同时建立超时未到账自动排查和补偿机制，让异常处理前置，减少“提现中/未到账”类反馈。',
        'case_stage': before_stage,
    },
    {
        'label': '微信提现通道问题',
        'problem': '用户问题主要发生在微信外跳、微信分身、登录微信与收款微信不一致、确认收款页未弹出等环节。典型 case：用户反馈切错微信号后一直显示提现中，或收款微信与登录微信一致却提示不一致。',
        'strategy': '通过优化提现状态同步流程，增强外部通道中断、失败、未确认等状态识别；同时完善失败通知和过程态展示，让用户知道当前卡在哪一步、是否可重试，从而减少微信提现通道类反馈。',
        'case_stage': before_stage,
        'case_ids': [15248574430, 15228942445, 15197374885, 15222533869],
    },
    {
        'label': '金额/余额异常',
        'problem': '用户最焦虑的是“钱没到账，但余额已经没了/少了/归零了”。典型 case：用户反馈提现没成功也没到账但余额没了，或提现后账户出现负余额。',
        'strategy': '通过优化余额计算与钱包状态逻辑，未到账前不做余额扣减，并新增用户无感知的“冻结”态；同时优化余额明细展示、明确余额来源，降低用户对资金丢失的担忧，减少余额异常反馈。',
        'case_stage': before_stage,
    },
    {
        'label': '提现状态/显示异常',
        'problem': '用户反馈页面展示和实际到账不一致，例如显示提现成功但微信未到账、历史进度异常、状态显示与实际资金结果不一致。典型 case：用户反馈“显示已到账，但是钱没有到微信里”。',
        'strategy': '通过优化提现状态同步流程，统一前端展示与后端真实处理结果；完善提现成功、失败的信息完整性，并新增历史余额变动结果，帮助用户回溯资金状态，减少状态显示异常反馈。',
        'case_stage': before_stage,
    },
    {
        'label': '虚假宣传/投诉维权',
        'problem': '这类反馈通常由提现失败、余额异常、状态不透明升级而来。典型 case：用户因为多单不能提现、页面提示异常，质疑活动是否虚假、是否欺骗消费者。',
        'strategy': '通过提现通知完备性、余额状态逻辑、过程态可视化三类优化，降低用户对资金流向和提现结果的误解，避免普通异常反馈升级为投诉或平台信任问题。',
        'case_stage': before_stage,
    },
]

colors = {
    '提现失败/退回': '#ff4d4d',
    '提现未到账/处理中': '#ff4d88',
    '微信提现通道问题': '#9b59b6',
    '金额/余额异常': '#e67e22',
    '提现状态/显示异常': '#4f7cae',
    '虚假宣传/投诉维权': '#c0392b',
}

rows_html = []
for idx, item in enumerate(labels):
    label = item['label']
    before_count = data['stage_cat'][before_stage].get(label, 0)
    after_count = data['stage_cat'][after_stage].get(label, 0)
    before_pct = pct(label, before_stage)
    after_pct = pct(label, after_stage)
    change = round(before_pct - after_pct, 1)
    chart_id = f'chart_{idx}'
    sample_cases = cases_by_ids(item['case_ids']) if item.get('case_ids') else cases_for(label, item.get('case_stage'), limit=2)
    cases_html = ''.join(
        f'''<div class="case">
          <div class="case-meta">{c['日期']} · {c.get('情绪') or '未知'} · ID {c['反馈ID']}</div>
          <div>{c['反馈内容']}</div>
        </div>'''
        for c in sample_cases
    )
    strategy_points = [p.strip('。') for p in item['strategy'].replace('；', '。').split('。') if p.strip()]
    strategy_html = '<ul class="strategy-list">' + ''.join(f'<li>{p}。</li>' for p in strategy_points) + '</ul>'
    rows_html.append(f'''
      <tr>
        <td class="tag-cell">
          <div class="tag-name">{label}</div>
        </td>
        <td class="trend-cell">
          <div class="trend-head">
            <div>
              <div class="trend-label">优化前占比</div>
              <div class="trend-value before">{before_pct}%</div>
            </div>
            <div class="trend-arrow">→</div>
            <div>
              <div class="trend-label">优化后占比</div>
              <div class="trend-value after">{after_pct}%</div>
            </div>
          </div>
          <div class="delta">占比下降 {change}pp</div>
          <div class="mini-chart"><canvas id="{chart_id}"></canvas></div>
          <div class="chart-note">每日该标签反馈趋势</div>
        </td>
        <td class="case-cell">
          {cases_html}
          <div class="judgement"><strong>问题判断：</strong>{item['problem']}</div>
        </td>
        <td class="strategy-cell">{strategy_html}</td>
      </tr>
    ''')

chart_payload = [
    {
        'id': f'chart_{idx}',
        'label': item['label'],
        'color': colors[item['label']],
        'data': daily_series(item['label']),
    }
    for idx, item in enumerate(labels)
]

core_fault_before = sum(data['stage_cat'][before_stage].get(x, 0) for x in ['提现失败/退回', '提现未到账/处理中', '微信提现通道问题', '金额/余额异常'])
core_fault_after = sum(data['stage_cat'][after_stage].get(x, 0) for x in ['提现失败/退回', '提现未到账/处理中', '微信提现通道问题', '金额/余额异常'])
core_fault_before_pct = round(core_fault_before / before_total * 100, 1)
core_fault_after_pct = round(core_fault_after / after_total * 100, 1)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>提现流程优化成效分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
:root {{
  --brand: #ff4d88;
  --bg: #f2f2f5;
  --surface: #fff;
  --text: #323232;
  --text2: #666;
  --text3: #999;
  --line: rgba(0,0,0,.1);
  --success: #00a878;
  --danger: #ff4d4d;
  --radius: 12px;
  --shadow: 0 2px 10px rgba(50,50,50,.08);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 24px;
  background: var(--bg);
  color: var(--text);
  font-family: "PingFang SC", -apple-system, BlinkMacSystemFont, sans-serif;
}}
.page {{ max-width: 1500px; margin: 0 auto; }}
.hero {{
  background: linear-gradient(135deg, #ff4d88 0%, #ff7eb3 100%);
  color: #fff;
  border-radius: var(--radius);
  padding: 28px 32px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}}
.hero h1 {{ margin: 0 0 8px; font-size: 26px; }}
.hero p {{ margin: 4px 0; font-size: 14px; opacity: .92; }}
.summary {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}}
.summary-card {{
  background: var(--surface);
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
}}
.summary-card .label {{ color: var(--text3); font-size: 13px; margin-bottom: 6px; }}
.summary-card .value {{ font-size: 24px; font-weight: 700; }}
.summary-card .sub {{ color: var(--text3); font-size: 12px; margin-top: 4px; }}
.report-card {{
  background: var(--surface);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}}
th {{
  background: #f7f7f9;
  color: var(--text2);
  font-weight: 600;
  font-size: 14px;
  text-align: left;
  padding: 14px 16px;
  border-bottom: 1px solid var(--line);
}}
td {{
  padding: 16px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
  font-size: 13px;
  line-height: 1.65;
}}
tr:last-child td {{ border-bottom: none; }}
th:nth-child(1), td:nth-child(1) {{ width: 13%; }}
th:nth-child(2), td:nth-child(2) {{ width: 22%; }}
th:nth-child(3), td:nth-child(3) {{ width: 35%; }}
th:nth-child(4), td:nth-child(4) {{ width: 30%; }}
.tag-name {{ font-size: 16px; font-weight: 700; margin-bottom: 8px; }}
.trend-head {{
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}}
.trend-label {{ color: var(--text3); font-size: 11px; }}
.trend-value {{ font-size: 22px; font-weight: 800; line-height: 1.2; }}
.trend-value.before {{ color: #666; }}
.trend-value.after {{ color: var(--brand); }}
.trend-arrow {{ color: var(--text3); font-size: 18px; }}
.delta {{
  display: inline-block;
  margin: 6px 0 10px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(0,168,120,.1);
  color: var(--success);
  font-size: 12px;
}}
.mini-chart {{
  height: 122px;
  padding: 8px 8px 2px;
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 10px;
  background: linear-gradient(180deg, #fff, #fafafa);
}}
.chart-note {{ margin-top: 6px; color: var(--text3); font-size: 11px; }}
.case {{
  background: #fafafa;
  border-left: 3px solid var(--brand);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
}}
.case-meta {{ color: var(--text3); font-size: 11px; margin-bottom: 4px; }}
.judgement {{
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #fff7fa;
  color: var(--text2);
}}
.strategy-cell {{
  color: var(--text2);
  font-size: 14px;
}}
.strategy-list {{
  margin: 0;
  padding-left: 18px;
}}
.strategy-list li {{
  margin-bottom: 8px;
}}
.strategy-list li:last-child {{ margin-bottom: 0; }}
.note {{
  margin-top: 14px;
  color: var(--text3);
  font-size: 12px;
}}
@media (max-width: 900px) {{
  body {{ padding: 12px; }}
  .summary {{ grid-template-columns: 1fr; }}
  table, thead, tbody, tr, th, td {{ display: block; width: 100% !important; }}
  thead {{ display: none; }}
  tr {{ border-bottom: 12px solid var(--bg); }}
}}
</style>
</head>
<body>
<div class="page">
  <section class="hero">
    <h1>提现流程优化成效分析报告</h1>
    <p>统计口径：6.1—6.25 为优化前，6.26—7.1 为优化后；样本均为提现关键词反馈，共 {data['total']} 条。</p>
    <p>分析方法：整体收敛看提现反馈日均量；具体策略成效看关键标签在全部提现反馈中的占比变化。</p>
  </section>

  <section class="summary">
    <div class="summary-card">
      <div class="label">提现反馈日均量</div>
      <div class="value">{data['before']['daily_total']}→{data['after']['daily_total']} 条/天</div>
      <div class="sub">优化后整体反馈有所收敛</div>
    </div>
    <div class="summary-card">
      <div class="label">核心故障类占比</div>
      <div class="value">{core_fault_before_pct}%→{core_fault_after_pct}%</div>
      <div class="sub">失败、未到账、微信通道、余额异常</div>
    </div>
    <div class="summary-card">
      <div class="label">优化后归零标签</div>
      <div class="value">4 个</div>
      <div class="sub">未到账/处理中、微信通道、余额异常、投诉维权</div>
    </div>
  </section>

  <section class="report-card">
    <table>
      <thead>
        <tr>
          <th>关键标签</th>
          <th>占比变化与趋势</th>
          <th>用户 case 与问题判断</th>
          <th>优化策略与减少的反馈</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
      </tbody>
    </table>
  </section>
  <div class="note">说明：占比 = 当前标签反馈数 / 当前阶段全部提现反馈数。趋势图展示每日该标签反馈数，红色虚线为 6.26 优化后起点。</div>
</div>

<script>
const DATE_LABELS = {json.dumps([d[5:] for d in data['date_labels']], ensure_ascii=False)};
const CHARTS = {json.dumps(chart_payload, ensure_ascii=False)};
const CUTOFF_LINE_IDX = DATE_LABELS.indexOf('06-25') + 0.5;
Chart.defaults.font.family = '"PingFang SC", -apple-system, sans-serif';
Chart.defaults.color = '#666';
CHARTS.forEach(cfg => {{
  new Chart(document.getElementById(cfg.id), {{
    type: 'line',
    data: {{
      labels: DATE_LABELS,
      datasets: [{{
        label: cfg.label,
        data: cfg.data,
        borderColor: cfg.color,
        backgroundColor: cfg.color + '22',
        fill: true,
        tension: .3,
        pointRadius: cfg.data.map(v => v > 0 ? 2.5 : 0),
        borderWidth: 2
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ callbacks: {{ title: ctx => '2026-' + ctx[0].label }} }},
        annotation: {{
          annotations: {{
            cutoff: {{
              type: 'line',
              xMin: CUTOFF_LINE_IDX,
              xMax: CUTOFF_LINE_IDX,
              borderColor: 'rgba(255,77,77,.6)',
              borderDash: [4,3],
              borderWidth: 1
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ display: false }},
        y: {{ beginAtZero: true, ticks: {{ stepSize: 1, font: {{ size: 10 }} }} }}
      }}
    }}
  }});
}});
</script>
</body>
</html>'''

with open(base / '提现优化成效分析报告.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(base / '提现优化成效分析报告.html')
