import duckdb
import matplotlib.pyplot as plt


bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']
members = "read_json_auto('../../data/members/*.json', union_by_name = true)"

QUERY = f"""
SELECT username,
       COUNT(CASE WHEN access_level = 20 THEN filename END) AS "Reporter",
       COUNT(CASE WHEN access_level = 30 THEN filename END) AS "Developer",
       COUNT(CASE WHEN access_level = 40 THEN filename END) AS "Maintainer",
       COUNT(CASE WHEN access_level = 50 THEN filename END) AS "Owner"
FROM {members}
WHERE username NOT IN {bots}
GROUP BY username
ORDER BY username
"""

results = duckdb.sql(QUERY).fetchall()

contributors = [row[0] for row in results]
counts_20 = [row[1] for row in results]
counts_30 = [row[2] for row in results]
counts_40 = [row[3] for row in results]
counts_50 = [row[4] for row in results]

fig, axs = plt.subplots(4, 1, figsize=(12, 9))

axs[0].bar(range(len(contributors)), counts_20)
axs[0].set_title('Number of projects for reporter')
axs[0].set_ylim(0, 257)
axs[0].set_xlabel('Contributors')
axs[0].set_ylabel(' ')

axs[1].bar(range(len(contributors)), counts_30)
axs[1].set_title('Number of projects for developer')
axs[1].set_ylim(0, 257)
axs[1].set_xlabel('Contributors')
axs[1].set_ylabel(' ')

axs[2].bar(range(len(contributors)), counts_40)
axs[2].set_title('Number of projects for maintainer')
axs[2].set_ylim(0, 257)
axs[2].set_xlabel('Contributors')
axs[2].set_ylabel(' ')

axs[3].bar(range(len(contributors)), counts_50)
axs[3].set_title('Number of projects for owner')
axs[3].set_ylim(0, 257)
axs[3].set_xlabel('Contributors')
axs[3].set_ylabel(' ')

fig.text(0.01, 0.48, 'Number of projects in which the member has the role', va='center', rotation='vertical', fontsize='medium')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('out/13_1_roles_distribution_per_user.png')
