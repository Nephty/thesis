"""
    Potential forks can be identified by locating user-namespaced projects that
    share a name with an official GNOME project, were created after the original project, and are not themselves
    part of the GNOME namespace. An estimate of the number of such forks is obtained using the query shown
    in Figure 3.9, which returns 1,634 potential forks.

This script uses demonstrates that number of projects.
"""

import duckdb

projects = "read_json_auto('../../data/projects.json')"

QUERY = f"""
SELECT fork.id, fork.name_with_namespace, fork.created_at, original.name_with_namespace, original.created_at
FROM {projects} fork
JOIN {projects} original
ON fork.name = original.name
AND original.namespace.name = 'GNOME' AND fork.namespace.name != 'GNOME'
AND fork.created_at > original.created_at AND original.forks_count > 0
"""

duckdb.sql(QUERY).show()
