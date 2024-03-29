from django.db import models
from financial_companion.models import User
import os
from financial_companion.helpers import random_filename


def change_filename(instance, filename) -> str:
    """Returns filepath with random filename for file to be stored"""
    return os.path.join('group_profile', random_filename(filename))


class UserGroup(models.Model):
    """Group model used for different groups"""
    name: models.CharField = models.CharField(max_length=50, blank=False)
    description: models.CharField = models.CharField(
        max_length=500, blank=False)
    owner_email: models.EmailField = models.EmailField(blank=False)
    invite_code: models.CharField = models.CharField(
        max_length=8, blank=False, unique=True)
    members: models.ManyToManyField = models.ManyToManyField(User)
    group_picture: models.ImageField = models.ImageField(
        upload_to=change_filename,
        height_field=None,
        width_field=None,
        max_length=100,
        blank=True)

    def add_member(self, user: User) -> None:
        """Adds user to group list"""
        self.members.add(user)

    def remove_member(self, user: User) -> None:
        """Removes user from group list"""
        self.members.remove(user)

    def is_member(self, user: User) -> bool:
        """Returns whether user is in the group"""
        return user in self.members.all()

    def members_count(self) -> int:
        """Returns number of members in the group"""
        return self.members.count()

    def get_members(self) -> str:
        """Returns string list of members in the group"""
        members_of_group: list[User] = self.members.all()
        return ",".join([str(p) for p in members_of_group])

    def make_owner(self, user: User) -> None:
        """Sets input user as group owner"""
        self.owner_email = user.email
        self.save()
