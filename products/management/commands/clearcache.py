from django.core.management.base import BaseCommand
from django_redis import get_redis_connection


class Command(BaseCommand):
    help = "Clears specific keys in Redis database 1 while keeping keys in database 0."

    def handle(self, *args, **kwargs):
        redis_conn = get_redis_connection("default")
        redis_conn.execute_command("SELECT", 1)  # Switch to database 1

        keys = redis_conn.keys("*")
        if keys:
            redis_conn.delete(*keys)
            self.stdout.write(self.style.SUCCESS("Cleared keys in database 1:"))
            for key in keys:
                self.stdout.write(f"{key.decode('utf-8')}")
        else:
            self.stdout.write(
                self.style.WARNING("No keys found in database 1 to clear.")
            )
