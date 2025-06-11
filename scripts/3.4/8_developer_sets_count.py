"""
    First, we create a query to count the number of projects in which a contributor has the developer role.
    We then wrap this query in another query that counts the number of contributors with the developer role
    on a given number of projects. This query is similar to that used in Figure 3.26 and is shown in Figure 3.27.

This script uses that queries and shows their results.
"""

import duckdb

members = "read_json_auto('../../data/members/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']

QUERY = f"""
SELECT appearances, COUNT(*), contributors
FROM (SELECT member_set, COUNT(*) appearances, contributors,
      FROM (SELECT filename, GROUP_CONCAT(username ORDER BY username) member_set, COUNT(*) contributors
            FROM {members}
            WHERE username NOT IN {bots}
              AND access_level = 30
            GROUP BY 1)
      GROUP BY 1, 3
      ORDER BY 2 DESC)
GROUP BY 1, 3
ORDER BY 1 DESC, 3 DESC
"""

result = duckdb.sql(QUERY)
result.show()
