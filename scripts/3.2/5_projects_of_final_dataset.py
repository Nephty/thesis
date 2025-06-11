"""
    Consequently, the final dataset comprises 254 projects. Figure 3.10
    shows the SQL query used to identify projects that satisfy both the GNOME namespace condition and the
    relaxed activity requirement.

This script uses that queries and shows their results.

The result is 259 and not 254 because, as specified in Section 3.2.3 :

    However, five of these 262 projects, while part of the GNOME
    namespace and having their last recorded activity on or after 00:00:00 on October 1st, 2024, did not exhibit
    any activity during the reference time period.

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
WHERE namespace.name = 'GNOME'
AND last_activity_at >= '2024-10-01T00:00:00'
"""

duckdb.sql(QUERY).show()



