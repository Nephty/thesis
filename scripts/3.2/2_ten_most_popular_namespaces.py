"""
    First, we construct an SQL query to retrieve the namespace name of each project in the dataset and
    count the number of times each name occurs. Figure 3.3 presents the final query, which groups the records
    by namespace to apply the COUNT function and selects the ten largest namespaces.

    The Archive namespace contains deprecated
    projects that are no longer actively maintained. Therefore, we exclude it by adding a WHERE clause to the
    query. This updated query is presented in Figure 3.4.

This script uses both queries and shows their results.
"""

import duckdb, re
import matplotlib.pyplot as plt

def sanitize_text(text):
    return re.sub(r'[^\x00-\x7F]', '?', text)

projects = "read_json_auto('../../data/projects.json')"

QUERY = f"""
SELECT namespace.name, COUNT(*)
FROM {projects}
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10
"""

result = duckdb.sql(QUERY)
result.show()

sanitized_result = [(sanitize_text(name), count) for name, count in result.fetchall()]
namespaces, _projects = zip(*sanitized_result)
plt.figure(figsize=(12, 8))
plt.bar(namespaces, _projects)
plt.xlabel('Namespaces')
plt.ylabel('Number of projects in namespace')
plt.tight_layout()
plt.xticks(rotation=30)
plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.savefig("out/2_1_namespaces_projects_count.png")

QUERY = f"""
SELECT namespace.name, COUNT(*)
FROM {projects}
WHERE namespace.name != 'Archive'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10
"""

result = duckdb.sql(QUERY)
result.show()

sanitized_result = [(sanitize_text(name), count) for name, count in result.fetchall()]
namespaces, _projects = zip(*sanitized_result)
plt.figure(figsize=(12, 8))
plt.bar(namespaces, _projects)
plt.xlabel('Namespaces')
plt.ylabel('Number of projects in namespace')
plt.tight_layout()
plt.xticks(rotation=30)
plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.savefig("out/2_2_namespaces_projects_count_without_archive.png")
