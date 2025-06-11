"""
    An initial SQL query is used to count the number of projects. Figure 3.2 presents this query, which returns a total
    of 6,978 projects.

This script uses that query and shows its results.

The result is 6,975 and not 6,978 because, as specified in Section 3.2.3 :

    In addition, three projects were archived after the dataset was retrieved but prior to the collection
    of information regarding role assignments. As archiving removes most project members, these projects cannot
    be used for contributor-based comparisons and are therefore excluded from further analysis. These projects
    are entirely removed from the dataset.
"""

import duckdb

projects = "read_json_auto('../../data/projects.json')"

QUERY = f"""
SELECT COUNT(*)
FROM {projects}
"""

duckdb.sql(QUERY).show()
