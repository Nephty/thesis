"""
This script contains all data extraction and creation of plots used in Section 3.5.
"""

import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from scipy.stats import spearmanr

READ_MATRICES_FROM_FILES = True

bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846', 'triage-bot', 'project_1_bot', 'gitlab-bot', 'project_665_bot_ed35143b338162a6e4c732a336a3c600']
events = "read_json_auto('../../data/events/*.json', union_by_name = true)"
members = "read_json_auto('../../data/members/*.json', union_by_name = true)"

time_slices = [
    ("2024-10-01", "2024-10-07"),
    ("2024-10-08", "2024-10-14"),
    ("2024-10-15", "2024-10-21"),
    ("2024-10-22", "2024-10-28"),
    ("2024-10-29", "2024-11-04"),
    ("2024-11-05", "2024-11-11"),
    ("2024-11-12", "2024-11-18"),
    ("2024-11-19", "2024-11-25"),
    ("2024-11-26", "2024-12-02"),
    ("2024-12-03", "2024-12-09"),
    ("2024-12-10", "2024-12-16"),
    ("2024-12-17", "2024-12-23"),
    ("2024-12-24", "2024-12-30")
]

core_developers = None

if not READ_MATRICES_FROM_FILES:
    core_developers = {time_slice: [] for time_slice in time_slices}

    for start_date, end_date in tqdm(time_slices):
        QUERY = f"""
        SELECT 
            events.author.username,
            COUNT(*) AS event_count
        FROM {events} events
        WHERE events.action_name IN ['pushed to', 'pushed new', 'deleted', 'accepted', 'approved', 'closed']
        AND events.created_at >= '{start_date} 00:00:00' 
        AND events.created_at <= '{end_date} 23:59:59'
        AND author.username NOT IN {bots}
        GROUP BY events.author.username
        ORDER BY event_count DESC, events.author.username
        LIMIT 37
        """
        core_developers[(start_date, end_date)] = duckdb.sql(QUERY).fetchall()

    teams_activity = {}  # { team_0: { period_0: total_events, period_1: total_events }, team_1: { period_0: total_events, period_1: total_events } }

    for team_number, time_slice in enumerate(core_developers):
        team = [core_developers[time_slice][i][0] for i in range(len(core_developers[time_slice]))]

        activity = []
        for start_date, end_date in tqdm(time_slices):
            QUERY = f"""
            SELECT events.author.username,
                   COUNT(*) AS event_count
            FROM {events} events
            WHERE events.action_name IN ['pushed to', 'pushed new', 'deleted', 'accepted', 'approved', 'closed']
            AND events.author.username IN {team}
            AND events.created_at >= '{start_date} 00:00:00' 
            AND events.created_at <= '{end_date} 23:59:59'
            AND author.username NOT IN {bots}
            GROUP BY events.author.username
            ORDER BY events.author.username DESC, events.author.username
            """
            activity.append(duckdb.sql(QUERY).fetchall())

        teams_activity[team_number] = {(start_date, end_date): activity[i] for i, (start_date, end_date) in
                                       enumerate(time_slices)}

    absolute_matrix = []  # (x, y) = number of events by team x in period y

    for time_slice in time_slices:
        absolute_line = []
        for team_number in teams_activity:
            total_events_in_current_period_for_team = sum(
                number_of_events for _, number_of_events in teams_activity[team_number][time_slice])
            absolute_line.append(total_events_in_current_period_for_team)
        absolute_matrix.append(absolute_line)

    total_events_of_teams = {i: sum(absolute_matrix[line][i] for line in range(len(absolute_matrix))) for i in
                             range(len(absolute_matrix))}

    normalized_matrix = []  # absolute matrix but each value is divided by the total of its row

    for time_slice_index, time_slice in enumerate(time_slices):
        normalized_line = []
        for team_number in teams_activity:
            normalized_line.append(absolute_matrix[time_slice_index][team_number] / sum(absolute_matrix[time_slice_index]))
        normalized_matrix.append(normalized_line)

    with open('out/core-developers-teams-activity.txt', 'w') as f:
        f.write(f"{teams_activity}")

    with open('out/core-developers-absolute-matrix.txt', 'w') as f:
        f.write(f"{absolute_matrix}")

    with open('out/core-developers-normalized-matrix.txt', 'w') as f:
        f.write(f"{normalized_matrix}")
else:
    with open('out/core-developers-teams-activity.txt', 'r') as f:
        teams_activity = eval(f.readline().strip())

    with open('out/core-developers-absolute-matrix.txt', 'r') as f:
        absolute_matrix = eval(f.readline().strip())

    with open('out/core-developers-normalized-matrix.txt', 'r') as f:
        normalized_matrix = eval(f.readline().strip())


if core_developers is None:
    core_developers = {time_slice: [] for time_slice in time_slices}

    for start_date, end_date in tqdm(time_slices):
        QUERY = f"""
        SELECT 
            events.author.username,
            COUNT(*) AS event_count
        FROM {events} events
        WHERE events.action_name IN ['pushed to', 'pushed new', 'deleted', 'accepted', 'approved', 'closed']
        AND events.created_at >= '{start_date} 00:00:00' 
        AND events.created_at <= '{end_date} 23:59:59'
        AND author.username NOT IN {bots}
        GROUP BY events.author.username
        ORDER BY event_count DESC, events.author.username
        LIMIT 30
        """
        core_developers[(start_date, end_date)] = duckdb.sql(QUERY).fetchall()

core_developers_names = set()
for time_slice in core_developers:
    core_developers_names = core_developers_names.union(set(pair[0] for pair in core_developers[time_slice]))
core_developers_names = list(core_developers_names)


# THREE LINE PLOTS
time_periods = [f"{i+1}" for i, (start, end) in enumerate(time_slices)]
team_labels = [f"Team {i+1}" for i in range(len(teams_activity))]
colors = plt.cm.get_cmap('cool', len(teams_activity))

fig, axs = plt.subplots(3, 1, figsize=(12, 18))

for team_number in teams_activity:
    axs[0].plot(time_periods, [absolute_matrix[i][team_number] for i in range(len(absolute_matrix))],
                marker='o', label=team_labels[team_number], color=colors(team_number))

axs[0].set_title('Number of events per team over time periods')
axs[0].set_xticklabels([i + 1 for i in range(len(absolute_matrix))])
axs[0].set_xlabel('Time period')
axs[0].set_ylabel('Number of events')
axs[0].set_ylim(0, 1200)
axs[0].legend(loc='upper left', bbox_to_anchor=(1, 1), title="Teams")
axs[0].grid()

for team_number in teams_activity:
    cumulative_data = [sum(absolute_matrix[j][team_number] for j in range(i + 1)) for i in range(len(absolute_matrix))]
    axs[1].plot(time_periods, cumulative_data, marker='o', label=team_labels[team_number], color=colors(team_number))

axs[1].set_title('Cumulative number of events per team over time periods')
axs[1].set_xticklabels([i + 1 for i in range(len(absolute_matrix))])
axs[1].set_xlabel('Time period')
axs[1].set_ylabel('Cumulative number of events')
axs[1].set_ylim(0, 10000)
axs[1].legend(loc='upper left', bbox_to_anchor=(1, 1), title="Teams")
axs[1].grid()

for team_number in teams_activity:
    axs[2].plot(time_periods, [normalized_matrix[i][team_number] for i in range(len(normalized_matrix))],
                marker='o', label=team_labels[team_number], color=colors(team_number))

axs[2].set_title('Normalized number of events per team over time periods')
axs[2].set_xticklabels([i + 1 for i in range(len(normalized_matrix))])
axs[2].set_xlabel('Time period')
axs[2].set_ylabel('Normalized number of events')
axs[2].set_ylim(0, 0.15)  # Adjust this based on the normalization range
axs[2].legend(loc='upper left', bbox_to_anchor=(1, 1), title="Teams")
axs[2].grid()

plt.tight_layout()
plt.savefig('out/1_1_core_developers_teams_events_count_three_line_plots.png')

team_evolution_matrix: list[list[int or float or None]] = [[None for _ in range(len(absolute_matrix))] for _ in range(len(absolute_matrix))]  # absolute matrix but each value is normalized between 0 and 1 for its team (from min(line), max(line))
normalized_for_all_teams_matrix: list[list[int or float or None]] = [[None for _ in range(len(absolute_matrix))] for _ in range(len(absolute_matrix))]  # absolute matrix but each value is normalized between 0 and 1 for the entire matrix

flattened_absolute_matrix = [item for sublist in absolute_matrix for item in sublist]
global_min, global_max = min(flattened_absolute_matrix), max(flattened_absolute_matrix)
for row_index in range(len(absolute_matrix)):
    for row in range(len(absolute_matrix)):
        local_min, local_max = 0, max(_row[row_index] for _row in absolute_matrix)
        value = absolute_matrix[row][row_index]
        team_evolution_matrix[row][row_index] = (value - local_min) / (local_max - local_min)
        normalized_for_all_teams_matrix[row][row_index] = (value - global_min) / (global_max - global_min)


plt.figure(figsize=(12, 8))
sns.heatmap(absolute_matrix,
            annot=True,
            fmt='g',
            cmap='gray_r',
            vmin=0,
            xticklabels=[f"Team {i+1}" for i in range(len(teams_activity))],
            yticklabels=[f"Period {i+1}" for i in range(len(time_slices))],
            cbar_kws={'label': 'Number of events'})

plt.xlabel('Time periods')
plt.ylabel('Teams')
plt.tight_layout()
plt.savefig('out/1_2_absolute_matrix.png')

plt.figure(figsize=(12, 8))
sns.heatmap(normalized_matrix,
            annot=True,
            fmt=".2f",
            cmap='gray_r',
            vmin=0,
            xticklabels=[f"Team {i+1}" for i in range(len(teams_activity))],
            yticklabels=[f"Period {i+1}" for i in range(len(time_slices))],
            cbar_kws={'label': 'Number of events'})

plt.xlabel('Time periods')
plt.ylabel('Teams')
plt.tight_layout()
plt.savefig('out/1_3_normalized_matrix.png')

plt.figure(figsize=(12, 8))
sns.heatmap(team_evolution_matrix,
            annot=True,
            fmt=".2f",
            cmap='gray_r',
            vmin=0,
            xticklabels=[f"Team {i+1}" for i in range(len(teams_activity))],
            yticklabels=[f"Period {i+1}" for i in range(len(time_slices))],
            cbar_kws={'label': 'Number of events'})

plt.xlabel('Time periods')
plt.ylabel('Teams')
plt.tight_layout()
plt.savefig('out/1_4_team_evolution_matrix.png')

num_teams = len(absolute_matrix[0])
spearmans = [[float('inf') for _ in range(num_teams)] for _ in range(num_teams)]
p_values_spearman = [[float('inf') for _ in range(num_teams)] for _ in range(num_teams)]

for i in range(num_teams):
    for j in range(i, num_teams):
        team_i_activity = [absolute_matrix[time_slice_index][i] for time_slice_index in range(len(absolute_matrix))]
        team_j_activity = [absolute_matrix[time_slice_index][j] for time_slice_index in range(len(absolute_matrix))]

        spearman_coefficient, p_value_s = spearmanr(team_i_activity, team_j_activity)
        spearmans[i][j] = spearman_coefficient
        spearmans[j][i] = spearman_coefficient
        p_values_spearman[i][j] = p_value_s
        p_values_spearman[j][i] = p_value_s


def correct_p_vals_holm_bonferroni(p_values):
    p_values_with_index = [(i, p_values[i]) for i in range(len(p_values))]
    sorted_p_values = sorted(p_values_with_index, key=lambda x: x[1])
    corrected_p_values = []
    for i, p_value in sorted_p_values:
        corrected_p_values.append((i, p_value * (len(p_values) + 1 - (i + 1))))
    return [p[1] for p in sorted(corrected_p_values, key=lambda x: x[0])]


# SPEARMAN
team_pairs = [f"{i}-{i+1}" for i in range(1, num_teams)]
spearman_coeffs = [spearmans[i][i+1] for i in range(num_teams - 1)]
spearman_pvals = [p_values_spearman[i][i+1] for i in range(num_teams - 1)]
alpha = 0.05
corrected_p_vals = correct_p_vals_holm_bonferroni(spearman_pvals)
fig, ax1 = plt.subplots(figsize=(14, 6))
x = list(range(len(team_pairs)))
width = 0.5
ax1.bar(x, spearman_coeffs, width=width, label='Spearman coefficient', color='lightgreen')
ax1.set_ylabel('Spearman correlation coefficient')
ax1.set_xlabel('Team pairs')
ax1.set_title('Spearman correlation coefficients and p-values for consecutive team pairs')
ax1.set_xticks(x)
ax1.set_xticklabels(team_pairs)
ax1.set_ylim(0, 1.05)
ax1.plot(x, corrected_p_vals, marker='s', linestyle='--', color='green', label='p-value, corrected with Holm-Bonferroni')
ax1.axhline(alpha, color='red', linestyle='dotted', linewidth=1)
ax1.text(-0.83, alpha + 0.005, f'α = {alpha}', color='red', fontsize=10)
ax1.axhline(min(spearman_coeffs), color='gray', linestyle='dotted', linewidth=1)
ax1.text(-0.83, min(spearman_coeffs) + 0.005, f'{round(min(spearman_coeffs), 3)}', color='gray', fontsize=10)
handles1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(handles1[::-1], labels1[::-1], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
plt.tight_layout()
plt.savefig('out/1_5_pearson_for_consecutive_teams.png')
plt.close()


# TURNOVER
teams = []
for team_activity in core_developers.values():
    team = set()
    for username, _ in team_activity:
        team.add(username)
    teams.append(team)
turnover = []
for team_index in range(len(teams) - 1):
    team_A = teams[team_index]
    team_B = teams[team_index + 1]
    turnover.append(len(team_A - team_B) / 37)
fig, ax1 = plt.subplots(figsize=(14, 6))
x = list(range(len(turnover)))
width = 0.5
ax1.bar(x, turnover, width=width, label='Turnover rate', color='red')
ax1.bar(x, [1 - t for t in turnover], width=width, bottom=turnover, label='Remaining rate', color='lightgreen')
ax1.set_ylabel('Rate')
ax1.set_xlabel('Team pairs')
ax1.set_xticks(x)
ax1.set_xticklabels(team_pairs)
ax1.set_ylim(0, 1.05)
ax1.axhline(min(turnover), color='gray', linestyle='dotted', linewidth=1)
ax1.text(-0.83, min(turnover) + 0.005, f'{round(min(turnover), 3)}', color='gray', fontsize=10)
ax1.text(12 - 0.5, min(turnover) + 0.005, f'{round(min(turnover) * 37)}', color='gray', fontsize=10)
ax1.axhline(max(turnover), color='gray', linestyle='dotted', linewidth=1)
ax1.text(-0.83, max(turnover) + 0.005, f'{round(max(turnover), 3)}', color='gray', fontsize=10)
ax1.text(12 - 0.5, max(turnover) + 0.005, f'{round(max(turnover) * 37)}', color='gray', fontsize=10)
ax2 = ax1.twinx()
ax2.set_ylabel('Number of contributors')
ax2.set_ylim(0, 37 * 1.05)
ax2.set_yticks(range(0, 38, 5))
handles1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(handles1[::-1], labels1[::-1], loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
plt.tight_layout()
plt.savefig('out/1_6_turnover_rates.png')
plt.close()


# ROLE DISTRIBUTION
QUERY = f"""
WITH user_roles AS (
    SELECT 
        username,
        MAX(CASE WHEN access_level = 40 THEN 1 ELSE 0 END) AS has_maintainer,
        MAX(CASE WHEN access_level = 30 THEN 1 ELSE 0 END) AS has_developer
    FROM {members}
    GROUP BY username
)
SELECT 
    author.username,
    COUNT(*) AS cnt,
    CASE 
        WHEN user_roles.has_maintainer = 1 THEN 'Maintainer'
        WHEN user_roles.has_developer = 1 THEN 'Developer'
        ELSE 'Contributor'
    END AS role
FROM {events} events
LEFT JOIN user_roles user_roles ON events.author.username = user_roles.username
WHERE author.username IN {core_developers_names}
GROUP BY author.username, user_roles.has_maintainer, user_roles.has_developer
ORDER BY cnt
"""

result = duckdb.sql(QUERY)
result = result.fetchall()

role_counts = {
    'Maintainer': 0,
    'Developer': 0,
    'Contributor': 0
}

for _, _, role in result:
    if role in role_counts:
        role_counts[role] += 1

total = len(result)

roles = list(role_counts.keys())
counts = [cnt / total for cnt in role_counts.values()]

plt.figure(figsize=(5, 5))
bars = plt.bar(roles, counts, color=[(0.15294117647058825, 0.39215686274509803, 0.09803921568627451), (0.5568627450980392, 0.00392156862745098, 0.3215686274509804), 'turquoise'])
plt.xlabel('Role')
plt.ylabel('Count')
plt.ylim(0, 1)
plt.grid(axis='y')

for bar, count in zip(bars, counts):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
             f'{100*count:.2f}%', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('out/1_7_role_distribution_in_core_developers')