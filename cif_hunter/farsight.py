import logging
import os
import arrow
import re
from pprint import pprint
from csirtg_indicator import Indicator
from csirtg_dnsdb.client import Client
from csirtg_dnsdb.exceptions import QuotaLimit
import os
ENABLED = os.getenv('CIF_HUNTER_ADVANCED', False)

TOKEN = os.environ.get('FARSIGHT_TOKEN')
PROVIDER = os.environ.get('FARSIGHT_PROVIDER', 'dnsdb.info')
MAX_QUERY_RESULTS = os.environ.get('FARSIGHT_QUERY_MAX', 10000)
CLIENT = Client()

logger = logging.getLogger(__name__)


def process(i):
    if not ENABLED and not TOKEN:
        return

    if i.itype != 'ipv4':
        return

    if 'search' not in i.tags:
        return

    if i.confidence and i.confidence < 9:
        return

    if re.search('^(\S+)\/(\d+)$', i.indicator):
        return

    max = MAX_QUERY_RESULTS
    rv = []

    try:
        for r in CLIENT.search(i.indicator):
            first = arrow.get(r.get('time_first') or r.get('zone_time_first'))
            first = first.datetime
            last = arrow.get(r.get('time_last') or r.get('zone_time_last'))
            last = last.datetime

            reporttime = arrow.utcnow().datetime

            r['rrname'] = r['rrname'].rstrip('.')

            ii = Indicator(
                indicator=r['rdata'],
                rdata=r['rrname'].rstrip('.'),
                count=r['count'],
                tags='pdns',
                confidence=10,
                firsttime=first,
                lasttime=last,
                reporttime=reporttime,
                provider=PROVIDER,
                tlp='amber',
                group='everyone'
            )

            rv.append(ii)
            max -= 1
            if max == 0:
                break

    except QuotaLimit:
        logger.warn('farsight quota limit reached... skipping')
    except Exception as e:
        logger.exception(e)
        return

    return rv
