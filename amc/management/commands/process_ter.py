from django.core.management.base import BaseCommand, CommandError

from amc.jobs.ter_process import start_process


import datetime


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("processing TER for amc")
        start_process()