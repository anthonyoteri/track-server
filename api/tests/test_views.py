from django.urls import reverse
import pendulum
import pytest
from rest_framework.test import APIClient
from rest_framework import status

from track.tests import factories


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_create_category(client):

    category_stub = factories.CategoryFactory.stub()

    body = {
        "name": category_stub.name,
        "description": category_stub.description,
    }
    url = reverse("api:category-list")

    resp = client.post(url, data=body)
    assert resp.status_code == status.HTTP_201_CREATED, resp.content

    result = resp.json()

    assert result == {**body, "projects": []}


@pytest.mark.django_db
def test_get_category(client):

    category = factories.CategoryFactory()
    url = reverse("api:category-detail", kwargs={"name": category.name})

    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK, resp.content

    body = resp.json()
    assert body["name"] == category.name
    assert body["description"] == category.description


@pytest.mark.django_db
def test_list_categories(client):
    categories = factories.CategoryFactory.create_batch(10)

    resp = client.get(reverse("api:category-list"))
    assert resp.status_code == status.HTTP_200_OK, resp.content
    body = resp.json()

    assert body["count"] == 10
    assert body["next"] is None
    assert body["previous"] is None
    for category, got in zip(categories, body["results"]):
        wanted = {
            "name": category.name,
            "description": category.description,
            "projects": [],
        }
        assert got == wanted


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["name", "description"])
def test_update_category(field, client):

    category = factories.CategoryFactory()
    url = reverse("api:category-detail", kwargs={"name": category.name})

    resp = client.patch(url, data={field: "foobar"})
    assert resp.status_code == status.HTTP_200_OK, resp.content

    body = resp.json()
    assert body[field] == "foobar"


@pytest.mark.django_db
def test_delete_category(client):
    category = factories.CategoryFactory()
    url = reverse("api:category-detail", kwargs={"name": category.name})

    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT, resp.content


@pytest.mark.django_db
def test_create_project(client):

    project_stub = factories.ProjectFactory.stub()

    body = {"name": project_stub.name, "description": project_stub.description}
    url = reverse("api:project-list")

    resp = client.post(url, data=body)
    assert resp.status_code == status.HTTP_201_CREATED, resp.content

    result = resp.json()

    assert result == {**body, "categories": []}


@pytest.mark.django_db
def test_get_project(client):

    project = factories.ProjectFactory()
    url = reverse("api:project-detail", kwargs={"name": project.name})

    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK, resp.content

    body = resp.json()
    assert body["name"] == project.name
    assert body["description"] == project.description


@pytest.mark.django_db
def test_list_projects(client):
    projects = factories.ProjectFactory.create_batch(10)

    resp = client.get(reverse("api:project-list"))
    assert resp.status_code == status.HTTP_200_OK, resp.content
    body = resp.json()

    assert body["count"] == 10
    assert body["next"] is None
    assert body["previous"] is None
    for project, got in zip(projects, body["results"]):
        wanted = {
            "name": project.name,
            "description": project.description,
            "categories": [],
        }
        assert got == wanted


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["name", "description"])
def test_update_project(field, client):

    project = factories.ProjectFactory()
    url = reverse("api:project-detail", kwargs={"name": project.name})

    resp = client.patch(url, data={field: "foobar"})
    assert resp.status_code == status.HTTP_200_OK, resp.content

    body = resp.json()
    assert body[field] == "foobar"


@pytest.mark.django_db
def test_assign_project(client, subtests):
    category_1 = factories.CategoryFactory()
    category_2 = factories.CategoryFactory()

    project = factories.ProjectFactory()

    url = reverse("api:project-detail", kwargs={"name": project.name})
    resp = client.patch(
        url, data={"categories": [category_1.name, category_2.name]}
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content

    with subtests.test(msg="categories in project"):
        resp_proj = client.get(url)
        assert resp_proj.json()["categories"] == [
            category_1.name,
            category_2.name,
        ]

    with subtests.test(msg="project in categories"):
        for category in [category_1, category_2]:
            resp_cat = client.get(
                reverse("api:category-detail", kwargs={"name": category.name})
            )
            assert resp_cat.json()["projects"] == [project.name]


@pytest.mark.django_db
def test_delete_project(client):
    project = factories.ProjectFactory()
    url = reverse("api:project-detail", kwargs={"name": project.name})

    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT, resp.content


@pytest.mark.django_db
def test_create_record(client):

    project = factories.ProjectFactory()
    now = pendulum.now().set(microsecond=0)

    url = reverse("api:record-list")

    body = {
        "project": project.name,
        "start_time": now.subtract(minutes=30).isoformat(),
    }

    resp = client.post(url, data=body)
    assert resp.status_code == status.HTTP_201_CREATED, resp.content

    got = resp.json()

    assert got["project"] == project.name
    assert pendulum.parse(got["start_time"]) == now.subtract(minutes=30)
    assert got["stop_time"] is None
    assert 30 * 60 <= got["elapsed"] <= 31 * 60


@pytest.mark.django_db
def test_create_record_with_stop_time(client):

    project = factories.ProjectFactory()
    now = pendulum.now().set(microsecond=0)

    url = reverse("api:record-list")

    body = {
        "project": project.name,
        "start_time": now.subtract(minutes=30).isoformat(),
        "stop_time": now.isoformat(),
    }

    resp = client.post(url, data=body)
    assert resp.status_code == status.HTTP_201_CREATED, resp.content

    got = resp.json()

    assert got["project"] == project.name
    assert pendulum.parse(got["start_time"]) == now.subtract(minutes=30)
    assert pendulum.parse(got["stop_time"]) == now
    assert got["elapsed"] == 30 * 60


@pytest.mark.django_db
def test_list_records(client):
    project = factories.ProjectFactory()
    records = factories.RecordFactory.create_batch(5, project=project)

    url = reverse("api:record-list")

    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK, resp.content

    body = resp.json()
    assert body["count"] == len(records)
    assert body["next"] is None
    assert body["previous"] is None
    for record, got in zip(
        sorted(records, key=lambda x: x.start_time, reverse=True),
        body["results"],
    ):
        assert got["project"] == project.name
        assert (
            pendulum.parse(got["start_time"]).timestamp()
            == record.start_time.timestamp()
        )
        assert (
            pendulum.parse(got["stop_time"]).timestamp()
            == record.stop_time.timestamp()
        )
        assert (
            got["elapsed"]
            == (
                pendulum.parse(got["stop_time"])
                - pendulum.parse(got["start_time"])
            ).total_seconds()
        )


@pytest.mark.django_db
def test_get_active_record(client):

    project = factories.ProjectFactory()
    record = factories.RecordFactory(project=project, stop_time_epoch=None)

    url = reverse("api:record-active")
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK, resp.content

    body = resp.json()

    assert body["project"] == project.name
    assert (
        pendulum.parse(body["start_time"]).timestamp()
        == record.start_time.timestamp()
    )
    assert body["stop_time"] is None
    assert body["elapsed"] >= 0


@pytest.mark.django_db
def test_get_active_record_missing(client):

    project = factories.ProjectFactory()
    factories.RecordFactory(project=project)

    url = reverse("api:record-active")
    resp = client.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND, resp.content


@pytest.mark.django_db
def test_weekly_report(client, subtests):

    project_1 = factories.ProjectFactory()
    project_2 = factories.ProjectFactory()
    project_3 = factories.ProjectFactory()

    # Set now to be a known date, in this case a Friday at 4pm.  All times in
    # this test will be relative to this `now`
    now = pendulum.datetime(2019, 7, 12, 16, 0, 0, tz="America/New_York")
    yesterday = now.subtract(days=1)

    # Setup records for Thursday
    record_1 = factories.RecordFactory(
        project=project_1,
        start_time_epoch=yesterday.at(9).timestamp(),
        stop_time_epoch=yesterday.at(13).timestamp(),
    )
    record_2 = factories.RecordFactory(
        project=project_2,
        start_time_epoch=yesterday.at(13).timestamp(),
        stop_time_epoch=yesterday.at(17).timestamp(),
    )

    # Setup records for Friday
    record_3 = factories.RecordFactory(
        project=project_3,
        start_time_epoch=now.at(9).timestamp(),
        stop_time_epoch=now.at(14, 30).timestamp(),
    )
    record_4 = factories.RecordFactory(
        project=project_1,
        start_time_epoch=now.at(14, 30).timestamp(),
        stop_time_epoch=now.at(14, 45).timestamp(),
    )
    record_5 = factories.RecordFactory(
        project=project_2,
        start_time_epoch=now.at(14, 45).timestamp(),
        stop_time_epoch=now.timestamp(),
    )

    with subtests.test(msg="no filter"):
        url = reverse(
            "api:report-week", kwargs={"year": 2019, "week_number": 28}
        )
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK, resp.content

        body = resp.json()
        assert body["week_number"] == "2019-W28"
        assert body["projects"] == sorted(
            [project_1.name, project_2.name, project_3.name]
        )

        expected = [
            {"date": "2019-07-08", "records": {}, "total": 0},
            {"date": "2019-07-09", "records": {}, "total": 0},
            {"date": "2019-07-10", "records": {}, "total": 0},
            {
                "date": "2019-07-11",
                "records": {
                    project_1.name: record_1.elapsed,
                    project_2.name: record_2.elapsed,
                },
                "total": record_1.elapsed + record_2.elapsed,
            },
            {
                "date": "2019-07-12",
                "records": {
                    project_3.name: record_3.elapsed,
                    project_1.name: record_4.elapsed,
                    project_2.name: record_5.elapsed,
                },
                "total": record_3.elapsed
                + record_4.elapsed
                + record_5.elapsed,
            },
            {"date": "2019-07-13", "records": {}, "total": 0},
            {"date": "2019-07-14", "records": {}, "total": 0},
        ]

        assert body["days"] == expected

    with subtests.test(msg="filter by category"):
        category_1 = factories.CategoryFactory()
        category_2 = factories.CategoryFactory()

        category_1.projects.add(project_1)
        category_1.projects.add(project_2)

        category_2.projects.add(project_2)
        category_2.projects.add(project_3)

        url = reverse(
            "api:report-week-category",
            kwargs={
                "year": 2019,
                "week_number": 28,
                "category": category_1.name,
            },
        )
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK, resp.content

        body = resp.json()
        assert body["week_number"] == "2019-W28"
        assert body["category"] == category_1.name
        assert body["projects"] == sorted([project_1.name, project_2.name])

        expected = [
            {"date": "2019-07-08", "records": {}, "total": 0},
            {"date": "2019-07-09", "records": {}, "total": 0},
            {"date": "2019-07-10", "records": {}, "total": 0},
            {
                "date": "2019-07-11",
                "records": {
                    project_1.name: record_1.elapsed,
                    project_2.name: record_2.elapsed,
                },
                "total": record_1.elapsed + record_2.elapsed,
            },
            {
                "date": "2019-07-12",
                "records": {
                    project_1.name: record_4.elapsed,
                    project_2.name: record_5.elapsed,
                },
                "total": record_4.elapsed + record_5.elapsed,
            },
            {"date": "2019-07-13", "records": {}, "total": 0},
            {"date": "2019-07-14", "records": {}, "total": 0},
        ]

        assert body["days"] == expected
        url = reverse(
            "api:report-week-category",
            kwargs={
                "year": 2019,
                "week_number": 28,
                "category": category_2.name,
            },
        )
        resp = client.get(url)
        assert resp.status_code == status.HTTP_200_OK, resp.content

        body = resp.json()
        assert body["week_number"] == "2019-W28"
        assert body["category"] == category_2.name
        assert body["projects"] == sorted([project_2.name, project_3.name])

        expected = [
            {"date": "2019-07-08", "records": {}, "total": 0},
            {"date": "2019-07-09", "records": {}, "total": 0},
            {"date": "2019-07-10", "records": {}, "total": 0},
            {
                "date": "2019-07-11",
                "records": {project_2.name: record_2.elapsed},
                "total": record_2.elapsed,
            },
            {
                "date": "2019-07-12",
                "records": {
                    project_3.name: record_3.elapsed,
                    project_2.name: record_5.elapsed,
                },
                "total": record_3.elapsed + record_5.elapsed,
            },
            {"date": "2019-07-13", "records": {}, "total": 0},
            {"date": "2019-07-14", "records": {}, "total": 0},
        ]

        assert body["days"] == expected
