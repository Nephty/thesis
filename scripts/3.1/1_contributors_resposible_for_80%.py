"""
    We examine at the contributors who are collectively responsible for 80% of the events of the ecosystem,
    amounting to 73 contributors.

This script prints a list of usernames of contributors who are, together, responsible for 80% of the events of the ecosystem.
"""

import duckdb

events = "read_json_auto('../../data/events/*.json', filename = true, union_by_name = true)"

QUERY = f"""
WITH contributor_events AS (
  SELECT
    author.username AS contributor,
    COUNT(*) AS events
  FROM {events}
    WHERE action_name IN ['pushed to', 'pushed new', 'deleted', 'accepted', 'approved', 'closed']
  GROUP BY contributor
),
total_events AS (
  SELECT SUM(events) AS total FROM contributor_events
),
ranked_contributors AS (
  SELECT
    contributor,
    events,
    SUM(events) OVER (ORDER BY events DESC, contributor) AS cumulative_events,
    SUM(events) OVER (ORDER BY events DESC, contributor) * 1.0 / (SELECT total FROM total_events) AS cumulative_percent,
    ROW_NUMBER() OVER (ORDER BY events DESC, contributor) AS row_num
  FROM contributor_events
),
below_80 AS (
  SELECT * FROM ranked_contributors WHERE cumulative_percent < 0.9
),
first_above_80 AS (
  SELECT * FROM ranked_contributors
  WHERE cumulative_percent >= 0.9
  ORDER BY row_num
  LIMIT 1
),
resulting_data AS (
SELECT * FROM below_80
UNION ALL
SELECT * FROM first_above_80
)
SELECT contributor FROM resulting_data
"""

unique_contributors = [res[0] for res in duckdb.sql(QUERY).fetchall()]
print(unique_contributors)
