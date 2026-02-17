import os
import csv
from typing import List, Dict, Any, Optional


def read_prices_csv(path: str, symbol: Optional[str] = None, limit: int = 100, offset: Optional[int] = None, from_ts: Optional[int] = None, to_ts: Optional[int] = None) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, 'r') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            try:
                if 'price' in r and r['price'] != '':
                    r['price'] = float(r['price'])
                if 'ts' in r and r['ts'] != '':
                    r['ts'] = int(r['ts'])
            except Exception:
                pass
            if symbol and r.get('symbol') != symbol:
                continue
            if from_ts is not None and ('ts' not in r or r['ts'] < from_ts):
                continue
            if to_ts is not None and ('ts' not in r or r['ts'] > to_ts):
                continue
            rows.append(r)
    # sort ascending by ts
    rows = sorted(rows, key=lambda x: x.get('ts', 0))
    # pagination: if offset is None, return last `limit` rows for backward compatibility
    if offset is None:
        return rows[-limit:]
    else:
        return rows[offset: offset + limit]


def aggregate_ohlc(rows: List[Dict[str, Any]], interval_seconds: int) -> List[Dict[str, Any]]:
    if not rows:
        return []
    # ensure rows sorted by ts ascending
    sorted_rows = sorted([r for r in rows if 'ts' in r and 'price' in r], key=lambda x: int(x['ts']))
    buckets = {}
    order = []
    for r in sorted_rows:
        ts = int(r['ts'])
        price = float(r['price'])
        bucket = ts - (ts % interval_seconds)
        if bucket not in buckets:
            buckets[bucket] = {'open': price, 'high': price, 'low': price, 'close': price, 'count': 1}
            order.append(bucket)
        else:
            b = buckets[bucket]
            b['high'] = max(b['high'], price)
            b['low'] = min(b['low'], price)
            b['close'] = price
            b['count'] += 1
    result = []
    for b in sorted(order):
        item = buckets[b]
        result.append({'bucket_ts': b, 'open': item['open'], 'high': item['high'], 'low': item['low'], 'close': item['close'], 'count': item['count']})
    return result
