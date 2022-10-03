import datetime

import reservations.models as models
import lib.scrape as scrape
import lib.bot as bot

from django.db.models import Count, F
from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task


def update_slots(data):
    for datum in data:
        weekday: int = datum["weekday"]
        day: datetime.date = datum["day"]
        start_time: datetime.time = datum["start_time"]
        duration: datetime.datetime.timedelta = datum["duration"]
        capacity: int = datum["capacity"]
        user_ids: list[str] = datum["user_ids"]

        block, _ = models.Block.objects.get_or_create(
            weekday=weekday, start_time=start_time, duration=duration
        )
        slot, _ = models.Slot.objects.get_or_create(
            block=block, date=day, capacity=capacity
        )
        for user_id in user_ids:
            models.Reservation.objects.get_or_create(slot=slot, user_uuid=user_id)


@db_periodic_task(crontab(minute="*/1"))
def fetch_and_update_slots():
    data = scrape.fetch_data()
    update_slots(data)
    print("Updated slots")

    notify_users_open_slots()


@db_task()
def notify_users_open_slots():
    # Get available slots
    available_slots = (
        models.Reservation.objects.select_related("slot")
        .values("slot_id")
        .annotate(count=Count("slot_id"))
        .filter(count__lt=F("slot__capacity"))
        .values_list(
            "slot_id",
            "count",
            "slot__capacity",
            "slot__block__start_time",
            "slot__block_id",
            "slot__date",
        )
    )
    blocks = {}
    for slot_id, count, capacity, start_time, block_id, date in available_slots:
        if block_id not in blocks:
            blocks[block_id] = {}
        blocks[block_id][slot_id] = {
            "count": count,
            "capacity": capacity,
            "start_time": start_time,
            "date": date,
        }

    # Notify users
    for user in models.User.objects.all():
        block_ids = models.BlockPreference.objects.filter(user=user).values("id")
        results = models.Slot.objects.filter(block_id__in=block_ids).values(
            "id", "block_id"
        )
        result_list = list(results)
        if len(result_list) == 0:
            continue
        else:
            msg = []
            for slot_id, block_id in result_list:
                if block_id not in blocks:
                    continue
                d = blocks[block_id]
                msg.append(
                    f"{d['date']} {d['start_time']} {d['count']}/{d['capacity']} cupos"
                )
        if msg:
            message = "\n".join("Hay cupos disponibles:" + msg)
            bot.send_message(message, user.chat_id)
        else:
            pass
    print("Notified users")
