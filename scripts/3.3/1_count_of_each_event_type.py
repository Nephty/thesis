"""
    To achieve this, we query the action_name field for each event, group the
    events by this field, and count how frequently each event type occurs. We then calculate the proportion of
    each event type and visualise the results using a pie chart. Event types that represent less than 1% of the
    events are grouped into in the “Other” category. Figure 3.11 presents the final query

This script uses that queries and shows their results.
"""

import duckdb
import matplotlib.pyplot as plt

events = "read_json_auto('../../data/events/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846']

QUERY = f"""
SELECT action_name, COUNT(*)
FROM {events}
WHERE author.username NOT IN {bots}
GROUP BY 1
ORDER BY 2 DESC
"""

result = duckdb.sql(QUERY)
result.show()

action_type, count = zip(*result.fetchall())

total = sum(count)
threshold = total * 0.01

filtered_labels = []
filtered_counts = []
other_count = 0

for label, value in zip(action_type, count):
    if value >= threshold:
        filtered_labels.append(label)
        filtered_counts.append(value)
    else:
        other_count += value

if other_count > 0:
    filtered_labels.append("Other")
    filtered_counts.append(other_count)

plt.figure(figsize=(10, 6))
plt.tight_layout()

wedges, texts, autotexts = plt.pie(
    filtered_counts, autopct='%1.1f%%', startangle=180,
    wedgeprops={'edgecolor': 'black'}, pctdistance=0.85, labeldistance=None,
    textprops={'fontsize': 10}
)

plt.legend(wedges, filtered_labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)
plt.gca().set_aspect('equal')

plt.savefig("out/1_1_event_types.png", bbox_inches="tight")

