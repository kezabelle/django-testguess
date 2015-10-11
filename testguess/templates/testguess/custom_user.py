        from django.contrib.auth import get_user_model
        from django.utils.crypto import get_random_string
        User = get_user_model()
        username = '{{ response.status_code }}@{{ request.method }}'
        password = get_random_string(5)
        user = User(**{User.USERNAME_FIELD: username})
        user.is_active = {{ request.user.is_active }}
        user.is_staff = {{ request.user.is_staff }}
        user.is_superuser = {{ request.user.is_superuser }}
        user.set_password(password)
        user.save()
        self.user = user
        self.auth = {'username': username, 'password': password}
        self.client.login(**self.auth)
