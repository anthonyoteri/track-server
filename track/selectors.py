from datetime import datetime, date, time, timedelta
import logging
from typing import Any, Dict, Optional, Set

from django.db.models import Q
import pendulum

from .models import Category, Project, Record


log = logging.getLogger(__name__)


def get_active_record() -> Optional[Record]:

    query = Q(stop_time_epoch__isnull=True)

    try:
        return Record.objects.get(query)
    except Record.DoesNotExist:
        return None


def get_elapsed_time(
    *,
    project: Project,
    begin: Optional[datetime] = None,
    end: Optional[datetime] = None
) -> int:

    query = Q(project=project)

    if begin is not None:
        query &= Q(start_time_epoch__gte=datetime.timestamp(begin))

    if end is not None:
        query &= Q(start_time_epoch__lt=datetime.timestamp(end))

    records = Record.objects.filter(query).all()

    if records is None:
        return 0

    total = sum([int(r.elapsed) for r in records])
    return total


def get_elapsed_time_per_category(
    *,
    category: Category,
    begin: Optional[datetime] = None,
    end: Optional[datetime] = None
) -> int:

    if category.projects.count() == 0:
        return 0

    return sum(
        [
            get_elapsed_time(project=p, begin=begin, end=end)
            for p in category.projects.all()
        ]
    )


def get_entries_per_day(
    *, day: date, category: Optional[str] = None
) -> Dict[Project, int]:

    range_begin = datetime.timestamp(datetime.combine(day, time()))
    range_end = datetime.timestamp(
        datetime.combine(day, time()) + timedelta(days=1)
    )

    in_range_query = Q(start_time_epoch__gte=range_begin) & Q(
        start_time_epoch__lte=range_end
    )
    records_in_range = Record.objects.filter(in_range_query).all()

    if category is not None:
        cat = Category.objects.get(name=category)
        records_in_range = records_in_range.filter(
            project__in=cat.projects.all()
        )

    projects_in_range = set([r.project for r in records_in_range])

    result = {}
    for project in projects_in_range:
        with_project = Q(project=project)
        total = sum(
            [
                int(r.elapsed)
                for r in records_in_range.filter(with_project).all()
            ]
        )

        result[project] = total

    return result


def get_entries_per_week(
    *, week_number: str, category: Optional[str] = None
) -> Dict:
    range_begin = pendulum.parse(week_number).start_of("week")
    range_end = pendulum.parse(week_number).end_of("week")

    period = pendulum.period(range_begin, range_end)
    result: Dict[str, Any] = {"week_number": week_number, "days": []}

    if category is not None:
        result["category"] = category

    included_projects: Set[str] = set()

    for dt in period.range("days"):

        # A hack to convert between pendulum date object and datetime.date
        python_date = datetime.fromtimestamp(dt.timestamp()).date()

        entries_per_day = get_entries_per_day(
            day=python_date, category=category
        )
        included_projects = included_projects.union(
            {k.name for k in entries_per_day.keys()}
        )

        log.debug("included projects now %s", included_projects)

        result["days"].append(
            {
                "date": python_date,
                "records": {k.name: v for k, v in entries_per_day.items()},
                "total": sum(entries_per_day.values()),
            }
        )

    result["projects"] = sorted(list(included_projects))

    return result
