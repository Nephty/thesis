"""
    We consider the proportion of some types of events based on the contributors’ activity level, but we refine the
    selection of event types and incorporate the target_type field. We also do not group event type shares of
    less than 1% into an “Other” category. We generate a plot displaying opened and closed events, broken
    down by their respective target_type. The resulting visualisation is shown in Figure 3.16.

This script demonstrates the construction of these plots.
"""

import duckdb

events = "read_json_auto('../../data/events/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846']

QUERY = f"""
SELECT DISTINCT e1.author.username, e1.action_name, e1.target_type, e2.total_events
FROM {events} AS e1
JOIN (SELECT author.username, COUNT(*) as total_events
      FROM {events}
      GROUP BY author.username) AS e2
ON e1.author.username = e2.username
WHERE e1.action_name = 'opened' AND (e1.target_type = 'Milestone' or e1.target_type = 'WorkItem')
AND author_username NOT IN {bots}
ORDER BY 4
"""

duckdb.sql(QUERY).show()
