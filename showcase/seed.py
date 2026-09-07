"""Repeatable seed data confined to the showcase tables."""

from __future__ import annotations

from django.db import transaction

from .models import Article, Contact, Tag


@transaction.atomic
def seed(reset: bool = False) -> None:
    """Create the initial catalogue and optionally reset showcase data."""
    if reset:
        Article.objects.all().delete()
        Contact.objects.all().delete()
        Tag.objects.all().delete()
    tags: list[Tag] = [
        Tag.objects.get_or_create(name=name)[0]
        for name in (
            'Django',
            'Python',
            'PostgreSQL',
            'Redis',
            'AsyncIO',
            'Bootstrap',
            'Celery',
            'Elasticsearch',
            'FastAPI',
            'Git',
            'HTMX',
            'IPython',
            'Jupyter',
            'Kubernetes',
            'Linux',
            'Matplotlib',
            'NumPy',
            'OpenTelemetry',
            'Quart',
            'SQLite',
            'TypeScript',
            'Uvicorn',
            'Vue',
            'WebAssembly',
            'XML',
            'YAML',
            'Zig',
        )
    ]
    contacts: list[Contact] = [
        Contact.objects.get_or_create(first_name=first, last_name=last)[0]
        for first, last in (
            ('Ada', 'Lovelace'),
            ('Grace', 'Hopper'),
            ('Ben', 'Carter'),
            ('Chloe', 'Davies'),
            ('Daniel', 'Evans'),
            ('Emma', 'Foster'),
            ('Finn', 'Green'),
            ('Hannah', 'Hughes'),
            ('Isla', 'Irving'),
            ('James', 'Jones'),
            ('Kai', 'Khan'),
            ('Lucy', 'Lewis'),
            ('Maya', 'Morgan'),
            ('Noah', 'Nelson'),
            ('Olivia', 'Owen'),
            ('Priya', 'Patel'),
            ('Quinn', 'Quigley'),
            ('Ravi', 'Reed'),
            ('Sophie', 'Singh'),
            ('Theo', 'Taylor'),
            ('Uma', 'Underwood'),
            ('Violet', 'Vaughan'),
            ('Will', 'Williams'),
            ('Xavier', 'Xu'),
            ('Yasmin', 'Young'),
            ('Zara', 'Zhang'),
        )
    ]
    for mode in ('create', 'existing', 'composite'):
        article: Article
        created: bool
        article, created = Article.objects.get_or_create(title=mode)
        if created:
            for tag in tags[:2]:
                article.tags.add(tag)
            article.contacts.add(contacts[0])
