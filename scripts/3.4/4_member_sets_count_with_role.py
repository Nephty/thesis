"""
    At this stage, we have no information on the role of each member within the member sets. To take this
    information into account, we modify the query shown in Figure 3.22 and add the access level of each member
    next to their username. Figure 3.24 presents this new query.

This script uses that queries and shows their results.
"""

import duckdb

members = "read_json_auto('../../data/members/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']

QUERY = f"""
SELECT appearances, COUNT(*), contributors
FROM (SELECT member_set, COUNT(*) appearances, contributors,
      FROM (SELECT filename, GROUP_CONCAT(CONCAT(username, access_level) ORDER BY username) member_set, COUNT(*) contributors
            FROM {members}
            WHERE username NOT IN {bots}
            GROUP BY 1)
      GROUP BY 1, 3
      ORDER BY 2 DESC)
GROUP BY 1, 3
ORDER BY 1 DESC, 3 DESC
"""

result = duckdb.sql(QUERY)
result.show()
