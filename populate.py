import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authentication.settings')

import django
django.setup()

from users.models import User


def populate():
    try:
        s_user = User.objects.get(username='superuser')
    except User.DoesNotExist:
        s_user = User.objects.create_superuser(
            username="superuser",
            password="admin1234",
        )
        s_user.first_name = 'Super User'
        s_user.last_name = '.'
        s_user.is_superuser = True
        s_user.is_staff = True
        s_user.save()


if __name__ == '__main__':
    print("Populating Project...")
    populate()