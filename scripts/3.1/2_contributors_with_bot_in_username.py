"""
    Additionally, we retrieve the profiles of all users whose name contains “bot”.

This script prints a list of usernames of contributors who have 'bot' in their username and were not found with the
previous technique.
"""

import duckdb

events = "read_json_auto('../../data/events/*.json', filename = true, union_by_name = true)"
previously_found_bots = ['translations', 'marge-bot', 'gnome-build-meta-bot']

QUERY = f"""
SELECT DISTINCT author.username
FROM {events}
WHERE 'bot' IN author.username
AND author.username NOT IN {previously_found_bots}
"""

bots = [res[0] for res in duckdb.sql(QUERY).fetchall()]
print(bots)
