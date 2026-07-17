import pandas as pd
import json
from datetime import date

path = '/Users/zncu/Downloads/用户提现反馈6.1-7.1.xlsx'
df = pd.read_excel(path)
df['反馈时间'] = pd.to_datetime(df['反馈时间'])
df['日期'] = df['反馈时间'].dt.date

# 不属于本次美柚钱包提现统计的反馈
EXCLUDE_IDS = {
    15265987079,  # 06-28 柚币兑换+返还APP提现失败，属返还网App
    15228942445,  # 06-15 微信分身/收款微信一致性问题，用户要求剔除
    15197374885,  # 06-02 收款微信显示不一致但实际一致，用户要求剔除
}
df = df[~df['反馈ID'].isin(EXCLUDE_IDS)].copy()

MANUAL = {
    0: '账号绑定/换绑/身份不符', 1: '使用咨询/操作指引', 5: '使用咨询/操作指引',
    8: '使用咨询/操作指引', 11: '提现焦虑/到账时间', 12: '使用咨询/操作指引',
    13: '提现失败/退回', 18: '无法提现/提现受阻', 24: '提现焦虑/到账时间',
    26: '使用咨询/操作指引', 29: '提现失败/退回', 32: '使用咨询/操作指引',
    34: '使用咨询/操作指引', 38: '使用咨询/操作指引', 47: '使用咨询/操作指引',
    53: '使用咨询/操作指引', 54: '使用咨询/操作指引', 58: '无法提现/提现受阻',
    65: '使用咨询/操作指引', 67: '使用咨询/操作指引', 68: '使用咨询/操作指引',
    78: '使用咨询/操作指引', 90: '使用咨询/操作指引', 96: '账号绑定/换绑/身份不符',
    97: '提现焦虑/到账时间', 98: '使用咨询/操作指引', 104: '使用咨询/操作指引',
    105: '使用咨询/操作指引', 108: '账号绑定/换绑/身份不符', 116: '虚假宣传/投诉维权',
    120: '使用咨询/操作指引', 122: '使用咨询/操作指引', 126: '使用咨询/操作指引',
    137: '金额/余额异常', 143: '账号绑定/换绑/身份不符', 152: '使用咨询/操作指引',
    161: '使用咨询/操作指引',
}


def classify(text):
    if pd.isna(text):
        return '其他/咨询类'
    t = str(text)
    labels = []
    if any(k in t for k in ['欺骗', '假的', '骗人', '维权', '赔偿', '投诉', '不接受']):
        labels.append('虚假宣传/投诉维权')
    wechat_channel = any(k in t for k in [
        '微信分身', '微信通道', '微信小号', '不支持微信', '切错微信',
        '登录的微信不一致', '收款微信', '绑定的微信', '微信提现', '跳到微信', '确认收款',
    ])
    binding_kw = [
        '解绑', '换绑', '绑定', '删除', '修改', '更换提现', '取消绑定',
        '提现账户', '提现账号', '收款账号', '验证码', '手机号', '支付宝账号',
        '身份', '实名', '回乡证', '港澳', '注销',
    ]
    is_binding = any(k in t for k in binding_kw)
    if any(k in t for k in ['余额没了', '余额没有了', '余额为0', '负的余额', '返现不见了', '返现变少', '钱没有了', '现金去哪']):
        labels.append('金额/余额异常')
    if '余额' in t and any(k in t for k in ['没了', '没有了', '少了', '不对', '负', '不见了']):
        if '金额/余额异常' not in labels:
            labels.append('金额/余额异常')
    is_fail = any(k in t for k in [
        '提现失败', '提现不成功', '没成功', '未成功', '失败了', '退回', '退回去',
        '被退回', '提现不了', '无法提现', '不能提现', '提不了', '不允许提现', '被锁定',
    ])
    is_block = any(k in t for k in [
        '提现不了', '无法提现', '不能提现', '提不了', '不允许提现', '被锁定',
        '点不了', '没反应', '灰色的', '卡住', '正在提交',
    ])
    is_processing = any(k in t for k in [
        '未到账', '没到账', '一直没到账', '还没到账', '迟迟没到账',
        '处理中', '提现中', '审核中', '申请中', '大半年',
    ])
    is_display = any(k in t for k in [
        '显示已到账', '显示返现成功', '显示与', '显示在提现中', '显示提现中',
        '显示账户', '显示被锁定', '显示不允许', '半年前的进度', '余额显示',
    ])
    is_anxiety = any(k in t for k in ['多久', '什么时候', '等多久', '到账时间', '24小时', '一个月', '七天', '太慢', '快点'])
    pure_consult = any(k in t for k in [
        '怎么提现', '如何提现', '怎么才能提现', '如何才能提现', '返现怎么提现',
        '返现如何提现', '咨询提现', '想要提现', '提现入口', '提现页面', '钱包入口',
        '提现有门槛', '提现有次数', '可以直接提现', '积累多少可以提现',
        '提现后可以解绑', '提现需要等', '提现要手续费',
    ])
    if '虚假宣传/投诉维权' in labels:
        return '虚假宣传/投诉维权'
    if is_fail and any(k in t for k in ['失败', '退回', '退回去', '被退回']):
        return '提现失败/退回'
    if is_binding and not is_fail and not is_processing and pure_consult:
        if any(k in t for k in ['解绑', '换绑', '删除', '取消绑定', '修改']):
            return '账号绑定/换绑/身份不符'
    if wechat_channel and (is_fail or is_block or is_processing):
        return '微信提现通道问题'
    if '金额/余额异常' in labels:
        return '金额/余额异常'
    if is_block:
        return '无法提现/提现受阻'
    if is_fail:
        return '提现失败/退回'
    if is_processing:
        return '提现未到账/处理中'
    if is_display:
        return '提现状态/显示异常'
    if is_binding:
        return '账号绑定/换绑/身份不符'
    if is_anxiety:
        return '提现焦虑/到账时间'
    if pure_consult:
        return '使用咨询/操作指引'
    return '其他/咨询类'


df['问题分类'] = [MANUAL.get(i, classify(row['反馈内容'])) for i, row in df.iterrows()]
CUTOFF = date(2026, 6, 25)
STAGE_BEFORE = '优化前(6.1-6.25)'
STAGE_AFTER = '优化后(6.26-7.1)'
# 6月25日当天仍算优化前，优化后从6月26日起
df['阶段'] = df['日期'].apply(lambda d: STAGE_AFTER if d > CUTOFF else STAGE_BEFORE)
date_range = pd.date_range('2026-06-01', '2026-07-01').date
daily_fail = df[df['问题分类'] == '提现失败/退回'].groupby('日期').size().reindex(date_range, fill_value=0)
daily_total = df.groupby('日期').size().reindex(date_range, fill_value=0)

cats_order = [
    '提现失败/退回', '无法提现/提现受阻', '提现未到账/处理中', '微信提现通道问题',
    '提现状态/显示异常', '账号绑定/换绑/身份不符', '金额/余额异常', '提现焦虑/到账时间',
    '使用咨询/操作指引', '催促处理/跟进', '虚假宣传/投诉维权', '其他/咨询类',
]
stage_cat = {}
for stage in [STAGE_BEFORE, STAGE_AFTER]:
    sub = df[df['阶段'] == stage]
    stage_cat[stage] = {c: int((sub['问题分类'] == c).sum()) for c in cats_order}

before = df[df['阶段'] == STAGE_BEFORE]
after = df[df['阶段'] == STAGE_AFTER]

daily_by_category = {}
for cat in cats_order:
    s = df[df['问题分类'] == cat].groupby('日期').size().reindex(date_range, fill_value=0)
    daily_by_category[cat] = {str(k): int(v) for k, v in s.items()}

cat_stage_stats = {}
for cat in cats_order:
    b = int((before['问题分类'] == cat).sum())
    a = int((after['问题分类'] == cat).sum())
    bd = before['日期'].nunique() or 1
    ad = after['日期'].nunique() or 1
    cat_stage_stats[cat] = {
        'before': b, 'after': a,
        'daily_before': round(b / bd, 2),
        'daily_after': round(a / ad, 2),
    }

out = {
    'total': len(df),
    'excluded_count': len(EXCLUDE_IDS),
    'excluded_ids': list(EXCLUDE_IDS),
    'cutoff': '2026-06-25',
    'cutoff_after_start': '2026-06-26',
    'stage_before': STAGE_BEFORE,
    'stage_after': STAGE_AFTER,
    'category_counts': {k: int(v) for k, v in df['问题分类'].value_counts().items()},
    'cats_order': cats_order,
    'stage_cat': stage_cat,
    'daily_fail': {str(k): int(v) for k, v in daily_fail.items()},
    'daily_total': {str(k): int(v) for k, v in daily_total.items()},
    'daily_by_category': daily_by_category,
    'cat_stage_stats': cat_stage_stats,
    'date_labels': [str(d) for d in date_range],
    'before': {
        'days': int(before['日期'].nunique()),
        'total': len(before),
        'fail': int((before['问题分类'] == '提现失败/退回').sum()),
        'daily_total': round(len(before) / before['日期'].nunique(), 2),
        'daily_fail': round((before['问题分类'] == '提现失败/退回').sum() / before['日期'].nunique(), 2),
    },
    'after': {
        'days': int(after['日期'].nunique()),
        'total': len(after),
        'fail': int((after['问题分类'] == '提现失败/退回').sum()),
        'daily_total': round(len(after) / after['日期'].nunique(), 2),
        'daily_fail': round((after['问题分类'] == '提现失败/退回').sum() / after['日期'].nunique(), 2),
    },
    'records': df[['反馈ID', '日期', '反馈内容', '问题分类', '阶段', '情绪']].assign(
        日期=lambda x: x['日期'].astype(str)
    ).to_dict('records'),
}

base = '/Users/zncu/Downloads/zncu-cursor workplace/demo文件/07-01-提现反馈分析'
with open(f'{base}/data.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False)
print('saved')
