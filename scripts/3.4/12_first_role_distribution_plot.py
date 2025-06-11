"""
    The data of the plots is retrieved with a single query that counts the number of projects in which each
    member has each role. This query is shown in Figure 3.32. The four constructed plots are combined in a
    single visualisation, shown in Figure 3.33.

This script presents this query and its related plot.
"""


import duckdb
import matplotlib.pyplot as plt
from collections import Counter


bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']
members = "read_json_auto('../../data/members/*.json', union_by_name = true)"

QUERY = f"""
SELECT username,
    COUNT(CASE WHEN access_level = 20 THEN filename END) AS reporter,
    COUNT(CASE WHEN access_level = 30 THEN filename END) AS developer,
    COUNT(CASE WHEN access_level = 40 THEN filename END) AS maintainer,
    COUNT(CASE WHEN access_level = 50 THEN filename END) AS owner
    FROM {members}
WHERE username NOT IN {bots}
GROUP BY 1
ORDER BY 1
"""

results = duckdb.sql(QUERY).fetchall()

counts_20 = [row[1] for row in results]
counts_30 = [row[2] for row in results]
counts_40 = [row[3] for row in results]
counts_50 = [row[4] for row in results]

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

reporter_counts = Counter(counts_20)
x = sorted(reporter_counts)
y = [reporter_counts[i] for i in x]
axs[0, 0].bar(x, y, edgecolor='black')
axs[0, 0].set_title('Distribution of reporters')
axs[0, 0].set_xlabel('Number of projects')
axs[0, 0].set_ylabel('Number of members having this role')

developer_counts = Counter(counts_30)
x = sorted(developer_counts)
y = [developer_counts[i] for i in x]
axs[0, 1].bar(x, y, edgecolor='black')
axs[0, 1].set_title('Distribution of developers')
axs[0, 1].set_xlabel('Number of projects')
axs[0, 1].set_ylabel('Number of members having this role')

maintainer_counts = Counter(counts_40)
x = sorted(maintainer_counts)
y = [maintainer_counts[i] for i in x]
axs[1, 0].bar(x, y, edgecolor='black')
axs[1, 0].set_xticks(x)
axs[1, 0].set_title('Distribution of maintainers')
axs[1, 0].set_xlabel('Number of projects')
axs[1, 0].set_ylabel('Number of members having this role')

owner_counts = Counter(counts_50)
x = sorted(owner_counts)
y = [owner_counts[i] for i in x]
axs[1, 1].bar(x, y, edgecolor='black')
axs[1, 1].set_title('Distribution of owners')
axs[1, 1].set_xlabel('Number of projects')
axs[1, 1].set_ylabel('Number of members having this role')

plt.tight_layout()
plt.savefig('out/12_1_roles_distribution_frequency.png')

