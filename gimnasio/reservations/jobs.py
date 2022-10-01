import datetime

import lib.scrape as scrape
import reservations.models as models


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


def fetch_and_update_slots():
    data = scrape.fetch_data()
    update_slots(data)
