from .config import gc
from .helper_functions import (
    fmt_as_str__maybe_in_critical_color,
    make_two_column_table,
)


def mini_card_stats(card, p, show_od):
    """mini_card_stats is called for current and prior card. Overdue days doesn't make sense
    for recently rated cards. So there needs to be an option to hide it. """
    # originally this was:
    # card_ivl_str=str(card.ivl),
    # dueday=str(self.due_day(card)),
    # value_for_overdue=str(self.valueForOverdue(card)),
    # actual_ivl
    right_column = p.card_ivl_str + ' (scheduled)'
    cmd = "BrowserSearch#" + str(p.c_CardID)
    clickable_cid = f'''<a href=# onclick="return pycmd('{cmd}')">{p.c_CardID}</a>'''

    t = gc("thresholds__lapse_counter_for_card", 10)
    thresh_col = fmt_as_str__maybe_in_critical_color(p.c_Lapses, -1, t, usespan=True, invert=True)

    rows_mini_stats = [
        ("Ivl/Ease", right_column + " / " + p.c_Ease_str),
        # ("sched Ivl",p.card_ivl_str),
        # ("actual Ivl",p.card_ivl_str),
        ("Due day", p.dueday),
        ("cid/card created", clickable_cid + '&nbsp;&nbsp;--&nbsp;&nbsp;' + p.now),
        ("Lapses/Reviews", thresh_col + " / " + p.c_Reviews),
        ("Tot/Average Time", p.c_TotalTime + " / " + p.c_AverageTime),
        ("Note/Card Type", p.c_NoteType + " / " + p.c_CardType),
    ]
    if show_od:
        if p.overdue_percent != "0":
            pc = '  (' + p.overdue_percent + '%)'
        else:
            pc = ""
        rows_mini_stats.insert(1, ("Overdue days: ", p.value_for_overdue + pc))
    return make_two_column_table(rows_mini_stats)


def mini_card_stats_with_ord(card, p, show_od):
    """mini_card_stats is called for current and prior card. Overdue days doesn't make sense
    for recently rated cards. So there needs to be an option to hide it. """
    right_column = p.card_ivl_str + ' (scheduled)'
    cmd = "BrowserSearch#" + str(p.c_CardID)
    clickable_cid = f'''<a href=# onclick="return pycmd('{cmd}')">{p.c_CardID}</a>'''
    rows_mini_stats = [
        ("Ivl", right_column),
        # ("sched Ivl",p.card_ivl_str),
        # ("actual Ivl",p.card_ivl_str),
        ("Due day", p.dueday),
        ("cid/card created", clickable_cid + '&nbsp;&nbsp;--&nbsp;&nbsp;' + p.now),
        ("Template No.", p.c_ord),
        ("Deck(did)", p.c_Deck + '   (' + str(p.c_did) + ')'),
        ("Ease", p.c_Ease_str),
    ]
    if show_od:
        if p.overdue_percent != "0":
            pc = '  (' + p.overdue_percent + '%)'
        else:
            pc = ""
        rows_mini_stats.insert(1, ("Overdue days: ", p.value_for_overdue + pc))
    return make_two_column_table(rows_mini_stats)


def card_stats_as_in_browser(card, p):
    # Extended Card Stats shows the info field that you see when you
    # click "Info" in the toolbar of the browser with this line:
    txt = ""
    # txt = self.mw.col.cardStats(card)
    # I rebuild this option here, so that it's easier to customize.
    as_in_browser = [
        ("Added", p.c_Added),
        ("First Review", p.c_FirstReview),
        ("Latest Review", p.c_LatestReview),
        ("Due", p.c_Due),
        ("Interval", p.c_Interval),
        ("Ease", p.c_Ease_str),
        ("Reviews", p.c_Reviews),
        ("Lapses", p.c_Lapses),
        ("Card Type", p.c_CardType),
        ("Note Type", p.c_NoteType),
        ("Deck", p.c_Deck),
        ("Note ID", p.c_NoteID),
        ("Card ID", p.c_CardID),
        ]
    if p.cnt:
        as_in_browser.insert(7, ("Average Time", p.c_AverageTime))
        as_in_browser.insert(8, ("Total Time", p.c_TotalTime))
    return txt + make_two_column_table(as_in_browser)
