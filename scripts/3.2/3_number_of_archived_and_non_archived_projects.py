"""
    We construct a query that extracts the month and year of the most recent activity for each project. The
    results are grouped by this value, and the SUM function is used in combination with a CASE statement to count
    the number of projects associated with the Archive namespace, as well as those that are not.

This script uses that queries and shows their results.
"""

import duckdb
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

projects = "read_json_auto('../../data/projects.json')"

QUERY = f"""
SELECT strftime('%Y-%m', CAST(last_activity_at AS TIMESTAMP)),
SUM(CASE WHEN namespace.name = 'Archive' THEN 1 ELSE 0 END),
SUM(CASE WHEN namespace.name != 'Archive' THEN 1 ELSE 0 END)
FROM {projects}
GROUP BY 1
ORDER BY 1
"""

result = duckdb.sql(QUERY)
result.show()

time_stamps, archived_projects, non_archived_projects = zip(*result.fetchall())
time_stamps = [datetime.strptime(ts, '%Y-%m') for ts in time_stamps]

total_projects = [archived + non_archived for archived, non_archived in zip(archived_projects, non_archived_projects)]

plt.figure(figsize=(12, 8))

plt.bar(time_stamps, archived_projects, width=20, color='tomato', label='Archived projects')
plt.bar(time_stamps, non_archived_projects, width=20, bottom=archived_projects, label='Non-archived projects')

plt.xlabel('Time')
plt.ylabel('Number of projects')
plt.ylim(0, max(total_projects) * 1.05)
plt.title('Last recorded activity of projects over time (monthly)')
plt.legend(loc='upper right')
plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=30)

plt.tight_layout()
plt.savefig("out/3_1_last_activity_monthly_archive_ratio.png")
