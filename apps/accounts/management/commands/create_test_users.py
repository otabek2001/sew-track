"""
Management command to create test users.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        """Create test users."""
        
        users_data = [
            {
                'email': 'admin@sewtrack.uz',
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.SUPER_ADMIN,
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'email': 'master@sewtrack.uz',
                'username': 'master',
                'password': 'master123',
                'first_name': 'Master',
                'last_name': 'Supervisor',
                'role': User.Role.MASTER,
            },
            {
                'email': 'worker@sewtrack.uz',
                'username': 'worker',
                'password': 'worker123',
                'first_name': 'Worker',
                'last_name': 'Employee',
                'role': User.Role.WORKER,
            },
            {
                'email': 'accountant@sewtrack.uz',
                'username': 'accountant',
                'password': 'accountant123',
                'first_name': 'Accountant',
                'last_name': 'Finance',
                'role': User.Role.ACCOUNTANT,
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for user_data in users_data:
            email = user_data['email']
            username = user_data['username']
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'❌ User already exists: {email}')
                )
                existing_count += 1
                continue
            
            password = user_data.pop('password')
            is_superuser = user_data.pop('is_superuser', False)
            
            if is_superuser:
                user = User.objects.create_superuser(password=password, **user_data)
            else:
                user = User.objects.create_user(password=password, **user_data)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created user: {email} (role: {user.get_role_display()})')
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Summary: {created_count} created, {existing_count} already existed'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f'📊 Total users in database: {User.objects.count()}')
        )

