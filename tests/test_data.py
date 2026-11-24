"""Recompute every value with QuantLib (calendars, Calendar.adjust and DayCounter.yearFraction), which shares no
code with the generator (holiday lists from the `holidays` package, rules in plain Python).

    pip install QuantLib
    python -m unittest discover -s tests -v
"""
import csv
import os
import unittest
from datetime import date

import QuantLib as ql

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
CALS = {"USD-FED": ql.UnitedStates(ql.UnitedStates.FederalReserve), "EUR-TARGET": ql.TARGET(),
        "GBP-ENG": ql.UnitedKingdom(ql.UnitedKingdom.Settlement)}
CONVS = {"following": ql.Following, "modified_following": ql.ModifiedFollowing, "preceding": ql.Preceding,
         "modified_preceding": ql.ModifiedPreceding}
DC = {"ACT/360": ql.Actual360(), "ACT/365F": ql.Actual365Fixed(), "30/360 bond basis": ql.Thirty360(ql.Thirty360.BondBasis),
      "30E/360": ql.Thirty360(ql.Thirty360.European), "ACT/ACT ISDA": ql.ActualActual(ql.ActualActual.ISDA)}


def rows(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def qd(s):
    d = date.fromisoformat(s)
    return ql.Date(d.day, d.month, d.year)


def iso(q):
    return f"{q.year():04d}-{q.month():02d}-{q.dayOfMonth():02d}"


class Data(unittest.TestCase):
    def test_rolls(self):
        rs = rows("business_day_rolls_2026_2028.csv")
        self.assertEqual(len(rs), 3 * 1096)
        for r in rs:
            cal, d = CALS[r["calendar"]], qd(r["date"])
            self.assertEqual(r["is_business_day"] == "1", cal.isBusinessDay(d), r)
            for c, q in CONVS.items():
                self.assertEqual(r[c], iso(cal.adjust(d, q)), (r["calendar"], r["date"], c))

    def test_day_counts(self):
        rs = rows("day_count_fractions.csv")
        self.assertEqual(len(rs), 1000)
        for r in rs:
            a, b = qd(r["start"]), qd(r["end"])
            self.assertEqual(int(r["days"]), b - a)
            for name, dc in DC.items():
                self.assertAlmostEqual(float(r[name]), dc.yearFraction(a, b), places=11, msg=(r["start"], r["end"], name))

    def test_known(self):
        rs = {(r["calendar"], r["date"]): r for r in rows("business_day_rolls_2026_2028.csv")}
        # Sat Jan 31, 2026: following crosses into February, so modified following goes back to Fri Jan 30
        r = rs[("USD-FED", "2026-01-31")]
        self.assertEqual((r["following"], r["modified_following"]), ("2026-02-02", "2026-01-30"))
        # Good Friday Apr 3, 2026 is a TARGET holiday but not a Federal Reserve holiday
        self.assertEqual(rs[("EUR-TARGET", "2026-04-03")]["is_business_day"], "0")
        self.assertEqual(rs[("USD-FED", "2026-04-03")]["is_business_day"], "1")


if __name__ == "__main__":
    unittest.main()
