#!/usr/bin/env python
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>

import re
from datetime import UTC as utc_tz
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo

    import tzlocal
    tz_name = tzlocal.get_localzone_name()
    local_tz = ZoneInfo(tz_name)
except Exception:
    tz_name = ''
    local_tz = datetime.now().astimezone().tzinfo
UNDEFINED_DATE = datetime(101, 1, 1, tzinfo=utc_tz)

# ISO 8601 regex pattern
_iso8601_re = re.compile(
    r'(\d{4})-?(\d{2})-?(\d{2})'  # date
    r'[T ]?(\d{2})?:?(\d{2})?:?(\d{2})?'  # time
    r'(?:\.(\d+))?'  # microseconds
    r'(Z|[+-]\d{2}:?\d{2})?'  # timezone
)


def _parse_iso8601_python(date_string):
    '''Pure Python ISO 8601 parser replacement for speedup.parse_iso8601.'''
    m = _iso8601_re.match(date_string.strip())
    if not m:
        raise ValueError(f'Invalid ISO 8601 date: {date_string}')

    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    hour = int(m.group(4)) if m.group(4) else 0
    minute = int(m.group(5)) if m.group(5) else 0
    second = int(m.group(6)) if m.group(6) else 0
    microsecond = 0
    if m.group(7):
        frac = m.group(7)[:6].ljust(6, '0')
        microsecond = int(frac)

    dt = datetime(year, month, day, hour, minute, second, microsecond)
    aware = False
    tzseconds = 0

    if m.group(8):
        aware = True
        tz_str = m.group(8)
        if tz_str == 'Z':
            tzseconds = 0
        else:
            sign = 1 if tz_str[0] == '+' else -1
            tz_str = tz_str[1:].replace(':', '')
            tz_hours = int(tz_str[:2])
            tz_mins = int(tz_str[2:4]) if len(tz_str) >= 4 else 0
            tzseconds = sign * (tz_hours * 3600 + tz_mins * 60)

    return dt, aware, tzseconds


def parse_iso8601(date_string, assume_utc=False, as_utc=True, require_aware=False):
    if not date_string:
        return UNDEFINED_DATE
    dt, aware, tzseconds = _parse_iso8601_python(date_string)
    tz = utc_tz if assume_utc else local_tz
    if aware:  # timezone was specified
        if tzseconds == 0:
            tz = utc_tz
        else:
            sign = '-' if tzseconds < 0 else '+'
            description = f'{sign}{abs(tzseconds) // 3600:02}:{abs(tzseconds) % 3600 // 60:02}'
            tz = timezone(timedelta(seconds=tzseconds), description)
    elif require_aware:
        raise ValueError(f'{date_string} does not specify a time zone')
    dt = dt.replace(tzinfo=tz)
    if as_utc and tz is utc_tz:
        return dt
    return dt.astimezone(utc_tz if as_utc else local_tz)


if __name__ == '__main__':
    import sys
    print(parse_iso8601(sys.argv[-1]))
