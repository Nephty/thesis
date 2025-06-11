"""
    We start by creating a basic SQL query to read the name of the author and the type of each considered
    event. This query is shown in Figure 3.13. Once we have retrieved this information, we compute the share
    that each event type represents for each level of activity. In other words, we consider all contributors who
    have generated n events and calculate the proportion that each event type represents ∀ n ∈ [1, 200]. After
    that, we group all shares that are less than 1% in an “Other” category. Using this data, we create two plots:
    one that shows the three most represented event types (commented on, pushed to and opened), and one that
    shows the next five most represented event types (closed, accepted, pushed new, deleted and approved)
    event types. The plots are separated is made for better readability. Figure 3.14 shows the first plot with two
    moving averages: one with a window size of 20 and another with a window size of 50. Figure 3.15 shows the
    second plot with a moving average with a window size of 50.

This script demonstrates the construction of these plots.
"""

import duckdb
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

events = "read_json_auto('../../data/events/*.json', union_by_name = true)"
bots = ['marge-bot', 'translations', 'gnome-build-meta-bot', 'support-bot', 'project_16754_bot_2b6da7b077af381b7f45e5a10781e7db', 'project_25833_bot_a55d157583ed16b001006899b37d7846']

QUERY = f"""
SELECT author.username, action_name
FROM {events}
WHERE author.username NOT IN {bots}
"""

result = duckdb.sql(QUERY)
result.show()


class MovingAverage:
    def __init__(self, initial_window_size: int = 50, split_moving_average: bool = False, splitting_point: int = 200, new_window_size: int = 100, plot_raw_data: bool = False, alpha: float = 1):
        self.initial_window_size = initial_window_size
        self.split_moving_average = split_moving_average
        self.splitting_point = splitting_point
        self.new_window_size = new_window_size
        self.plot_raw_data = plot_raw_data
        self.alpha = alpha


OPERATION = int.__ge__
X_MIN = 1
X_MAX = 200
Y_MIN = 0
MAIN_Y_MAX = 100
OTHER_Y_MAX = 14
X_LINES = [10]
MAIN_Y_TICKS_STEP = 10
OTHER_Y_TICKS_STEP = 2
WINDOW_SIZE = 20
MAIN_PLOT_WINDOW_SIZES = [MovingAverage(50, False, 200, 50, False), MovingAverage(20, False, 200, 20, False, alpha=0.5)]
OTHER_PLOT_WINDOW_SIZES = [MovingAverage(50, False, 200, 50, False)]
SPLIT_LEGEND = False
MAIN_PLOT_METHOD = "selection"
MAIN_PLOT_SELECTION = ["commented on", "pushed to", "opened"]
OTHER_MAIN_PLOT_SELECTION = ["closed", "accepted", "pushed new", "approved", "deleted"]
events_count_threshold = range(X_MIN, X_MAX + 1, 1)


def moving_average(data, window_size):
    moving_averages = []
    for i in range(len(data)):
        window = data[max(0, i - window_size + 1):i + 1]
        non_zero_window = [x for x in window if x != 0]
        if non_zero_window:
            moving_average = sum(non_zero_window) / len(non_zero_window)
        else:
            moving_average = 0
        moving_averages.append(moving_average)
    return moving_averages

QUERY = f"""
SELECT 
    author.username,
    action_name AS "Event type"
FROM {events}
WHERE author.username NOT IN {bots}
"""

result = duckdb.sql(QUERY).fetchall()

user_actions_count = {}
for username, action_name in result:
    if username not in user_actions_count:
        user_actions_count[username] = {}
    if action_name not in user_actions_count[username]:
        user_actions_count[username][action_name] = 0
    user_actions_count[username][action_name] += 1

shares_dict = {}

index = 0
for threshold in tqdm(events_count_threshold):

    filtered_user_actions_count = {username: actions for username, actions in user_actions_count.items() if sum(actions.values()) == threshold}

    action_count = {}
    for actions in filtered_user_actions_count.values():
        for action_name, count in actions.items():
            if action_name not in action_count:
                action_count[action_name] = 0
            action_count[action_name] += count

    total_count = sum(action_count.values())
    for action_name, count in action_count.items():
        share = (count / total_count) * 100 if total_count > 0 else 0
        if action_name not in shares_dict:
            shares_dict[action_name] = [0] * len(events_count_threshold)
        shares_dict[action_name][index] = share
    index += 1

grouped_shares_dict = {}
for action_name, shares in shares_dict.items():
    if all(share < 1 for share in shares):
        if "Other" not in grouped_shares_dict:
            grouped_shares_dict["Other"] = [0] * len(events_count_threshold)
        for i in range(len(events_count_threshold)):
            grouped_shares_dict["Other"][i] += shares[i]
    else:
        grouped_shares_dict[action_name] = shares

moving_averages_dict = {}
for action_name in grouped_shares_dict:
    for label in ['main', 'other']:
        for MA in MAIN_PLOT_WINDOW_SIZES if label == "main" else OTHER_PLOT_WINDOW_SIZES:
            moving_averages = moving_average(grouped_shares_dict[action_name], MA.initial_window_size)

            if MA.split_moving_average:
                moving_averages_dict[action_name + f'_MA{MA.initial_window_size}'] = moving_average(grouped_shares_dict[action_name], MA.initial_window_size)[:MA.splitting_point + 1]
                moving_averages_dict[action_name + f'_MA{MA.new_window_size}_SPLIT'] = moving_average(grouped_shares_dict[action_name], MA.new_window_size)[MA.splitting_point + 1:]
            else:
                moving_averages_dict[action_name + f'_MA{MA.initial_window_size}'] = moving_averages

combined_dict = {**grouped_shares_dict, **moving_averages_dict}

action_names = list(grouped_shares_dict.keys())
main_plot_action_names = sorted(action_names, key=lambda x: max(grouped_shares_dict[x]), reverse=True)[:3] if MAIN_PLOT_METHOD == "top3" else MAIN_PLOT_SELECTION
other_action_names = [name for name in action_names if name not in main_plot_action_names] if MAIN_PLOT_METHOD == "top3" else OTHER_MAIN_PLOT_SELECTION

for action_names_list, label in zip([main_plot_action_names, other_action_names], ['main', 'other']):
    plt.figure(figsize=(12, 6))
    for action_name in tqdm(action_names_list):
        for index, MA in enumerate(MAIN_PLOT_WINDOW_SIZES if label == "main" else OTHER_PLOT_WINDOW_SIZES):
            last_color_lighter = None
            if MA.split_moving_average:
                plt.plot(events_count_threshold[:MA.splitting_point + 1], moving_averages_dict[action_name + f'_MA{MA.initial_window_size}'], linestyle='-', linewidth=1, label=action_name + f' MA{MA.initial_window_size}')
                plt.plot(events_count_threshold[MA.splitting_point + 1:], moving_averages_dict[action_name + f'_MA{MA.new_window_size}_SPLIT'], linestyle='--', linewidth=1, label=action_name + f' MA{MA.new_window_size}' if SPLIT_LEGEND else "", color=plt.gca().lines[-1].get_color())
            else:
                if index == 0:
                    plt.plot(events_count_threshold, moving_averages_dict[action_name + f'_MA{MA.initial_window_size}'], linestyle='-', linewidth=1, label=action_name + f' MA{MA.initial_window_size}')
                else:
                    plt.plot(events_count_threshold, moving_averages_dict[action_name + f'_MA{MA.initial_window_size}'], linestyle='-', linewidth=1, label=action_name + f' MA{MA.initial_window_size}', color=to_rgba(plt.gca().lines[-1].get_color(), alpha=MA.alpha))
            if MA.plot_raw_data:
                plt.scatter(events_count_threshold, grouped_shares_dict[action_name], color=plt.gca().lines[-1].get_color(), alpha=0.5, marker='o')


    Y_MAX = MAIN_Y_MAX if label == "main" else OTHER_Y_MAX
    Y_TICKS_STEP = MAIN_Y_TICKS_STEP if label == "main" else OTHER_Y_TICKS_STEP
    plt.yticks(range(0, Y_MAX + 1, Y_TICKS_STEP))
    plt.ylim(Y_MIN, Y_MAX)
    for x_line in X_LINES:
        plt.axvline(x=x_line, color='gray', linestyle='--', linewidth=0.5)
    plt.xlabel(f'Number of events per contributor')
    plt.ylabel('Share (%)')
    plt.xticks(sorted(set(list(range(0, X_MAX + 1, 100)) + X_LINES)))
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.legend(title='Event types', bbox_to_anchor=(1.25, 1), loc='upper right')
    plt.tight_layout()
    plt.savefig(f"out/3_{'1' if label == 'main' else '2'}_event_type_shares_{label}_moving_average.png")
    plt.close()
