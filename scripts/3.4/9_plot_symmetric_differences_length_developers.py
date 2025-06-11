"""
    We reproduce Figure 3.23 by considering the most frequent set as the base developer set, and plotting
    the lengths of the symmetric difference between each developer set and the base developer set. This plot is
    shown in Figure 3.29.

This script shows the construction of this plot.
"""


import duckdb
import matplotlib.pyplot as plt


bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']
members = "read_json_auto('../../data/members/*.json', union_by_name = true)"

QUERY = f"""
SELECT member_set AS "Members set", COUNT(*) AS "Appearances"
FROM (SELECT filename, GROUP_CONCAT(username ORDER BY username) AS member_set
      FROM {members}
      WHERE username NOT IN {bots}
        AND access_level = 30
      GROUP BY filename) AS project_members_sets
GROUP BY "Members set"
ORDER BY Appearances DESC
"""

result = duckdb.sql(QUERY).fetchall()

members_sets = []
base_set = None

N = max(r[1] for r in result)

for members_set, appearances in result:
    if appearances == N:
        base_set = set(members_set.split(','))
        break

if base_set is None:
    print(f"No base set found for appearances={N}")
    exit(1)

QUERY = f"""
SELECT member_set AS "Members set"
FROM (SELECT filename, GROUP_CONCAT(username ORDER BY username) AS member_set
      FROM {members}
      WHERE username NOT IN {bots}
        AND access_level = 30
      GROUP BY filename)
"""

result = duckdb.sql(QUERY).fetchall()

def jaccard_distance(A, B):
    A, B = set(A), set(B)
    intersection = A.intersection(B)
    union = A.union(B)
    if not union:
        return 0.0
    return 1 - len(intersection) / len(union)

differences = []
differences_lengths = []
max_symm_diff_value = 0
dj_total = 0

for members_set in result:
    current_set_members = set(members_set[0].split(','))
    difference = current_set_members.symmetric_difference(base_set)
    differences.append(difference)
    differences_lengths.append(len(difference))

differences_lengths = sorted(differences_lengths)

plt.figure(figsize=(10, 6))
plt.bar(range(len(differences_lengths)), differences_lengths)
plt.ylim(0, 300)
plt.xlabel('Index of developer set')
plt.ylabel('Symmetric difference length')
plt.grid(axis='y')
plt.tight_layout()
plt.savefig('out/9_1_base_set_developers_difference.png')