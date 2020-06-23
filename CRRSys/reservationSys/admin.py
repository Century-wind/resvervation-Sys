from django.contrib import admin
from .models import Staff, Room, Booking
# Register your models here.

# 注册管理目标页面
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'phone', 'create_date',
                    'department', 'position', 'password')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'state', 'info')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'rid', 'theme', 'order_time', 'start_time',
                    'end_time', 'note')

    list_filter = ['rid']

