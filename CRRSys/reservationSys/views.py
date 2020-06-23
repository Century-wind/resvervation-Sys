from django.shortcuts import render_to_response, render, redirect, HttpResponse
from .models import Room, Staff, Booking
import datetime
from datetime import timedelta
import time
import re
import json
import psutil


# 登录界面
def login_view(request):
    if request.method == 'GET':
        return render(request, 'text/login.html')

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        message = "请填写相应信息！"
        if username:
            try:
                user = Staff.objects.get(phone=username)
                if user.password == password:
                    resp = redirect('/')
                    # 加入cookie信息
                    resp.set_cookie('user', user.id)
                    return resp
                else:
                    message = "密码错误！"
            except Staff.DoesNotExist:
                message = "用户不存在！"
            return render(request, 'text/login.html', {'message': message, 'account': username})
        return render(request, 'text/login.html', {'message': message})


# 登录装饰器
def login_decor(index):  # 传入一个界面
    def wrappwer(request, *args, **kwargs):
        # 从网页请求中获取cookie
        user = request.COOKIES.get('user')
        if not user:
            return redirect('login')
        else:
            return index(request, *args, **kwargs)

    return wrappwer


# 登出
@login_decor
def logout(request):
    # 设置响应连接
    response = redirect('/')
    # 清除响应的cookie
    response.delete_cookie('user')
    # 返回响应
    return response


# 注册界面
def register(request):
    if request.method == 'GET':
        return render(request, 'text/register.html')

    elif request.method == 'POST':
        username = request.POST.get('username')  # name
        password = request.POST.get('password')
        department = request.POST.get('department')
        phone = request.POST.get('phone')   # phone
        position = request.POST.get('position')
        # 获取人脸图片信息Base64格式
        face_id = request.POST.get('face')
        # 图片转换： 提取图片数据（去除 data:image/png;base64,）
        match_index = re.search(';base64,', face_id).span()[1]
        face_id = face_id[match_index:]

        try:
            user = Staff.objects.get(phone=phone)
            if user:
                message = "用户已存在!"
                return render(request, 'text/register.html', {'message': message, 'account': phone})
        except Staff.DoesNotExist:
            Staff.objects.create(name=username, phone=phone, password=password, department=department,
                                 position=position, faceId=face_id)
            message = "注册成功，请登录！"
            return redirect('login/', {'message': message})


# 公用日历
def calender():
    days, day, wk, years = [], [], [], []
    week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fir', 'Sat', 'Sun']
    today = datetime.date.today()
    # 获取7天的星期和日期
    for i in range(7):
        dat = today + datetime.timedelta(i)
        year = dat.strftime('%Y')  # 年份
        w, ds = dat.weekday(), dat.strftime('%m %d')  # x月 x日
        # 日期int格式： 0304
        d = ds.replace(' ', '')
        days.append(ds)
        day.append(d)
        wk.append(w)
        years.append(year)

    weeks = {
        week[wk[0]]: days[0],
        week[wk[1]]: days[1],
        week[wk[2]]: days[2],
        week[wk[3]]: days[3],
        week[wk[4]]: days[4],
        week[wk[5]]: days[5],
        week[wk[6]]: days[6],
    }

    times = [
        ('09:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('10:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('11:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('12:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('13:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('14:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('15:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('16:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
        ('17:00', day[0], day[1], day[2], day[3], day[4], day[5], day[6]),
    ]

    return weeks, times, years


# 进行中的会议室
def doing_book(books):
    # 获取当前时间为标记:
    now = datetime.datetime.now()
    now_rooms_c, day_rooms_c, now_rooms, day_rooms = [], [], set(), []   # 集合：不可重复

    if books:
        for foo in books:
            # print(foo.start_time.day)
            # 所有代办预订数
            if foo.start_time > now:
                room = Room.objects.get(address=foo.rid)
                now_rooms_c.append(room)     # 所有代办预订会议室数
                now_rooms.add(room)  # 代办会议室
                # print('订单信息：%s' % room)
            # 当日代办预订会议室
            oneday = foo.start_time - now
            if oneday > timedelta(days=0) and oneday <= timedelta(days=1):
                room = Room.objects.get(address=foo.rid)
                day_rooms_c.append(room)
                # print("当日代办：")
                # print(len(day_rooms_c))
            if foo.start_time.day == now.day:
                room = Room.objects.get(address=foo.rid)
                day_rooms.append(room)
                # print(foo.start_time.day)

    return now_rooms, now_rooms_c, day_rooms_c, day_rooms


# 个人中心
@login_decor
def account(request):
    user_id = request.COOKIES.get('user')
    user = Staff.objects.get(id=user_id)

    books = Booking.objects.filter(sid=user_id)

    today = datetime.datetime.now()
    recent_books = []
    # 近日订单
    for book in books:
        if book.start_time - today > timedelta(days=0):
            recent_books.append(book)
            # print(book.start_time)

    count = len(recent_books)
    context = {
        'user': user,
        'username': user.name,
        'now_book': count,
        'counts': len(books),
        'order': recent_books,
    }

    if request.method == 'POST':
        phone = request.POST.get('phone')  # phone
        username = request.POST.get('username')  # name
        department = request.POST.get('department')
        position = request.POST.get('position')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        if gender == 'male':
            gender = True
        elif gender == 'female':
            gender = False
        Staff.objects.filter(id=user_id).update(phone=phone, name=username, department=department,
                                 position=position, password=password, gender=gender)

    return render(request, 'text/account.html', context)


# 我的订单
@login_decor
def order(request):
    user_id = request.COOKIES.get('user')
    user = Staff.objects.get(id=user_id)

    books = Booking.objects.filter(sid=user_id)

    today = datetime.datetime.now()
    recent_books = []
    # 近日订单
    for book in books:
        if book.start_time - today > timedelta(days=0):
            recent_books.append(book)
            # print(book.start_time)

    count = len(recent_books)

    context = {
        'user': user,
        'username': user.name,
        'now_book': count,
        'counts': len(books),
        'books': books,
        'order': recent_books,
    }

    return render_to_response('text/myOrder.html', context)


# 主页
def index(request):
    memory_use_rate = psutil.virtual_memory().percent  # 内存使用率
    cpu_use_rate = psutil.cpu_percent(0)
    user_id = request.COOKIES.get('user')
    books = Booking.objects.all()
    rooms = Room.objects.all()
    _, times, years = calender()
    t_data = times[0][1]
    t_data = t_data[0:2] + '月' + t_data[2:-1] + '日'

    #   待处理会议室，待处理总计数， 今日待处理数， 今日预订数
    now_rooms, rooms_count, today_rooms, day_rooms = doing_book(books)

    # 当日会议室占用率
    useage_rate = len(day_rooms)/9/len(rooms)*100
    useage_rate = format(useage_rate, '.2f')

    context = {
        'rate': useage_rate,
        'year': years[0],
        'time': t_data,  # 日期
        'count': len(books),  # 总预订数
        'rooms': now_rooms,  # 代办预订
        'rooms_count': len(rooms_count),  # 代办预订
        'today_rooms': today_rooms,  # 今日代办预订
        'now_book': len(now_rooms),  # 待处理预订数
        'cpu': cpu_use_rate,  # cpu 使用率
        'RAM': memory_use_rate,  # cpu 使用率
    }

    if user_id:
        user = Staff.objects.get(id=user_id)
        books = Booking.objects.filter(sid=user_id)

        book_cout = len(books)

        # 根据订单查已预订的房间
        now_rooms, rooms_count, _, _ = doing_book(books)

        # 数据覆盖
        context['username'] = user.name
        context['rooms'] = now_rooms
        context['count'] = book_cout    # 总预订数
        context['rooms_count'] = len(rooms_count)  # 代办预订数
        context['now_book'] = len(now_rooms)

    return render(request, 'text/index.html', context)


# 会议室
@login_decor
def meeting_room(request):
    user_id = request.COOKIES.get('user')
    user = Staff.objects.get(id=user_id)
    rooms = Room.objects.all()
    rates = []

    for room in rooms:
        books = Booking.objects.filter(rid=room.id)
        # 今日预订数
        _, _, day_rooms, _ = doing_book(books)
        # print(day_rooms)
        rate = format((len(day_rooms)/9.00*100), '.1f')
        rates.append(rate)
    room_rate_zip = zip(rooms, rates)

    context = {
        'dates': room_rate_zip,
        'username': user.name,
    }
    return render_to_response('text/tables.html', context)


# 预订页面
@login_decor
def detail(request, room_id):
    user_id = request.COOKIES.get('user')
    user = Staff.objects.get(id=user_id)
    room_detail = Room.objects.get(id=room_id)

    # 获取星期和日期
    weeks, times, _ = calender()

    # 获取该房间所有订单
    books = Booking.objects.filter(rid=room_id)

    # 获取当前时间
    now = datetime.datetime.now()
    book_times = set()  # 集合：不可重复
    book_times_t = set()
    book_times_d = set()

    if books:
        # print(books)
        for foo in books:
            # print(foo.start_time)
            if foo.start_time > now:
                # print('订单信息：%s' % foo.start_time)
                # print(str(foo.start_time)[-8:-3])
                book_time_t = str(foo.start_time)[-8:-3]
                book_time_d = str(foo.start_time)[5:10].replace("-", '')
                # print(str(foo.start_time)[5:10].replace("-", ''))
                # 已有预订时间点
                book_times.add(foo.start_time)
                # 已有预订时间点 时间 和 日期
                book_times_t.add(book_time_t)
                book_times_d.add(book_time_d)

    context = {
        'book_times': book_times,   # 已有预订点
        'book_times_t': book_times_t,   # 已有预订点
        'book_times_d': book_times_d,   # 已有预订点


        'js_book_dates': json.dumps(list(book_times_d)),   # 已有预订点
        'js_book_times': json.dumps(list(book_times_t)),  # 已有预订点


        'room_detail': room_detail,
        'time': times,
        'weeks': weeks,
        'username': user.name,
    }
    return render_to_response('text/detail.html', context)

# 预订页面2
@login_decor
def book(request, room_id, data_id, time_id):
    user_id = request.COOKIES.get('user')
    user = Staff.objects.get(id=user_id)
    room_book = Room.objects.get(id=room_id)

    _, times, years = calender()
    num = times[0].index(data_id)
    year = years[num-1]

    message = []

    if request.method == 'POST':
        rid = Room.objects.get(id=room_id)
        sid = Staff.objects.get(id=user_id)
        start_time = time.strptime(year + data_id + time_id, "%Y%m%d%H:%M")
        start_time_d = datetime.datetime.fromtimestamp(time.mktime(start_time))
        end_time = time.strptime(year + data_id + request.POST['end_time'], "%Y%m%d%H:%M")
        end_time_d = datetime.datetime.fromtimestamp(time.mktime(end_time))
        theme = request.POST['theme']
        note = request.POST['note']

        Booking.objects.create(rid=rid, sid=sid, theme=theme, note=note, start_time=start_time_d, end_time=end_time_d)
        message = ':预约成功！'

    context = {
        'message': message,
        'room': room_book,
        'time': time_id,
        'username': user.name,

    }
    return render(request, 'text/book.html', context)

