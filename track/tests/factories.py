from datetime import datetime, timedelta
import random

import factory

from track.models import Category, Project, Record


class CategoryFactory(factory.DjangoModelFactory):
    name = factory.Faker("slug")
    description = factory.Faker("text")

    class Meta:
        model = Category


class ProjectFactory(factory.DjangoModelFactory):
    name = factory.Faker("slug")
    description = factory.Faker("text")

    class Meta:
        model = Project


class RecordFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    start_time_epoch = factory.Faker(
        "random_int",
        min=int(datetime.timestamp(datetime.now() - timedelta(days=30))),
        max=int(datetime.timestamp(datetime.now() - timedelta(minutes=30))),
    )
    stop_time_epoch = factory.LazyAttribute(
        lambda obj: obj.start_time_epoch + random.randint(0, 30 * 60 * 60)
    )

    class Meta:
        model = Record
