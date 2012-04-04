from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings


from foundry.models import FoundryComment


class Command(BaseCommand):
    help = "Scan comments for naughty words and report by email."

    @transaction.commit_on_success
    def handle(self, *args, **options):
        for comment in FoundryComment.objects.filter(moderated=False):
            pass


