"""Create deterministic showcase data without altering other apps."""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from showcase.seed import seed


class Command(BaseCommand):
    """Prepare data for the native showcase."""

    help: str = 'Seed the isolated showcase tables.'

    def add_arguments(self, parser: CommandParser) -> None:
        """Expose an explicit reset option."""
        parser.add_argument('--reset', action='store_true')

    def handle(self, *args: Any, **options: Any) -> None:
        """Seed the catalogue and report success."""
        seed(reset=bool(options['reset']))
        self.stdout.write('Showcase data ready.')
