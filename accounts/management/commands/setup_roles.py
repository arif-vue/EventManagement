from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from events.models import UserProfile

class Command(BaseCommand):
    help = 'Setup initial groups and roles for the Event Management System'

    def handle(self, *args, **options):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Admin group'))
        
        organizer_group, created = Group.objects.get_or_create(name='Organizer')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Organizer group'))
            
        participant_group, created = Group.objects.get_or_create(name='Participant')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Participant group'))
        
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@eventmanagement.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            admin_user.groups.add(admin_group)
            
            # Create profile for admin
            UserProfile.objects.create(user=admin_user, is_activated=True)
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Created admin user with username: admin, password: admin123'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS('Setup completed successfully!')
        )
