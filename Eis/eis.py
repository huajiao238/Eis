"""
@create by PyCharm
@author      : 西藏恰成信息工程有限公司
@filename    : eis.py
@create_time : 2021-05-21
@contact : TEL:0891-6579668   PHONE:18076986378  WECHART&QQ:1032601165
"""

import tkinter as tk
from netmiko import ConnectHandler, SSHDetect
import os
import re
from tkinter.filedialog import askopenfilename
import tkinter.messagebox


class Eis(object):
    def __init__(self):
        # if True:
        #     Login()
        #     return
        self.msg = tkinter.messagebox
        self.window = tk.Tk()
        self.window.title('雅合博网络设备自动化巡检系统')
        self.window.iconbitmap('.\\common/logo.ico')
        self.window.resizable(0, 0)
        self.set_window_center(800, 800)
        self.window.update()
        # 多设备文件路径
        self.filepath = tk.StringVar(value='请选择保存有设备IP、用户名及密码的文本文档')
        # 单设备巡检IP
        self.danip = tk.StringVar(value='请输入设备IP地址')
        # 单设备巡检用户名
        self.username = tk.StringVar(value='请输入用户名')
        # 单设备巡检密码
        self.password = tk.StringVar(value='请输入密码')
        # 单设备巡检设备类型
        self.shebei = tk.StringVar(value='请输入设备类型，不支持中文，或删除这段话后留空。')
        tk.Entry(self.window, textvariable=self.filepath, width=80).place(x=100, y=15)
        tk.Label(self.window, text='多设备巡检：').place(x=10, y=15)
        # 信息显示框
        self.text = tk.Text(self.window, height=34, width=120, bg='blue', fg='white', padx=20, pady=20)
        self.text.place(x=0, y=320)
        # 文件选择按钮
        tk.Button(self.window, text='选择文件', width=10, height=1, command=self.select_path).place(x=690, y=10)
        # 多设备巡检开始按钮
        tk.Button(self.window, text='立即巡检', width=20, height=1, command=self.check).place(x=300, y=50)
        tk.Label(self.window, text='单设备巡检：').place(x=10, y=120)
        # 单设备IP输入框
        tk.Entry(self.window, textvariable=self.danip, width=50).place(x=200, y=120)
        # 单设备用户名输入框
        tk.Entry(self.window, textvariable=self.username, width=50).place(x=200, y=160)
        # 单设备密码输入框
        tk.Entry(self.window, textvariable=self.password, width=50).place(x=200, y=200)
        # 单设备类型输入框
        tk.Entry(self.window, textvariable=self.shebei, width=50).place(x=200, y=240)
        # 单设备巡检按钮
        tk.Button(self.window, text='立即巡检', width=20, height=1, command=self.inspection).place(x=300, y=280)
        # 清空控制台按钮
        tk.Button(self.window, text='清空控制台', width=10, height=1, command=self.clear_console).place(x=680, y=740)
        self.window.mainloop()

    # 消息提示
    def alert_info(self, title, msg):
        self.msg.showinfo(title, msg)

    # 错误提示
    def alert_error(self, title, msg):
        self.msg.showerror(title, msg)

    # 警告提示
    def alert_warn(self, title, msg):
        self.msg.showwarning(title, msg)

    # 窗口居中弹出
    def set_window_center(self, curwidth, curheight):
        if not curwidth:
            curwidth = self.window.winfo_width()
        if not curheight:
            curheight = self.window.winfo_height()
        # 获取屏幕宽度和高度
        scn_w, scn_h = self.window.maxsize()
        # 计算中心坐标
        cen_x = (scn_w - curwidth) / 2
        cen_y = (scn_h - curheight) / 2
        # 设置窗口初始大小和位置
        size_xy = '%dx%d+%d+%d' % (curwidth, curheight, cen_x, cen_y)
        self.window.geometry(size_xy)

    # 设备文件选择
    def select_path(self):
        path = askopenfilename(title='请选择设备文件', filetypes=[('TXT', '*.txt')])
        self.filepath.set(path)

    # 多设备巡检
    def check(self):
        path = self.filepath.get()
        if path == '请选择保存有设备IP、用户名及密码的文本文档' or path == '':
            tkinter.messagebox.showerror('错误', '请选择设备文件！！')
            return
        with open(path, encoding='utf-8') as device_list:
            device = device_list.readlines()
        for line in device:
            line = line.strip("\n")
            ipaddr = line.split(",")[0]
            user = line.split(",")[1]
            pwd = line.split(",")[2]
            device_type = line.split(",")[3]
            if device_type == '':
                self.text.insert('insert', '正在判断设备类型\n\n')
                self.text.update()
                self.text.see(tk.END)
                device_type = self.detect_device(ip=ipaddr, user=user, pwd=pwd)  # 自动发现设备类型
                self.text.insert('insert', '设备类型为：' + device_type + '\n\n')
                self.text.update()
                self.text.see(tk.END)
            self._connect(device_type=device_type, ip=ipaddr, user=user, pwd=pwd)
        self.text.insert('insert', '巡检完毕\n\n')
        self.text.update()
        self.text.see(tk.END)
        self.alert_info(title='巡检完毕', msg='大功告成，人生苦短，我用Python！')

    # 单设备巡检
    def inspection(self):
        ip = self.danip.get()
        user = self.username.get()
        pwd = self.password.get()
        device_type = self.shebei.get()
        if ip == '请输入设备IP地址' or ip == '':
            self.alert_error(title='错误', msg='请输入IP地址！！')
            return
        elif user == '请输入用户' or user == '':
            self.alert_error(title='错误', msg='请输入ssh用户名！！')
            return
        elif pwd == '请输入密码' or pwd == '':
            self.alert_error(title='错误', msg='请输入ssh用户密码！！')
            return
        elif device_type == '请输入设备类型，不支持中文，或删除这段话后留空。':
            self.alert_error(title='错误', msg='请输入正确的设备类型或留空')
            return
        elif device_type == '':
            self.text.insert('insert', '正在判断设备类型\n\n')
            self.text.update()
            self.text.see(tk.END)
            device_type = self.detect_device(ip=ip, user=user, pwd=pwd)  # 自动发现设备类型
            self.text.insert('insert', '设备类型为：' + device_type + '\n\n')
            self.text.update()
            self.text.see(tk.END)
        # 执行操作
        self._connect(device_type=device_type, ip=ip, user=user, pwd=pwd)
        self.text.insert('insert', '巡检完毕\n\n')
        self.text.update()
        self.text.see(tk.END)
        self.alert_info(title='巡检完毕', msg='大功告成，人生苦短，我用Python！')

    # 清空控制台
    def clear_console(self):
        self.text.delete('1.0', 'end')

    # 设备自动发现
    def detect_device(self, ip, user, pwd):
        device = {
            'device_type': 'autodetect',
            'host': ip,
            'username': user,
            'password': pwd
        }
        _detect = SSHDetect(**device)
        device_type = _detect.autodetect()
        return device_type

    # ssh连接并执行命令
    def _connect(self, device_type, ip, user, pwd):
        device = {  # 连接信息
            'device_type': device_type,
            'ip': ip,
            'username': user,
            'password': pwd,
        }
        # 判断ip是否合法
        if not re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                        device['ip']):
            self.alert_error(title='错误', msg='IP地址不合法：' + ip)
            return
        # 判断设备类型是否存在
        if not self.type_check(device_type=device['device_type']):
            self.alert_error(title='错误', msg='设备类型不支持，请检查后重试')
            return
        # 根据设备类型加载命令文件
        command_files = 'command/' + device_type + '.txt'
        self.text.insert('insert', '正在连接：' + ip + '\n\n')
        self.text.update()
        self.text.see(tk.END)
        # 连接设备
        try:
            connect = ConnectHandler(**device)
            connect.enable()
            with open(command_files, encoding='utf-8') as command_file:
                command_list = command_file.readlines()
            command_file.close()
            # 循环执行命令
            for command in command_list:
                line = command.strip("\n")
                # 字符串分片，提取命令
                command = line.split(":")[0]
                # 字符串分片提取备注
                vendor = line.split(':')[1]
                self.text.insert('insert', '正在' + vendor + '\n')
                self.text.update()
                self.text.see(tk.END)
                # 获取设备返回信息
                output = connect.send_command(command, strip_command=False, strip_prompt=False)
                if re.search('found at|detected at', output):
                    self.text.insert('insert', '命令"' + command + '"执行失败\n\n')
                    continue
                self.text.insert('insert', '正在保存文件\n')
                self.text.update()
                self.text.see(tk.END)
                logpath = 'inspection/' + device_type + '/' + ip
                # 判断路径是否存在
                if not os.path.exists(logpath):
                    os.makedirs(logpath)  # 如果不存在则创建相关目录
                #  将设备返回信息写入文件内
                f = open('inspection/' + device_type + '/' + ip + '/' + vendor + '.txt', 'w')
                f.write(output)
                f.close()
                self.text.insert('insert', '文件保存成功\n\n')
                self.text.update()
                self.text.see(tk.END)
            connect.disconnect()
        except:
            self.text.insert('insert', ip + '连接失败,请检查ip、用户名及密码是否正确\n\n')

    # 判断设备类型
    def type_check(self, device_type):
        with open('common/device_type.txt') as f:
            data = f.read().splitlines()
        f.close()
        # print(data)
        if device_type in data:
            return True
        else:
            return False


if __name__ == '__main__':
    Eis()
