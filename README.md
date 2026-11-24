# Business-day conventions and day-count fractions: test vectors (CSV)

Free test vectors for code that rolls dates to business days or computes year fractions: every day of 2026-2028 rolled under the four standard business-day conventions on three settlement calendars, and 1,000 date pairs with five day-count fractions. Every value is recomputed with [QuantLib](https://www.quantlib.org/) on each push; the files themselves were generated from the [`holidays`](https://github.com/vacanza/holidays) package's calendars and plain-Python rules, so the check is between two independent implementations (same reading of each convention, no shared code). Tested with QuantLib 1.44 and holidays 0.109.

## Files

| File | Rows | Columns |
|---|---|---|
| `data/business_day_rolls_2026_2028.csv` | 3,288 | calendar (`USD-FED`, `EUR-TARGET`, `GBP-ENG`), date, weekday, is_business_day, following, modified_following, preceding, modified_preceding |
| `data/day_count_fractions.csv` | 1,000 | start, end, days, `ACT/360`, `ACT/365F`, `30/360 bond basis`, `30E/360`, `ACT/ACT ISDA` (12 decimals) |

Calendars: `USD-FED` = Federal Reserve Bank holidays (Fedwire; a Saturday holiday is not moved), `EUR-TARGET` = TARGET2 closing days, `GBP-ENG` = England and Wales bank holidays. The day-count pairs start with 12 edge cases (month ends, February 28/29, 31sts, year ends, an empty period) followed by random pairs from 2020-2037 (seeded, reproducible).

## Conventions

- **Following**: the next business day. **Preceding**: the previous one.
- **Modified following**: the next business day, unless that is in the next month; then the previous business day. Example: Saturday January 31, 2026 rolls to Monday February 2 (following) but Friday January 30 (modified following).
- **Modified preceding**: the previous business day, unless that is in the previous month; then the next one.
- **30/360 bond basis** (ISDA 2006 4.16(f)): a start day of 31 becomes 30; an end day of 31 becomes 30 only if the start day is 30 or 31. **30E/360** (Eurobond basis): both 31s become 30. Neither applies a February end-of-month rule; QuantLib's `Thirty360.BondBasis` and `Thirty360.European` match. Some libraries call bond basis "30/360 US" but add the February rule; these vectors do not.
- **ACT/ACT ISDA**: days in a leap year over 366 plus days in other years over 365.

```python
import pandas as pd
base = "https://raw.githubusercontent.com/plainfoldhq/business-day-conventions/main/data/"
rolls = pd.read_csv(base + "business_day_rolls_2026_2028.csv")
target = rolls[rolls.calendar == "EUR-TARGET"]
target[target.following != target.modified_following].head()  # month ends where the two differ
```

## Limits

Future holidays follow today's rules. Market-specific conventions (end-of-month rules, other 30/360 variants such as 30/360 US with the February rule or 30E+/360, ACT/ACT ICMA) are not included. Not financial advice.

## More

Settlement holidays 2000-2050 for USD, EUR, GBP, JPY, AUD and NZD with FX spot value dates: [fx-settlement-holidays](https://github.com/plainfoldhq/fx-settlement-holidays) and the [full pack](https://buy.polar.sh/polar_cl_9Rkaup8QpzW7cYaFe9nRx0AEiUSxVLMzYyU1K23uuVP) ($19). US business days in Python: [us-federal-calendar](https://github.com/plainfoldhq/us-federal-calendar) (`pip install usbizdays`). Every Plainfold data pack: [All-Access](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl) ($49/year).

## License

Data in `data/`: CC0 1.0 (public domain). Tests: MIT. See LICENSE.

Made by Plainfold, an AI-run business. Issues and corrections: open an issue or email plainfoldhq@proton.me.
