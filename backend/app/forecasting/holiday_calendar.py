from __future__ import annotations

import pandas as pd


def get_walmart_holiday_dates(
    start_year: int,
    end_year: int,
) -> set[pd.Timestamp]:
    """
    Return weekly dates associated with major Walmart
    holiday/event weeks.

    Events:
    - Super Bowl week
    - Labor Day week
    - Thanksgiving week
    - Christmas week
    """

    if start_year > end_year:
        raise ValueError(
            "start_year must be less than or equal to end_year."
        )

    holiday_dates: set[pd.Timestamp] = set()

    for year in range(start_year, end_year + 1):

        # -------------------------
        # Super Bowl week
        # -------------------------

        super_bowl = pd.Timestamp(
            year=year,
            month=2,
            day=1,
        )

        while super_bowl.weekday() != 6:
            super_bowl += pd.Timedelta(days=1)

        super_bowl_week = (
            super_bowl + pd.Timedelta(days=5)
        )

        # -------------------------
        # Labor Day week
        # -------------------------

        labor_day = pd.Timestamp(
            year=year,
            month=9,
            day=1,
        )

        while labor_day.weekday() != 0:
            labor_day += pd.Timedelta(days=1)

        labor_day_week = (
            labor_day + pd.Timedelta(days=4)
        )

        # -------------------------
        # Thanksgiving week
        # -------------------------

        november_first = pd.Timestamp(
            year=year,
            month=11,
            day=1,
        )

        thanksgiving = november_first
        thursday_count = 0

        while True:

            if thanksgiving.weekday() == 3:
                thursday_count += 1

                if thursday_count == 4:
                    break

            thanksgiving += pd.Timedelta(days=1)

        thanksgiving_week = (
            thanksgiving + pd.Timedelta(days=1)
        )

        # -------------------------
        # Christmas week
        # -------------------------

        christmas = pd.Timestamp(
            year=year,
            month=12,
            day=25,
        )

        christmas_week = (
            christmas
            + pd.Timedelta(
                days=(4 - christmas.weekday()) % 7
            )
        )

        holiday_dates.update(
            {
                super_bowl_week.normalize(),
                labor_day_week.normalize(),
                thanksgiving_week.normalize(),
                christmas_week.normalize(),
            }
        )

    return holiday_dates


def get_holiday_flag(
    date: pd.Timestamp,
) -> int:
    """
    Return 1 if the supplied weekly date belongs
    to a Walmart holiday/event week, otherwise 0.
    """

    date = pd.Timestamp(date).normalize()

    holiday_dates = get_walmart_holiday_dates(
        start_year=date.year,
        end_year=date.year,
    )

    return int(date in holiday_dates)