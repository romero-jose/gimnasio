from django.contrib import admin

from .models import Block, BlockPreference, Reservation, Slot, User


class BlockAdmin(admin.ModelAdmin):
    list_display = ("weekday", "start_time", "duration")
    ordering = ["weekday", "start_time"]
    save_as = True


admin.site.register(Block, BlockAdmin)
admin.site.register(Slot)
admin.site.register(BlockPreference)
admin.site.register(Reservation)
admin.site.register(User)
