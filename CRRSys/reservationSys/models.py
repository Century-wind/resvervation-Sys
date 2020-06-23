
# Create your models here.
from django.db import models
from datetime import datetime


class Staff(models.Model):
    name = models.CharField(u'姓名', max_length=24)
    gender = models.BooleanField(u'性别', default=True)
    phone = models.CharField(u'联系方式', max_length=24)  # ->账号
    create_date = models.TimeField(u'创建时间', default=datetime.now())
    department = models.CharField(u'公司部门', max_length=200)
    position = models.CharField(u'职位', max_length=24)
    password = models.CharField(u'密码', max_length=24)
    faceId = models.TextField(u'人脸信息', max_length=131070, default=0)

    # 设置元信息
    '''
    元数据是指“所有不是字段的东西”，
    比如排序选项（attr:~Options.ordering），
    数据库表名（db_table），
    或是人可读的单复数名（verbose_name 和 verbose_name_plural）。
    '''
    class Meta:
        # 数据库表名
        db_table = "Staff"
        # 页面表名
        verbose_name_plural = '用户信息'

    def __str__(self):
        return str(self.name)


class Room(models.Model):
    address = models.CharField(u'会议室地址', max_length=8)
    state = models.BooleanField(u'会议室状态', default=0)
    info = models.CharField(u'会议室信息', max_length=24, default='小型会议室')

    class Meta:
        db_table = "Room"
        verbose_name_plural = '会议室信息'

    def __str__(self):
        return str(self.address)


class Booking(models.Model):
    sid = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name="员工编号")
    rid = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="会议室编号")
    theme = models.CharField(u'会议主题', max_length=200)
    order_time = models.DateTimeField(u'预订时间', default=datetime.now())
    start_time = models.DateTimeField(u'开始时间')
    end_time = models.DateTimeField(u'结束时间')
    note = models.CharField(u'备注信息', max_length=200)

    class Meta:
        db_table = "Booking"
        verbose_name_plural = '订单信息'

    def __str__(self):
        return str(self.theme)
