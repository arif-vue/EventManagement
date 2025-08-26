from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Fix the site domain for development'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(pk=1)
            site.domain = '127.0.0.1:8000'
            site.name = 'Event Management System (Development)'
            site.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated site domain to: {site.domain}'
                )
            )
        except Site.DoesNotExist:
            site = Site.objects.create(
                pk=1,
                domain='127.0.0.1:8000',
                name='Event Management System (Development)'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created new site with domain: {site.domain}'
                )
            )
