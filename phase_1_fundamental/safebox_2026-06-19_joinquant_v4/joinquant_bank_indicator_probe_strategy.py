from jqdata import *
from datetime import datetime

import pandas as pd


def initialize(context):
    set_benchmark('512800.XSHG')
    set_option('use_real_price', True)
    set_option('avoid_future_data', True)

    g.probe_codes = [
        '000001.XSHE', '600000.XSHG', '600036.XSHG', '601166.XSHG',
        '601288.XSHG', '601398.XSHG', '601939.XSHG', '601988.XSHG'
    ]
    g.probe_dates = [
        datetime(2021, 5, 28).date(),
        datetime(2021, 8, 31).date(),
        datetime(2022, 4, 29).date(),
        datetime(2022, 8, 31).date(),
        datetime(2023, 4, 28).date(),
        datetime(2023, 8, 31).date(),
        datetime(2024, 4, 30).date(),
        datetime(2024, 8, 30).date(),
        datetime(2025, 4, 30).date(),
        datetime(2025, 8, 29).date(),
        datetime(2026, 4, 30).date(),
    ]
    g.probe_done = False

    run_daily(run_probe_once, time='09:35')


def run_probe_once(context):
    if g.probe_done:
        return

    log.info('========== bank_indicator probe start ==========')
    for probe_date in g.probe_dates:
        probe_bank_indicator_snapshot(probe_date, g.probe_codes)
    g.probe_done = True
    log.info('========== bank_indicator probe end ==========')


def probe_bank_indicator_snapshot(probe_date, codes):
    log.info('---- probe date=%s ----' % str(probe_date))

    try:
        df = get_fundamentals(
            query(
                bank_indicator.code,
                bank_indicator.pubDate,
                bank_indicator.statDate,
                bank_indicator.capital_adequacy_ratio,
                bank_indicator.deposit_loan_ratio,
                bank_indicator.Nonperforming_loan_rate,
                bank_indicator.non_performing_loan_provision_coverage
            ).filter(bank_indicator.code.in_(codes)),
            date=probe_date,
        )
    except Exception as exc:
        log.info('bank_indicator date query failed on %s: %s' % (str(probe_date), str(exc)))
        return

    if df is None or len(df) == 0:
        log.info('bank_indicator date query returned empty on %s' % str(probe_date))
        return

    df = df.copy()
    log.info('rows=%d columns=%s' % (len(df), str(list(df.columns))))

    for col in [
        'capital_adequacy_ratio',
        'deposit_loan_ratio',
        'Nonperforming_loan_rate',
        'non_performing_loan_provision_coverage'
    ]:
        if col not in df.columns:
            log.info('missing column: %s' % col)
            continue
        non_na = int(pd.to_numeric(df[col], errors='coerce').notna().sum())
        log.info('%s coverage=%d/%d' % (col, non_na, len(df)))

    show_cols = [col for col in [
        'code', 'pubDate', 'statDate',
        'capital_adequacy_ratio',
        'deposit_loan_ratio',
        'Nonperforming_loan_rate',
        'non_performing_loan_provision_coverage'
    ] if col in df.columns]
    log.info('\n' + str(df[show_cols].sort_values('code').head(20)))
