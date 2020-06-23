#! /home/hang/anaconda3/bin/python
# encoding: utf-8
# @author: hang(@century wind)
# @email: 1789533256@qq.com
# @project: 预订系统/face.py
# @time: 20-4-19 下午1:40
# @about: 人脸识别
import pymysql
import time
import datetime
import base64
import cv2 as cv
import face_recognition as fr


# 绑定会议室id,获取数据库订单
def room_bind(id):
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "hang", "reserSys")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL 查询
    sql = "SELECT * FROM Booking WHERE rid_id=%d" % id
    cursor.execute(sql)
    # 使用 fetchall() 方法获取所有数据.
    datas = cursor.fetchall()
    # 获取当前时间点
    now = datetime.datetime.now()
    # 设置预订者ID
    userid = 0
    for data in datas:
        s_time, e_time, sid = data[-5], data[-4], data[-1]
        c_time = s_time - datetime.timedelta(minutes=15)
        # 当前时间大于会前15分钟并小于会议结束时间
        if (c_time <= now) and e_time > now:
            # print(sid)
            userid = sid
    # 关闭数据库连接
    db.close()
    return userid


# 获取数据库face
def data_acquisition(userid):
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "hang", "reserSys")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL 查询
    sql = "SELECT * FROM Staff WHERE id=%d" % userid
    cursor.execute(sql)
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    name, face = data[1], data[-1]
    # 关闭数据库连接
    db.close()
    return name, face


# 转换为图片:输入姓名和人脸数据
def date_img(name, data):
    data_len = len(data) % 4
    if data_len != 0:
        data += '=' * (4 - data_len)

    # 二进制图片数据编译
    img_data = base64.b64decode(data)

    with open('static/faceImg/' + name + '.png', 'wb') as f:
        f.write(img_data)


def face_compare(url, knowned_name):
    # 1. 获取图片
    face = cv.imread(url)

    # 人脸编码
    face_encoding = fr.face_encodings(face)

    if len(face_encoding) > 0:
        print("人脸信息已录入")
        face_encoding = face_encoding[0]
    else:
        print('Face Not found')

    # 建立人脸库和对应的名字库
    known_face_encodings = [face_encoding, ]
    known_face_names = [knowned_name, ]

    # 1.1 创建视频捕获对象
    vc = cv.VideoCapture(0)

    # 1.2 使用循环不断捕获
    while True:
        ret, img = vc.read()
        if not ret:
            print("没有捕获到！")
            break
        # 获取人脸位置
        locations = fr.face_locations(img=img, number_of_times_to_upsample=1, model='hog')
        # 未知人脸编码
        unface_encoding = fr.face_encodings(img, locations, 50)

        # 设置解锁旗 flag
        flag = 0
        # 取脸识别
        for (top, right, bottom, left), face_encode in zip(locations, unface_encoding):
            # 用以上数据画方框
            cv.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
            # 匹配识别人脸
            matchs = fr.compare_faces(known_face_encodings, face_encode)
            name = 'unknown'
            for match, known_name in zip(matchs, known_face_names):
                if match:
                    name = known_name
                    print("解锁")
                    flag = 1
                    break

            # 标记名字
            cv.putText(img, name, (left, top-20), cv.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (0, 0, 255), 2)

        cv.imshow('face', img)

    # 3. 等待键盘事件
        if cv.waitKey(1) != -1 or flag:
            time.sleep(6)
            # 关闭摄像头
            vc.release()
            # 4. 销毁窗口
            cv.destroyAllWindows()
            break


if __name__ == '__main__':
    try:
        s_id = room_bind(2)
        print('用户id：%d' % s_id)
        face_name, face_data = data_acquisition(s_id)
        print(face_name)
        date_img(face_name, face_data)
        url = 'static/faceImg/' + face_name + '.png'
        face_compare(url, face_name)
    except TypeError:
        print("该会议室此刻没有预订用户！")
    except base64.binascii.Error:
        print("没有人脸信息")


