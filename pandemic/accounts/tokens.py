from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class RegisterToken(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, user, timestamp):
        # Ensure results are consistent across DB backends
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return str(user.pk) + user.password + str(login_timestamp) + str(timestamp) + str(user.is_active)

RegistrationTokenizer = RegisterToken()

