import re
from datetime import (datetime, timedelta)

_time_re = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def _parse_hms_format(time_str):
    parts = _time_re.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

def _parse_colons_format(time_str):
    try:
        t = datetime.strptime(time_str ,"%H:%M:%S")
        return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    except ValueError:
        return None

def _parse_minutes(time_str):
    try:
        return timedelta(minutes=int(time_str))
    except ValueError, TypeError:
        return None

def parse_time(time_str):
    values = [f(time_str) for f in _parse_hms_format, _parse_colons_format, _parse_minutes]
    values = filter(None, values)

    return values[0] if len(values) else None

def format_timedelta(td):
    total_seconds = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    out = '%02dh' % hours if hours != 0 else ''

    out += '%02dm%02ds' % (minutes, seconds)

    return out
