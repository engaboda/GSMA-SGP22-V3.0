import os
from binascii import hexlify

from django.db import models


class HandleNotifyState:
    INSTALLED: str = 'Installed'
    ENABLED: str = 'Enabled'
    DISABLED: str = 'Disabled'
    DELETED: str = 'Deleted'

    @classmethod
    def as_list(cls):
        return (
            (value, name) for name, value in vars(cls).items() if name.isupper()
        )


class Profile(models.Model):
    upp = models.TextField()
    linked_eid = models.CharField()

    @classmethod
    def create_random_hex(cls, length=16):
        return hexlify(os.urandom(length))

    @classmethod
    def generate_matching_id(cls):
        """
            4.1.1 Matching ID from SGP 22
            It SHALL consist only of upper case alphanumeric characters (0-9, A-Z) and the "-" in any
            combination.
        """
        matching_id = cls.create_random_hex().decode().upper()
        matching_id = "-".join(matching_id[i:i + 5] for i in range(0, 20, 5))
        return matching_id

    @classmethod
    def check_matching_id(cls, matching_id):
        """
            It SHALL consist only of upper case alphanumeric characters (0-9, A-Z) and the "-" in any combination.
        """
        is_matching_id_contains_under_score = "-" in matching_id
        is_matching_id_contains_upper_case = matching_id.replace("-", '').isupper()
        is_matching_id_contains_only_num_and_letter = matching_id.replace("-", '').isalnum()
        return (
                is_matching_id_contains_under_score and
                is_matching_id_contains_upper_case and
                is_matching_id_contains_only_num_and_letter
        )
