"""
    As demonstrated by the query shown in Figure 3.20, there are four
    owners who happen to own all projects.

This script uses that queries and shows their results.
"""

import duckdb

members = "read_json_auto('../../data/members/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846']

QUERY = f"""
SELECT username, COUNT(*)
FROM {members}
WHERE access_level = 50
GROUP BY 1
ORDER BY 2
"""

result = duckdb.sql(QUERY)
result.show()
