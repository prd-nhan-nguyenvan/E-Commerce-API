import cProfile
import io
import pstats

from django.core.management.base import BaseCommand
from rest_framework.test import APIClient as Client


class Command(BaseCommand):
    help = "Profile a view by calling it multiple times"

    missing_args_message = (
        "You must provide a URL and the number of times to call the view"
    )

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="The URL to profile")
        parser.add_argument("times", type=int, help="Number of times to call the view")

    def handle(self, *args, **kwargs):
        url = kwargs["url"]
        total_runs = kwargs["times"]

        client = Client()
        pr = cProfile.Profile()

        for _ in range(total_runs):
            pr.enable()
            client.get(url)
            pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.strip_dirs().sort_stats("cumulative").print_stats(10)  # Show top 10 results

        self.stdout.write(s.getvalue())
