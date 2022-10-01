from calendar import FRIDAY, SATURDAY, SUNDAY, THURSDAY, TUESDAY, WEDNESDAY
from enum import unique
from django.utils.translation import gettext_lazy as _
from django.db import models

# Create your models here.
# blocks, slots, reservations, users, preferred_blocks

TIME_FORMAT = "%H:%M"


class Weekday(models.IntegerChoices):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class Block(models.Model):
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    duration = models.DurationField()

    def __str__(self):
        weekday: str = self.get_weekday_display()
        start_time = self.start_time.strftime(TIME_FORMAT)
        return f"{weekday} {start_time}"

    class Meta:
        unique_together = ("weekday", "start_time")
        db_table = "block"


class Slot(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    date = models.DateField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.date.isoformat()} {self.block}"

    class Meta:
        unique_together = ("block", "date")
        db_table = "slot"


class Reservation(models.Model):
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    user_uuid = models.UUIDField()

    def __str__(self):
        return f"{self.slot} {self.user_uuid}"

    class Meta:
        unique_together = ("slot", "user_uuid")
        db_table = "reservation"


class User(models.Model):
    chat_id = models.TextField(unique=True)
    ucampus_uuid = models.UUIDField()
    name = models.TextField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "user"


class BlockPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {self.block}"

    class Meta:
        unique_together = ("user", "block")
        db_table = "block_preference"
