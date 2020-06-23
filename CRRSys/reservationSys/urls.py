#! /home/hang/anaconda3/bin/python
# encoding: utf-8
# @author: hang(@century wind)
# @email: 1789533256@qq.com
# @project: Project/urls.py
# @time: 20-2-23 下午5:41
# @about: 


from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('meeting-room', views.meeting_room, name='meeting_room'),
    path('login/', views.login_view, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('account', views.account, name='account'),
    path('order', views.order, name='order'),
    path('detail/<int:room_id>', views.detail, name='detail'),
    # 正则路径表示法
    re_path('detail/(?P<room_id>[0-9])/(?P<data_id>[0-9]{4})/(?P<time_id>[0-9]{2}:00)/', views.book, name='book')
]
