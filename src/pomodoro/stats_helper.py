from collections import Counter
from typing import List, Dict, Any

def get_stats(events_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []

    curr_categories: List[str] = []
    curr_focus: List[str] = []
    curr_productivity: List[bool] = []

    focus_to_num = {'low': 1, 'medium': 2, 'high': 3}
    num_to_focus = {v: k for k, v in focus_to_num.items()}

    def flush_block() -> None:
        if not (curr_categories or curr_focus or curr_productivity):
            return

        most_common_category = (
            Counter(curr_categories).most_common(1)[0][0]
            if curr_categories else None
        )

        if curr_focus:
            avg_focus_numeric = sum(focus_to_num[f] for f in curr_focus) / len(curr_focus)
            avg_focus = num_to_focus[min(max(round(avg_focus_numeric), 1), 3)]
        else:
            avg_focus = None

        percent_productive = (
            sum(curr_productivity) / len(curr_productivity) * 100
            if curr_productivity else 0
        )

        result.append({
            'most_common_category': most_common_category,
            'avg_focus_level': avg_focus,
            'percent_productive': percent_productive,
        })

        curr_categories.clear()
        curr_focus.clear()
        curr_productivity.clear()

    for event in events_list:
        etype = event.get('event_type')

        if etype == 'AI_SNAP':
            cat = event.get('s_category')
            if isinstance(cat, list):
                curr_categories.extend(cat)
            elif cat is not None:
                curr_categories.append(cat)

            focus = event.get('s_focus')
            if focus in focus_to_num:
                curr_focus.append(focus)

            curr_productivity.append(bool(event.get('s_is_productive', False)))

        elif etype == 'POM_START':
            flush_block()

    flush_block()
    return result
