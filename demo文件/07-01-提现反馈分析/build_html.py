import json

base = '/Users/zncu/Downloads/zncu-cursor workplace/demo文件/07-01-提现反馈分析'
with open(f'{base}/data.json', encoding='utf-8') as f:
    data = json.load(f)

before_total = data['before']['total'] or 1
after_total = data['after']['total'] or 1
bt, at = data['before']['daily_total'], data['after']['daily_total']
total_reduction = round((1 - at / bt) * 100) if bt else 0
fail_before_share = round(data['before']['fail'] / before_total * 100, 1)
fail_after_share = round(data['after']['fail'] / after_total * 100, 1)
fail_share_delta = round(fail_after_share - fail_before_share, 1)


def pct_chg(before, after):
    if not before:
        return 'flat', '—'
    pct = round((1 - after / before) * 100)
    if pct > 0:
        return 'down', f'↓{pct}%'
    if pct < 0:
        return 'up', f'↑{abs(pct)}%'
    return 'flat', '持平'


def share_chg(before_share, after_share):
    delta = round(after_share - before_share, 1)
    if delta < 0:
        return 'down', f'占比 ↓{abs(delta)}pct'
    if delta > 0:
        return 'up', f'占比 ↑{delta}pct'
    return 'flat', '—'


# 每日总览：全量提现反馈保留日均；分类问题用阶段占比，不用日均
daily_compare_items = []
b, a = data['before']['daily_total'], data['after']['daily_total']
cls, chg = pct_chg(b, a)
daily_compare_items.append(f'''
<div class="daily-compare-item">
  <div class="dci-label"><span class="dot" style="background:#95a5a6"></span>总提现反馈日均</div>
  <div class="dci-values">
    <span class="dci-before">优化前 <strong>{b}</strong></span>
    <span class="dci-arrow">→</span>
    <span class="dci-after">优化后 <strong>{a}</strong></span>
    <span class="chg {cls}">{chg}</span>
  </div>
  <div class="dci-sub">阶段总量 {data['before']['total']} 条 → {data['after']['total']} 条 · {data['before']['days']}天 vs {data['after']['days']}天</div>
</div>''')
cls, chg = share_chg(fail_before_share, fail_after_share)
daily_compare_items.append(f'''
<div class="daily-compare-item">
  <div class="dci-label"><span class="dot" style="background:#ff4d4d"></span>提现失败占比</div>
  <div class="dci-values">
    <span class="dci-before">优化前 <strong>{fail_before_share}%</strong></span>
    <span class="dci-arrow">→</span>
    <span class="dci-after">优化后 <strong>{fail_after_share}%</strong></span>
    <span class="chg {cls}">{chg}</span>
  </div>
  <div class="dci-sub">阶段条数 {data['before']['fail']} 条 → {data['after']['fail']} 条 · 占各阶段总提现反馈比例</div>
</div>''')

CAT_COLORS = {
    '提现失败/退回': '#ff4d4d',
    '无法提现/提现受阻': '#ff9500',
    '提现未到账/处理中': '#ff4d88',
    '微信提现通道问题': '#9b59b6',
    '提现状态/显示异常': '#4f7cae',
    '账号绑定/换绑/身份不符': '#00cc99',
    '金额/余额异常': '#e67e22',
    '提现焦虑/到账时间': '#f39c12',
    '使用咨询/操作指引': '#95a5a6',
    '催促处理/跟进': '#34495e',
    '虚假宣传/投诉维权': '#c0392b',
    '其他/咨询类': '#bdc3c7',
}

LABEL_DEFS = [
    ('无法提现/提现受阻', '系统拦截用户提现行为，无法完成流程'),
    ('提现失败/退回', '提现申请被拒绝或资金被退回'),
    ('提现未到账/处理中', '申请已提交但长时间未到账或状态卡在「处理中」'),
    ('提现状态/显示异常', '页面展示信息与实际不符'),
    ('账号绑定/换绑/身份不符', '微信/支付宝绑定问题导致无法提现'),
    ('提现焦虑/到账时间', '对到账时间过长的焦虑反馈'),
    ('金额/余额异常', '账户余额与预期不符'),
    ('微信提现通道问题', '微信渠道特有的提现问题'),
    ('催促处理/跟进', '用户主动催促问题处理进度'),
    ('虚假宣传/投诉维权', '涉及虚假宣传或强烈投诉'),
    ('使用咨询/操作指引', '操作咨询类（如怎么提现、门槛规则等）'),
    ('其他/咨询类', '未归入以上标签的咨询反馈'),
]

cat_cards = []
for cat in data['cats_order']:
    stats = data['cat_stage_stats'][cat]
    total = data['category_counts'].get(cat, 0)
    if total == 0:
        continue
    before_share = round(stats['before'] / before_total * 100, 1)
    after_share = round(stats['after'] / after_total * 100, 1)
    cls, chg_text = share_chg(before_share, after_share)
    chg = f'<span class="chg {cls}">{chg_text}</span>' if chg_text != '—' else ''
    cat_id = cat.replace('/', '-').replace(' ', '')
    cat_cards.append(f'''
    <div class="cat-card" data-cat="{cat}">
      <div class="cat-card-head">
        <span class="cat-dot" style="background:{CAT_COLORS.get(cat, '#999')}"></span>
        <div>
          <div class="cat-name">{cat} <span class="cat-total">{total}条</span></div>
          <div class="cat-stat">优化前 {stats["before"]}条（占{before_share}%）→ 优化后 {stats["after"]}条（占{after_share}%） {chg}</div>
        </div>
      </div>
      <div class="cat-chart-wrap"><canvas id="chart-{cat_id}"></canvas></div>
    </div>''')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>用户提现反馈分析 · 6.1-7.1</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
:root {{
  --brand: #ff4d88; --bg: #f2f2f5; --surface: #fff; --text: #323232;
  --text2: #666; --text3: #999; --line: rgba(0,0,0,.08);
  --success: #00cc99; --danger: #ff4d4d; --warning: #ff9500;
  --radius: 12px; --shadow: 0 2px 10px rgba(50,50,50,.08);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "PingFang SC", -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 24px 16px 48px; }}
header {{
  background: linear-gradient(135deg, #ff4d88 0%, #ff7eb3 100%);
  color: #fff; border-radius: var(--radius); padding: 28px 32px; margin-bottom: 24px; box-shadow: var(--shadow);
}}
header h1 {{ font-size: 24px; font-weight: 600; margin-bottom: 8px; }}
header p {{ font-size: 14px; opacity: .9; }}
.badge {{ display: inline-block; background: rgba(255,255,255,.2); padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-top: 12px; }}
.conclusion {{
  background: var(--surface); border-left: 4px solid var(--success); border-radius: var(--radius);
  padding: 20px 24px; margin-bottom: 24px; box-shadow: var(--shadow);
}}
.conclusion h2 {{ font-size: 17px; margin-bottom: 12px; color: var(--success); }}
.conclusion p {{ font-size: 14px; color: var(--text2); margin-bottom: 8px; }}
.card {{ background: var(--surface); border-radius: var(--radius); padding: 20px 24px; box-shadow: var(--shadow); margin-bottom: 24px; }}
.card h3 {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; padding-bottom: 12px; border-bottom: 1px solid var(--line); }}
.card .hint {{ font-size: 12px; color: var(--text3); margin-bottom: 16px; }}
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }}
.chart-wrap {{ position: relative; height: 300px; }}
.chart-wrap.tall {{ height: 360px; }}

/* 分类趋势 + 案例面板 */
.trend-layout {{ display: grid; grid-template-columns: 1fr 380px; gap: 20px; align-items: start; }}
@media (max-width: 1100px) {{ .trend-layout {{ grid-template-columns: 1fr; }} }}
.cat-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }}
.cat-card {{
  border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px;
  transition: border-color .2s, box-shadow .2s; cursor: crosshair;
}}
.cat-card.active {{ border-color: var(--brand); box-shadow: 0 0 0 2px rgba(255,77,136,.15); }}
.cat-card-head {{ display: flex; gap: 10px; margin-bottom: 10px; }}
.cat-dot {{ width: 10px; height: 10px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }}
.cat-name {{ font-size: 14px; font-weight: 600; }}
.cat-total {{ font-size: 12px; color: var(--text3); font-weight: 400; }}
.cat-stat {{ font-size: 11px; color: var(--text3); margin-top: 2px; }}
.chg {{ font-size: 11px; padding: 1px 6px; border-radius: 4px; margin-left: 4px; }}
.chg.down {{ background: #e8f5e9; color: #2e7d32; }}
.chg.up {{ background: #ffebee; color: #c62828; }}
.chg.flat {{ background: #f5f5f5; color: #999; }}
.cat-chart-wrap {{ position: relative; height: 140px; }}

.case-panel {{
  position: sticky; top: 16px; background: var(--surface); border-radius: var(--radius);
  border: 1px solid var(--line); box-shadow: var(--shadow); overflow: hidden;
}}
.case-panel-head {{
  padding: 16px 18px; background: linear-gradient(135deg, #fff5f8, #fff);
  border-bottom: 1px solid var(--line);
}}
.case-panel-head h4 {{ font-size: 15px; font-weight: 600; }}
.case-panel-head .meta {{ font-size: 12px; color: var(--text3); margin-top: 4px; }}
.case-panel-body {{ max-height: calc(100vh - 120px); overflow-y: auto; padding: 12px 16px 16px; }}
.case-empty {{ text-align: center; padding: 40px 20px; color: var(--text3); font-size: 13px; }}
.case-item {{
  padding: 12px; border-radius: 8px; background: #fafafa; margin-bottom: 10px;
  border-left: 3px solid var(--brand);
}}
.case-item:last-child {{ margin-bottom: 0; }}
.case-item .case-meta {{ font-size: 11px; color: var(--text3); margin-bottom: 6px; display: flex; gap: 8px; flex-wrap: wrap; }}
.case-item .case-text {{ font-size: 13px; color: var(--text); line-height: 1.55; }}
.tag {{ display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 11px; }}
.stage-before {{ background: #fff3e0; color: #e65100; }}
.stage-after {{ background: #e8f5e9; color: #2e7d32; }}
.emotion {{ background: #f0f0f0; color: #666; }}

.filters {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }}
.filters select, .filters input {{ padding: 8px 12px; border: 1px solid var(--line); border-radius: 8px; font-size: 13px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ background: #fafafa; font-weight: 500; color: var(--text2); position: sticky; top: 0; }}
.table-wrap {{ max-height: 480px; overflow: auto; border: 1px solid var(--line); border-radius: 8px; }}
.daily-compare-row {{
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px;
}}
@media (max-width: 900px) {{ .daily-compare-row {{ grid-template-columns: 1fr; }} }}
.daily-compare-item {{
  background: #fafafa; border-radius: 8px; padding: 14px 16px; border: 1px solid var(--line);
}}
.dci-label {{ font-size: 13px; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }}
.dci-label .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
.dci-values {{ font-size: 13px; color: var(--text2); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.dci-values strong {{ font-size: 18px; color: var(--text); }}
.dci-arrow {{ color: var(--text3); }}
.dci-sub {{ font-size: 11px; color: var(--text3); margin-top: 6px; }}
.daily-charts {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; }}
@media (max-width: 900px) {{ .daily-charts {{ grid-template-columns: 1fr; }} }}
@media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>用户提现反馈分析</h1>
    <p>数据周期：2026年6月1日 — 7月1日 · 共 {data['total']} 条提现关键词反馈{f"（已排除 {data.get('excluded_count', 0)} 条返还网App反馈）" if data.get('excluded_count') else ''}</p>
    <span class="badge">背景：6月25日上线提现流程优化 · 6月25日归入优化前，优化后从6月26日起</span>
  </header>

  <section class="conclusion">
    <h2>核心结论：提现失败类反馈明显减少</h2>
    <p>优化前（6.1—6.25，{data['before']['days']}天）vs 优化后（6.26—7.1，{data['after']['days']}天）：总提现反馈日均 {data['before']['daily_total']} → <strong>{data['after']['daily_total']}</strong>（↓{total_reduction}%）；「提现失败/退回」占比 {fail_before_share}% → <strong>{fail_after_share}%</strong>（占比下降 {abs(fail_share_delta)}pct）</p>
  </section>

  <div class="card">
    <h3>各类别趋势变化</h3>
    <p class="hint">按各阶段内占比对比（非日均）· 悬停趋势图日期点可查看当日真实反馈</p>
    <div class="trend-layout">
      <div class="cat-grid" id="catGrid">
        {''.join(cat_cards)}
      </div>
      <div class="case-panel" id="casePanel">
        <div class="case-panel-head">
          <h4 id="caseTitle">用户反馈案例</h4>
          <div class="meta" id="caseMeta">悬停左侧趋势图上的日期点查看</div>
        </div>
        <div class="case-panel-body" id="caseBody">
          <div class="case-empty">👆 将鼠标移到趋势图的某一天<br>即可查看当日真实反馈 case</div>
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <h3>每日反馈总览</h3>
    <p class="hint">优化前（6.1—6.25，{data['before']['days']}天）vs 优化后（6.26—7.1，{data['after']['days']}天）</p>
    <div class="daily-compare-row">
      {''.join(daily_compare_items)}
    </div>
    <div class="daily-charts">
      <div>
        <p class="hint" style="margin-bottom:8px">每日趋势 · 仅总提现反馈显示阶段日均参考线</p>
        <div class="chart-wrap tall"><canvas id="dailyTrend"></canvas></div>
      </div>
      <div>
        <p class="hint" style="margin-bottom:8px">总提现反馈日均对比 · 优化前 vs 优化后</p>
        <div class="chart-wrap tall"><canvas id="dailyAvgCompare"></canvas></div>
      </div>
    </div>
  </div>

  <div class="card">
    <h3>优化前后结构对比</h3>
    <div class="chart-wrap tall"><canvas id="stackedBar"></canvas></div>
  </div>

  <div class="card">
    <h3>分类明细列表</h3>
    <div class="filters">
      <select id="filterStage"><option value="">全部阶段</option><option value="{data['stage_before']}">优化前(6.1-6.25)</option><option value="{data['stage_after']}">优化后(6.26-7.1)</option></select>
      <select id="filterCat"><option value="">全部分类</option></select>
      <input type="text" id="filterText" placeholder="搜索反馈内容…">
    </div>
    <div class="table-wrap">
      <table><thead><tr><th>日期</th><th>阶段</th><th>分类</th><th>情绪</th><th>反馈内容</th></tr></thead>
      <tbody id="tableBody"></tbody></table>
    </div>
  </div>
</div>

<script>
const DATA = {json.dumps(data, ensure_ascii=False)};
const CAT_COLORS = {json.dumps(CAT_COLORS, ensure_ascii=False)};
const DATE_LABELS = DATA.date_labels.map(d => d.slice(5));
const CUTOFF_DAY_IDX = DATA.date_labels.indexOf('2026-06-25');
const CUTOFF_LINE_IDX = CUTOFF_DAY_IDX + 0.5; // 6.25归优化前，虚线划在6/25与6/26之间

Chart.defaults.font.family = '"PingFang SC", -apple-system, sans-serif';
Chart.defaults.color = '#666';

// 案例索引：date + category -> cases
const caseIndex = {{}};
DATA.records.forEach(r => {{
  const key = r['日期'] + '|' + r['问题分类'];
  if (!caseIndex[key]) caseIndex[key] = [];
  caseIndex[key].push(r);
}});

function showCases(date, category) {{
  const key = date + '|' + category;
  const cases = caseIndex[key] || [];
  const title = document.getElementById('caseTitle');
  const meta = document.getElementById('caseMeta');
  const body = document.getElementById('caseBody');
  const color = CAT_COLORS[category] || '#ff4d88';

  title.textContent = category;
  meta.innerHTML = `<span style="color:${{color}};font-weight:600">${{date}}</span> · 共 ${{cases.length}} 条反馈`;

  document.querySelectorAll('.cat-card').forEach(el => {{
    el.classList.toggle('active', el.dataset.cat === category);
  }});

  if (cases.length === 0) {{
    body.innerHTML = `<div class="case-empty">📭 ${{date.slice(5)}} 当日无「${{category}}」类反馈</div>`;
    return;
  }}

  body.innerHTML = cases.map((c, i) => {{
    const stageCls = c['阶段'].includes('优化后') ? 'stage-after' : 'stage-before';
  const stageText = c['阶段'].includes('优化后') ? '优化后' : '优化前';
    return `<div class="case-item" style="border-left-color:${{color}}">
      <div class="case-meta">
        <span>#${{i+1}}</span>
        <span class="tag ${{stageCls}}">${{stageText}}</span>
        <span class="tag emotion">${{c['情绪'] || '未知'}}</span>
        <span>ID: ${{c['反馈ID']}}</span>
      </div>
      <div class="case-text">${{c['反馈内容']}}</div>
    </div>`;
  }}).join('');
}}

function makeCategoryChart(canvasId, category) {{
  const color = CAT_COLORS[category] || '#999';
  const values = DATA.date_labels.map(d => DATA.daily_by_category[category][d] || 0);
  const chart = new Chart(document.getElementById(canvasId), {{
    type: 'line',
    data: {{
      labels: DATE_LABELS,
      datasets: [{{
        data: values,
        borderColor: color,
        backgroundColor: color + '22',
        fill: true,
        tension: 0.3,
        pointRadius: values.map(v => v > 0 ? 4 : 2),
        pointHoverRadius: 7,
        pointBackgroundColor: color,
        borderWidth: 2,
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          enabled: true,
          callbacks: {{
            title: ctx => '2026-' + ctx[0].label,
            label: ctx => `${{category}}: ${{ctx.raw}} 条`,
            afterBody: ctx => {{
              const d = '2026-' + ctx[0].label;
              const n = (caseIndex[d + '|' + category] || []).length;
              return n ? `悬停查看 ${{n}} 条真实反馈` : '当日无反馈';
            }}
          }}
        }},
        annotation: {{
          annotations: {{
            cutoff: {{
              type: 'line', xMin: CUTOFF_LINE_IDX, xMax: CUTOFF_LINE_IDX,
              borderColor: 'rgba(255,77,77,.5)', borderWidth: 1, borderDash: [4,3],
              label: {{ display: true, content: '6.26起', position: 'start', font: {{ size: 9 }} }}
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ ticks: {{ maxTicksLimit: 8, font: {{ size: 10 }} }} }},
        y: {{ beginAtZero: true, ticks: {{ stepSize: 1, font: {{ size: 10 }} }}, suggestedMax: Math.max(2, ...values) }}
      }},
      onHover: (ev, els) => {{
        if (els.length) {{
          const idx = els[0].index;
          showCases(DATA.date_labels[idx], category);
        }}
      }}
    }}
  }});
  chart.canvas.addEventListener('mouseleave', () => {{
    document.querySelectorAll('.cat-card').forEach(el => el.classList.remove('active'));
  }});
  return chart;
}}

// 初始化各类别图表
DATA.cats_order.forEach(cat => {{
  if (!DATA.category_counts[cat]) return;
  const id = 'chart-' + cat.replace(/\\//g, '-').replace(/ /g, '');
  const canvas = document.getElementById(id);
  if (canvas) makeCategoryChart(id, cat);
}});

// 总览趋势（全量就是提现反馈；仅总提现反馈显示阶段日均参考线）
const dailyAvgBefore = DATA.before.daily_total;
const dailyAvgAfter = DATA.after.daily_total;
const beforeEndIdx = CUTOFF_DAY_IDX;
const afterStartIdx = DATA.date_labels.indexOf('2026-06-26');

new Chart(document.getElementById('dailyTrend'), {{
  type: 'line',
  data: {{
    labels: DATE_LABELS,
    datasets: [
      {{ label: '总提现反馈', data: Object.values(DATA.daily_total), borderColor: '#95a5a6', backgroundColor: 'rgba(149,165,166,.08)', fill: true, tension: .3, pointRadius: 3 }},
      {{ label: '提现失败', data: Object.values(DATA.daily_fail), borderColor: '#ff4d4d', borderWidth: 2, tension: .3, pointRadius: 4 }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{
      legend: {{ position: 'bottom' }},
      tooltip: {{
        callbacks: {{
          afterBody: ctx => {{
            const idx = ctx[0].dataIndex;
            const isAfter = idx > CUTOFF_DAY_IDX;
            const b = DATA.before, a = DATA.after;
            return isAfter
              ? `优化后: 总提现反馈日均${{a.daily_total}}条/天 · 失败${{a.fail}}条`
              : `优化前: 总提现反馈日均${{b.daily_total}}条/天 · 失败${{b.fail}}条`;
          }}
        }}
      }},
      annotation: {{
        annotations: {{
          lineCutoff: {{
            type: 'line', xMin: CUTOFF_LINE_IDX, xMax: CUTOFF_LINE_IDX,
            borderColor: '#ff4d4d', borderDash: [6,4], borderWidth: 2,
            label: {{ display: true, content: '6.26 优化后', font: {{ size: 10 }} }}
          }},
          avgTotalBefore: {{
            type: 'line', yMin: dailyAvgBefore, yMax: dailyAvgBefore,
            xMin: 0, xMax: beforeEndIdx,
            borderColor: 'rgba(149,165,166,.7)', borderDash: [5,5], borderWidth: 1.5,
            label: {{ display: true, content: `总提现日均${{dailyAvgBefore}}`, position: 'start', font: {{ size: 9 }} }}
          }},
          avgTotalAfter: {{
            type: 'line', yMin: dailyAvgAfter, yMax: dailyAvgAfter,
            xMin: afterStartIdx, xMax: DATE_LABELS.length - 1,
            borderColor: 'rgba(149,165,166,.9)', borderDash: [2,3], borderWidth: 2,
            label: {{ display: true, content: `总提现日均${{dailyAvgAfter}}`, position: 'end', font: {{ size: 9 }} }}
          }}
        }}
      }}
    }},
    scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }},
    onHover: (ev, els) => {{
      if (els.length) {{
        const idx = els[0].index;
        const date = DATA.date_labels[idx];
        const allCases = DATA.records.filter(r => r['日期'] === date);
        const stage = idx > CUTOFF_DAY_IDX ? '优化后' : '优化前';
        document.getElementById('caseTitle').textContent = '当日全部反馈';
        document.getElementById('caseMeta').innerHTML = `<span style="font-weight:600">${{date}}</span> · <span class="tag ${{idx > CUTOFF_DAY_IDX ? 'stage-after' : 'stage-before'}}">${{stage}}</span> · 共 ${{allCases.length}} 条`;
        document.querySelectorAll('.cat-card').forEach(el => el.classList.remove('active'));
        document.getElementById('caseBody').innerHTML = allCases.length ? allCases.map((c, i) => {{
          const color = CAT_COLORS[c['问题分类']] || '#999';
          const stageCls = c['阶段'].includes('优化后') ? 'stage-after' : 'stage-before';
          return `<div class="case-item" style="border-left-color:${{color}}"><div class="case-meta"><span>#${{i+1}}</span>
            <span class="tag" style="background:${{color}}22;color:${{color}}">${{c['问题分类']}}</span>
            <span class="tag ${{stageCls}}">${{c['阶段'].includes('优化后')?'优化后':'优化前'}}</span>
            <span class="tag emotion">${{c['情绪']||'-'}}</span></div>
            <div class="case-text">${{c['反馈内容']}}</div></div>`;
        }}).join('') : '<div class="case-empty">当日无反馈</div>';
      }}
    }}
  }}
}});

// 总提现反馈日均对比
new Chart(document.getElementById('dailyAvgCompare'), {{
  type: 'bar',
  data: {{
    labels: ['总提现反馈日均'],
    datasets: [
      {{
        label: '优化前',
        data: [DATA.before.daily_total],
        backgroundColor: 'rgba(149,165,166,.55)', borderRadius: 6
      }},
      {{
        label: '优化后',
        data: [DATA.after.daily_total],
        backgroundColor: 'rgba(149,165,166,.9)', borderRadius: 6
      }}
    ]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'bottom' }},
      tooltip: {{
        callbacks: {{
          afterLabel: () => `阶段总量: ${{DATA.before.total}} → ${{DATA.after.total}} 条`
        }}
      }}
    }},
    scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: '条/天' }} }} }}
  }}
}});

// 堆叠柱
const stages = [DATA.stage_before, DATA.stage_after];
const stackCats = DATA.cats_order.filter(c => DATA.category_counts[c]);
new Chart(document.getElementById('stackedBar'), {{
  type: 'bar',
  data: {{
    labels: ['优化前', '优化后'],
    datasets: stackCats.map(c => ({{
      label: c, data: stages.map(s => DATA.stage_cat[s][c] || 0),
      backgroundColor: CAT_COLORS[c], borderRadius: 3
    }}))
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 10, font: {{ size: 10 }} }} }} }},
    scales: {{ x: {{ stacked: true }}, y: {{ stacked: true, beginAtZero: true }} }}
  }}
}});

// 表格
const catSelect = document.getElementById('filterCat');
DATA.cats_order.filter(c => DATA.category_counts[c]).forEach(c => {{
  const o = document.createElement('option'); o.value = c; o.textContent = c; catSelect.appendChild(o);
}});
function renderTable() {{
  const stage = document.getElementById('filterStage').value;
  const cat = document.getElementById('filterCat').value;
  const text = document.getElementById('filterText').value.toLowerCase();
  document.getElementById('tableBody').innerHTML = DATA.records
    .filter(r => (!stage||r['阶段']===stage) && (!cat||r['问题分类']===cat) && (!text||r['反馈内容'].toLowerCase().includes(text)))
    .map(r => {{
      const color = CAT_COLORS[r['问题分类']]||'#999';
      const sc = r['阶段'].includes('优化后')?'stage-after':'stage-before';
      return `<tr><td>${{r['日期'].slice(5)}}</td><td><span class="tag ${{sc}}">${{r['阶段'].includes('优化后')?'优化后':'优化前'}}</span></td>
        <td><span class="tag" style="background:${{color}}22;color:${{color}}">${{r['问题分类']}}</span></td>
        <td>${{r['情绪']||'-'}}</td><td>${{r['反馈内容']}}</td></tr>`;
    }}).join('');
}}
['filterStage','filterCat'].forEach(id => document.getElementById(id).addEventListener('change', renderTable));
document.getElementById('filterText').addEventListener('input', renderTable);
renderTable();
</script>
</body>
</html>'''

with open(f'{base}/提现反馈分析.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML rebuilt')
