"""
   In order to understand maintainer dynamics within the GNOME
    ecosystem, we examine how many projects are maintained by contributors who hold the maintainer role in
    at least one project. This can be verified using the query shown in Figure 3.25.

This script uses that queries and shows their results.
"""

import duckdb

members = "read_json_auto('../../data/members/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']

QUERY = f"""
SELECT maintains, COUNT(*)
FROM (SELECT username, COUNT(*) maintains
      FROM {members}
      WHERE access_level = 40
      AND username NOT IN {bots}
      GROUP BY 1
      ORDER BY 2 DESC)
GROUP BY 1
ORDER BY 1 DESC
"""

result = duckdb.sql(QUERY)
result.show()
