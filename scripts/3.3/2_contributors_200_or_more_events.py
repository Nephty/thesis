"""
    The highest individual contribution, consisting of 2049 events, was achieved by matthiasc. Although this
    number is quite high, only 41 contributors have generated 200 or more events. This represents approximately
    1.68% of the contributors.

This script demonstrates these numbers.
"""

import duckdb

events = "read_json_auto('../../data/events/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846']

QUERY = f"""
SELECT author.username, COUNT(*) cnt,
    CASE 
        WHEN author.username IN {bots} THEN 'bot'
        ELSE 'not bot'
    END AS user_type
FROM {events}
GROUP BY 1
HAVING COUNT(*) >= 200
ORDER BY 3, 2 DESC
"""

result = duckdb.sql(QUERY)
result.show()
