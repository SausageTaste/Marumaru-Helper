# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'marumaru_helper_gui_v3.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!


import os
import sys
import time
import json
import random
import shutil
import socket
import datetime
import functools
import traceback
import webbrowser
import urllib.error as ue
import urllib.request as ur

import win32api
from PIL import Image
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread

import marumaru as m


try:
    _fromUtf8 = QtCore.QString.fromUtf8
    pass
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


BFONT = QtGui.QFont()
BFONT.setFamily("Malgun Gothic")
BFONT.setPointSize(9)

DATA_FOL_LOC_S = "marumaru_helper_v3\\"
SAVE_TXT_S = DATA_FOL_LOC_S + "data"
SAVE_JSON_S = DATA_FOL_LOC_S + "data.json"
CONFIG_TXT_S = DATA_FOL_LOC_S + "config"
THUMB_FOL_S = DATA_FOL_LOC_S + "thumbnail\\"
BACKUP_FOL_S = DATA_FOL_LOC_S + "backup\\"
LOG_FOL_S = DATA_FOL_LOC_S + "log\\"
LANG_FOL_S = DATA_FOL_LOC_S + "language\\"
UI_DIR_S = LANG_FOL_S + "{}\\ui.txt"
ST_DIR_S = LANG_FOL_S + "{}\\st.txt"

TRY_I = 1
DEFAULT_LANG_S = "korean"

DEFAULT_ENCODING_S = "cp1252"
CONTAINER_T = ("()", "[]", "{}", "〔〕", "<>", "《》", "「」", "『』", "【】", "□□", "■■", "◁▷", "◀▶", "‘’", "“”")

socket.setdefaulttimeout(10)


class WTF(Exception):
    def __init__(self, text:str=''):
        self.text = ''
        self.list = []

        if isinstance(text, list):
            self.list = text
        else:
            self.text = str(text)

    def __str__(self):
        if self.text:
            return self.text
        elif self.list:
            string = ''
            for x_s in self.list:
                string += "{}\n".format(x_s)
            return string
        else:
            return "wtf??"


######## Functions ########

#### Pasted functions ####

def clear_dirt_way(dirt:str) -> None:
    folder_list = []
    for x_str in dirt.split('\\'):
        if x_str:
            folder_list.append(x_str)

    if folder_list[0].endswith(':'):
        work_dirt = folder_list.pop(0) + '\\'
    else:
        work_dirt = ''

    for x_str in folder_list:
        work_dirt += "{}\\".format(x_str)
        if not os.path.isdir(work_dirt):
            os.mkdir(work_dirt)

def url_urllib_html(url_s:str) -> str:
    opener = ur.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                          '(KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    ur.install_opener(opener)

    page = ur.urlopen(url_s)
    html_b = page.read()
    html_s = html_b.decode('utf8')
    return html_s

####  ####

def mk_log_name(type_s:str) -> str:
    for x in range(1, 10000):
        name_s = "log-{}-{:0>4}".format(type_s, x)
        for y_s in os.listdir(LOG_FOL_S):
            tail_cut = y_s.rindex('-')
            if name_s == y_s[:tail_cut]:
                break
        else:
            return name_s + "-{}".format(int(time.time()))

def load_txt_data_gen() -> iter:
    clear_dirt_way(DATA_FOL_LOC_S)
    try:
        file = open(SAVE_TXT_S, 'r', encoding="utf8")
    except FileNotFoundError:
        file = open(SAVE_TXT_S, 'w', encoding="utf8")
        file.close()
        return []
    else:
        save_s = file.read()
        file.close()

        save_s = save_s.lstrip('\ufeff')
        manga_data_l = save_s.split("\n%divider%\n")
        for x_s in manga_data_l:
            return_l = []
            if len(x_s) < 10:
                continue
            x_s = x_s.strip('<')
            element_l = x_s.split('<')

            assert len(element_l) == 10
            if element_l[8] == "True":
                continue

            return_l.append(int(element_l[0]))  # number
            return_l.append(element_l[2])  # url
            return_l.append(element_l[3])  # thum url
            return_l.append(element_l[4])  # title

            chapter_l = []
            element_l[5] = element_l[5].strip('>')
            for y_s in element_l[5].split('>'):
                chel = y_s.split('|')
                try:
                    a_tuple = (int(chel[0]), chel[1], chel[2], int(chel[3]))
                except ValueError:
                    pass
                else:
                    chapter_l.append(a_tuple)
            return_l.append(chapter_l)

            return_l.append(int(element_l[6]))  # last up
            for y_s in element_l[7:]:
                if y_s == "True":
                    return_l.append(True)
                elif y_s == "False":
                    return_l.append(False)
                else:
                    raise WTF

            if len(return_l) == 9:
                yield return_l
            else:
                print("Error occured during loading.")
                output_s = "Error occured during loading.\n"
                for y, y_el in enumerate(return_l):
                    output_s += "{} : {}".format(y, y_el)

                clear_dirt_way(LOG_FOL_S)
                file_name = "{}{}.txt".format(LOG_FOL_S, mk_log_name("LoadingError"))
                with open(file_name, 'w', encoding="utf8") as f:
                    f.write(output_s)

def load_txt_data_sorted_gen() -> iter:
    title_l = []
    for x_l in load_txt_data_gen():
        title_l.append(x_l[3])
    title_l.sort()
    for x_s in title_l:
        for y_l in load_txt_data_gen():
            if x_s == y_l[3]:
                yield y_l

def load_config_dict() -> dict:
    with open(CONFIG_TXT_S, 'r', encoding="utf8") as file:
        read_data_l = file.readlines()

    a_dict = {}
    for x_s in read_data_l:
        x_s = x_s.rstrip('\n')
        try:
            cut_index = x_s.index(" : ")
        except ValueError:
            pass
        else:
            key_s = x_s[:cut_index]
            value_part_s = x_s[cut_index + 3:]
            if value_part_s == "True":
                value = True
            elif value_part_s == "False":
                value = False
            elif value_part_s.isnumeric():
                value = int(value_part_s)
            else:
                value = value_part_s.strip('"')

            a_dict[key_s] = value

    return a_dict

def resize_keep_aspect(std_width, std_height, width:int, height:int) -> tuple:
    std_ratio_f = std_height / std_width
    input_ratio_f = height / width
    if std_ratio_f > input_ratio_f:
        return_height = int((std_width / width)*height)
        return std_width, return_height
    elif std_ratio_f < input_ratio_f:
        return_width = int((std_height / height) * width)
        return return_width, std_height
    else:
        return std_width, std_height

def sec_to_string(sec:int) -> tuple:
    unit_t =       ("s", "m", "h", "d")
    unit_scale_t = ( 1,    60,   60,     24)

    cur_num_i = sec
    cur_unit_s = "s"
    for x in range(len(unit_scale_t)):
        x_unit_s = unit_t[x]
        x_unit_scale_i = unit_scale_t[x]

        if cur_num_i // x_unit_scale_i > 0:
            cur_unit_s = x_unit_s
            cur_num_i = cur_num_i // x_unit_scale_i
        else:
            break

    return cur_num_i, cur_unit_s

def is_new(the_time_i:int) -> bool:
    if time.time() - the_time_i < 60 * 60 * 12:
        return True
    else:
        return False

def get_backup_file_list() -> list:
    try:
        return os.listdir(BACKUP_FOL_S)
    except:
        return []

def load_txt_into_dict(file_dir:str) -> dict:
    try:
        file = open(file_dir, 'r', encoding="utf8")
    except UnicodeDecodeError:
        file = open(file_dir, 'r')
    else:
        read_data_l = file.readlines()

    a_dict = {}
    for x_s in read_data_l:
        x_s = x_s.rstrip('\n')
        x_s = x_s.lstrip('\ufeff')
        try:
            cut_index = x_s.index(":")
        except ValueError:
            pass
        else:
            key_s = x_s[:cut_index]
            key_s = key_s.strip()
            value_part_s = x_s[cut_index + 1:]
            value_part_s = value_part_s.strip()

            if value_part_s == "True":
                value = True
            elif value_part_s == "False":
                value = False
            elif value_part_s.isnumeric():
                value = int(value_part_s)
            elif value_part_s.startswith('"') and value_part_s.endswith('"'):
                value = value_part_s[1:-1]
                temp_l = value.split("\\n")
                value = '\n'.join(temp_l)
            else:
                prints("failed to convert str into value : {}".format(repr(x_s)))

            a_dict[key_s] = value

    return a_dict

def split_command(command_line:str) -> list:
    command_l = command_line.split(' ')

    final_l = []
    working_bock_b = False
    a_block_l = []
    for x_s in command_l:
        if working_bock_b:
            a_block_l.append(x_s)
            if x_s.endswith('"'):
                final_l.append(' '.join(a_block_l).strip('"'))
                a_block_l = []
                working_bock_b = False
        else:
            if x_s.startswith('"'):
                working_bock_b = True
                a_block_l.append(x_s)
                if x_s.endswith('"'):
                    final_l.append(' '.join(a_block_l).strip('"'))
                    a_block_l = []
                    working_bock_b = False
            else:
                final_l.append(x_s)
    if working_bock_b:
        raise WTF

    return final_l

def print_or_export(option:int=0) -> None:
    if option == 1:
        file_option = open("marumaru_helper_v3 printed.txt", 'w', encoding="utf8")
    else:
        file_option = None

    for x_l in load_txt_data_sorted_gen():
        number_i, url_s, thum_url_s, title_s, chapter_l, last_up_i, search_flag, delete_flag, show_all_flag = x_l
        printed = False
        for y_t in chapter_l:
            read_i, chap_name_s, chap_url_s, first_fetched_i = y_t
            if not read_i:
                if not printed:
                    print('\n', file=file_option)
                    print(title_s, file=file_option)
                    print(url_s, file=file_option)
                    printed = True
                print(file=file_option)
                print("\t" + chap_name_s, file=file_option)
                print("\t" + chap_url_s, file=file_option)

def check_data() -> bool:
    first_time = False

    data = __import__("marumaru_helper_v3_data", fromlist=["marumaru_helper_v3_data"])

    if not os.path.isdir(DATA_FOL_LOC_S):
        first_time = True
        os.mkdir(DATA_FOL_LOC_S)

    if not os.path.isfile(SAVE_TXT_S):
        with open(SAVE_TXT_S, 'w', encoding="utf8") as file:
            if first_time:
                file.write(data.SAVE_DATA_S)
            else:
                pass

    if not os.path.isfile(CONFIG_TXT_S):
        with open(CONFIG_TXT_S, 'w', encoding="utf8") as file:
            file.write(data.CONFIG_S)

    if not os.path.isdir(LANG_FOL_S):
        os.mkdir(LANG_FOL_S)

    if not os.path.isdir(LANG_FOL_S + DEFAULT_LANG_S):
        os.mkdir(LANG_FOL_S + DEFAULT_LANG_S)

    if not os.path.isfile(UI_DIR_S.format(DEFAULT_LANG_S)):
        with open(UI_DIR_S.format(DEFAULT_LANG_S), 'w', encoding="utf8") as file:
            file.write(data.KOREAN_UI_S)

    if not os.path.isfile(ST_DIR_S.format(DEFAULT_LANG_S)):
        with open(ST_DIR_S.format(DEFAULT_LANG_S), 'w', encoding="utf8") as file:
            file.write(data.KOREAN_ST_S)

    del data
    print("finished data check")

    return first_time

def prints(*args):
    args = list(map(lambda x: x.__str__(), args))
    text_s = ' '.join(args)
    try:
        print(text_s)
    except UnicodeDecodeError:
        print(text_s.encode("utf8", errors="ignore").decode(encoding=DEFAULT_ENCODING_S, errors="ignore"))

######## Classes ########


class UiMainWindow(QtGui.QMainWindow):
    def __init__(self, MainWindow):
        super().__init__()

        self.first_time_b = check_data()

        ######## ui ########

        self.MainWindow = MainWindow

        self.MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.MainWindow.resize(1000, 600)

        self.centralwidget = QtGui.QWidget(self.MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        self.central_grid = QtGui.QGridLayout(self.centralwidget)
        self.central_grid.setObjectName(_fromUtf8("central_grid"))

        self.scrollArea = QtGui.QScrollArea(self.centralwidget)
        self.scrollArea.setMinimumSize(QtCore.QSize(400, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))

        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 706, 367))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))

        self.scroll_con_grid = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.scroll_con_grid.setObjectName(_fromUtf8("scroll_con_grid"))

        self.list_view = QtGui.QListView(self.centralwidget)
        self.list_view.setObjectName(_fromUtf8("list_view"))
        self.list_view.setMaximumSize(QtCore.QSize(16777215, 170))
        self.central_grid.addWidget(self.list_view, 2, 0, 1, 1)

        self.model = QtGui.QStandardItemModel()

        self.label_divider = QtGui.QLabel(self.centralwidget)
        self.label_divider.setObjectName(_fromUtf8("label_divider"))
        self.central_grid.addWidget(self.label_divider, 3, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.central_grid.addWidget(self.scrollArea, 4, 0, 1, 1)

        self.label_1 = QtGui.QLabel(self.centralwidget)
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.central_grid.addWidget(self.label_1, 1, 0, 1, 1)

        self.ver_lay_btn_place = QtGui.QVBoxLayout()
        self.ver_lay_btn_place.setObjectName(_fromUtf8("ver_lay_btn_place"))
        self.central_grid.addLayout(self.ver_lay_btn_place, 1, 1, 1, 1)

        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.central_grid.addWidget(self.progressBar, 5, 0, 1, 1)

        self.btn_search = QtGui.QPushButton(self.centralwidget)
        self.btn_search.setObjectName(_fromUtf8("btn_search"))
        self.central_grid.addWidget(self.btn_search, 5, 1, 1, 1)

        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.central_grid.addWidget(self.lineEdit, 0, 0, 1, 1)

        self.btn_add = QtGui.QPushButton(self.centralwidget)
        self.btn_add.setObjectName(_fromUtf8("btn_add"))
        self.central_grid.addWidget(self.btn_add, 0, 1, 1, 1)

        self.btn_option = QtGui.QPushButton(self.centralwidget)
        self.btn_option.setObjectName(_fromUtf8("btn_option"))
        self.central_grid.addWidget(self.btn_option, 1,1,1,1)

        self.MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 830, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.MainWindow.setStatusBar(self.statusbar)

        ######## member variables ########

        ######## function call ########

        self.init()
        self.retranslateUi()
        self.connect_sig()

        ########

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def retranslateUi(self):
        self.MainWindow.setWindowTitle(_translate("MainWindow", self.data.ld_ui_get_a_value("main-window"), None))

        ######## btn ########
        self.btn_search.setFont(BFONT)
        self.btn_search.setText(_translate("MainWindow", self.data.ld_ui_get_a_value("main-btn_search"), None))
        self.btn_add.setFont(BFONT)
        self.btn_add.setText(_translate("MainWindow", self.data.ld_ui_get_a_value("main-btn_add"), None))
        self.btn_option.setFont(BFONT)
        self.btn_option.setText(_translate("MainWindow", self.data.ld_ui_get_a_value("main-btn_option"), None))

        ######## etc ########
        self.lineEdit.setFont(BFONT)
        self.label_1.setFont(BFONT)
        self.label_1.setText(_translate("MainWindow", self.data.ld_ui_get_a_value("main-label_1"), None))

        ######## tooltip ########
        QtGui.QToolTip.setFont(BFONT)
        self.btn_add.setToolTip(self.data.ld_ui_get_a_value("main-btn_add-tooltip"))
        self.btn_search.setToolTip(self.data.ld_ui_get_a_value("main-btn_search-tooltip"))

        self.lineEdit.setToolTip(self.data.ld_ui_get_a_value("main-lineEdit-tooltip"))
        self.list_view.setToolTip(self.data.ld_ui_get_a_value("main-list_view-tooltip"))
        self.progressBar.setToolTip(self.data.ld_ui_get_a_value("main-progressBar-tooltip"))

    def connect_sig(self):
        self.btn_add.clicked.connect(self.btn_add_f)
        self.btn_option.clicked.connect(self.option_window)
        self.btn_search.clicked.connect(self.btn_search_f)

        self.lineEdit.returnPressed.connect(self.btn_add_f)
        self.list_view.clicked.connect(self.list_view_f)
        self.list_view.doubleClicked.connect(self.list_view_double_f)

    def init(self):
        self.item_l = []
        self.thread_single_l = []

        self.can_replace = True

        self.cfg = load_config_dict()
        print("loaded cfg")

        try:
            self.data = DataContainer(self.cfg["language"])
        except FileNotFoundError:
            before_s = self.cfg["language"]
            self.cfg["language"] = DEFAULT_LANG_S
            self.data = DataContainer(self.cfg["language"])
            self.save_config()
            print("Language '{}' does not exist so default language '{}' has been loaded."
                  .format(before_s, DEFAULT_LANG_S))
        else:
            print("loaded DataContainer")

        data_l = list(load_txt_data_gen())

        if self.cfg["main-sort_on_init-option"]:
            data_l = self.sort_data(data_l, self.cfg["main-sort_on_init-option"], self.cfg["main-sort_on_init-reverse"])

        self.set_all_items(data_l, False)
        self.save_to_txt()
        self.draw_list_view()

        self.test()

    def test(self):
        print("func called: test")
        pass

    def every_time(self):
        print("func called: every_time")
        self.refresh_all_label()
        self.label_1.setText(_translate("MainWindow", self.data.ld_ui_get_a_value("main-label_1"), None))

    def on_draw(self):
        print("func called: on_draw")
        st = time.time()
        for x_I in self.item_l:
            if x_I.image_exists():
                x_I.set_thum()
        print("Drawing all thums took {} sec.".format(time.time() - st))

        if self.first_time_b:
            self.on_first_start()

    def on_exit(self):
        print("func called: on_exit")
        pass

    def on_first_start(self):
        url_s = "http://marumaru.in/?m=bbs&bid=manga&p=2&uid=169554"
        self.add_url_to_item_class(url_s)
        self.draw_list_view()

        url_s = "http://marumaru.in/b/manga/16"
        self.add_url_to_item_class(url_s)
        self.draw_list_view()

        text_s = """마루마루 도우미를 다운로드해 주셔서 감사합니다.
프로그램 사용 방법을 좀 더 쉽게 익힐 수 있도록
미리 만화 두 개가 추가돼 있습니다.
'검색' 버튼을 눌러서 어떤 일이 일어나나 직접 확인해 보세요.

직접 만화를 추가하시러면
제일 윗단의 텍스트 입력 상자에 해당 마루마루 만화의 URL을
붙여넣은 뒤 우측의 '추가'버튼을 누르세요."""
        NoticeWindow(text_s, self).exec_()

    ######## Button functions ########

    def btn_dbg_f(self):
        self.every_time()

        print(self.thread_single_l)

    def btn_add_f_dum(self):
        self.every_time()

        text_s = self.lineEdit.text()
        if not text_s:
            pass
        elif text_s.startswith("https"):
            self.label_1.setText("이 프로그램은 https를 사용하는 마루마루를 지원하지 않습니다.")

        ######## command ########

        elif text_s == "thread_list":
            print(self.thread_single_l)
        elif text_s.startswith("pop"):
            try:
                args_l = split_command(text_s)
            except WTF:
                self.label_1.setText("command error : pop (invalid form)")
            else:
                if len(args_l) == 1:
                    NoticeWindow("pop command has been entered.\nThis is just for experimant.", self).exec_()
                    self.label_1.setText("command : pop")
                elif len(args_l) == 2:
                    NoticeWindow(args_l[1], self).exec_()
                    self.label_1.setText("command : pop")
                else:
                    self.label_1.setText("command error : pop (it takes only 0 or 1 arguments)")
        elif text_s == "backup_data":
            self.backup_data()
            self.label_1.setText("command : backup_data")
        elif text_s == "restore_data":
            self.backup_load_data()
            self.label_1.setText("command : restore_data")
        elif text_s.startswith("save_config"):
            try:
                args_l = split_command(text_s)
            except WTF:
                self.label_1.setText("command error : save_config (invalid form)")
            else:
                if len(args_l) == 1:
                    self.save_config()
                    self.label_1.setText("command : save_config")
                else:
                    self.label_1.setText("command error : save_config (it takes no argument)")
        elif text_s.startswith("settings"):
            try:
                args_l = split_command(text_s)
            except WTF:
                self.label_1.setText("command error : settings (invalid form)")
            else:
                if len(args_l) == 1:
                    self.option_window()
                    self.label_1.setText("command : settings")
                else:
                    self.label_1.setText("command error : settings (it takes no argument)")
        elif text_s.startswith("retranslate"):
            try:
                args_l = split_command(text_s)
            except WTF:
                self.label_1.setText("command error : set_font (invalid form)")
            else:
                if len(args_l) == 2:
                    try:
                        self.retranslate_all(args_l[1])
                    except FileNotFoundError:
                        self.label_1.setText("command error : retranslate (not existing language)")
                    else:
                        self.label_1.setText("command : retranslate")
                else:
                    self.label_1.setText("command error : retranslate (one argument is required)")
        elif text_s.startswith("set_font"):
            try:
                args_l = split_command(text_s)
            except WTF:
                self.label_1.setText("command error : set_font (invalid form)")
            else:
                if len(args_l) == 2:
                    self.set_font(args_l[1])
                    self.label_1.setText("command : set_font")
                else:
                    self.label_1.setText("command error : set_font (one argument is required)")

        ######## add manga ########

        else:
            if not text_s.startswith("http://"):
                text_s = "http://" + text_s

            if m.is_manga_url(text_s):
                result_code_i = self.add_url_to_item_class(text_s)
                if result_code_i == -1:
                    self.label_1.setText(self.data.get_value("ui", "main-label-already"))
                    self.lineEdit.clear()
                elif result_code_i == 0:
                    self.label_1.setText(self.data.get_value("ui", "main-label-success"))
                    self.lineEdit.clear()
                    self.draw_list_view()
            else:
                prints("invalid marumaru URL : {}".format(text_s))
                self.label_1.setText(self.data.get_value("ui", "main-label-invalid"))

    def btn_add_f(self):
        self.every_time()

        text_s = self.lineEdit.text()
        if not text_s:
            return
        try:
            args_l = split_command(text_s)
        except:
            self.label_1.setText(self.data.get_value("ui", "main-label_1-invalid_form"))
            return
        args_len_i = len(args_l)
        if args_len_i < 1:
            return
        if not args_l[0]:
            return

        if m.is_manga_url(args_l[0]):
            if text_s.startswith("https"):
                self.label_1.setText(self.data.get_value("ui", "main-label-https"))
                return

            if not args_l[0].startswith("http://"):
                args_l[0] = "http://" + args_l[0]
            if not args_l[0].startswith("http://marumaru.in/") and not args_l[0].startswith("http://www.marumaru.in/"):
                prints("invalid marumaru URL: {}".format(args_l[0]))
                self.label_1.setText(self.data.get_value("ui", "main-label-invalid"))
                return

            result_code_i = self.add_url_to_item_class(args_l[0])
            if result_code_i == -1:
                self.label_1.setText(self.data.get_value("ui", "main-label-already"))
                self.lineEdit.clear()
            elif result_code_i == 0:
                self.label_1.setText(self.data.get_value("ui", "main-label-success"))
                self.lineEdit.clear()
                self.draw_list_view()

        #### commands ####

        elif args_l[0] == "con_threads":
            if args_len_i == 1:
                print("Threads for single fetch")
                print("-"*50)
                for x_thread in self.thread_single_l:
                    print(x_thread)
                print("-" * 50)
                self.label_1.setText('Command "con_threads" : Threads objects have been printed on console.')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "con_threads" : The command takes no argument.')
                return
        elif args_l[0] == "con_item_chap_list":
            if args_len_i == 2:
                try:
                    index = int(args_l[1]) - 1
                except ValueError:
                    self.label_1.setText('Command error "con_item_chap_list" : First argument must be int.')
                    return
                else:
                    for x, x_t in enumerate(self.item_l[index].get_chapter_l()):
                        print("{:0>3} : {}".format(x, x_t))
                    self.label_1.setText('Command "con_item_chap_list" : Chapter list has been printed on console.')
                    self.lineEdit.clear()
                    return
            else:
                self.label_1.setText('Command error "con_item_chap_list" : The command takes one(int) argument.')
                return
        elif args_l[0] == "con_print":
            if args_len_i == 2:
                print(args_l[1])
                self.label_1.setText('Command "con_print" : Called function print({}).'.format(args_l[1]))
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "con_print" : The command takes one(any) argument.')
                return
        elif args_l[0] == "popup":
            if args_len_i == 1:
                self.label_1.setText('Command "popup"')
                NoticeWindow("pop command has been entered.\nThis is just for experiment.", self).exec_()
                self.lineEdit.clear()
                return
            elif args_len_i == 2:
                self.label_1.setText('Command "popup"')
                NoticeWindow(args_l[1], self).exec_()
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "popup" : The command takes one(any) argument or not.')
                return
        elif args_l[0] == "save_config":
            if args_len_i == 1:
                self.save_config()
                self.label_1.setText('Command "save_config"')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "all_save_config" : The command takes no argument.')
                return
        elif args_l[0] == "save_data":
            if args_len_i == 1:
                self.save_to_txt()
                self.label_1.setText('Command "save_data"')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "save_data" : The command takes no argument.')
                return
        elif args_l[0] == "save_data_json":
            if args_len_i == 1:
                self.save_data_json()
                self.label_1.setText('Command "save_data_json"')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "save_data_json" : The command takes no argument.')
                return
        elif args_l[0] == "load_data_json":
            if args_len_i == 1:
                self.label_1.setText('Command error "load_data_json" : This command is not implemented yet.')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "load_data_json" : The command takes no argument.')
                return
        elif args_l[0] == "retranslate":
            if args_len_i == 1:
                self.retranslate_all()
                self.label_1.setText('Command "retranslate" : Most likely nothing changed.')
                self.lineEdit.clear()
                return
            elif args_len_i == 2:
                try:
                    self.retranslate_all(args_l[1])
                except FileNotFoundError:
                    self.label_1.setText('Command error "retranslate" : Given name \'{}\' does not exists in \'{}\'.'
                                         .format(args_l[1], LANG_FOL_S))
                    return
                else:
                    self.label_1.setText('Command "retranslate" : Retranslated to \'{}\'.'
                                         .format(args_l[1]))
                    self.lineEdit.clear()
                    return
            else:
                self.label_1.setText('Command error "retranslate" : The command takes only one(any) argument.')
                return
        elif args_l[0] == "set_font":
            if args_len_i == 2 or args_len_i == 3:
                self.set_font(*args_l[1:])
                self.label_1.setText('Command "set_font" : Font changed to \'{}\'.'.format(args_l[1]))
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "set_font" : The command takes one(any) argument.')
                return
        elif args_l[0] == "settings":
            if args_len_i == 1:
                self.option_window()
                self.label_1.setText('Command "settings"')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "settings" : The command takes no argument.')
                return
        elif args_l[0] == "item_retitle":
            if args_len_i == 2 or args_len_i == 3:
                try:
                    index_i = int(args_l[1]) - 1
                    print(index_i)
                except ValueError:
                    self.label_1.setText('Command error "item_retitle" : First argument must be int.')
                    return
                else:
                    a_item = self.item_l[index_i]
                    title_before_s = a_item.get_title()
                    if args_len_i == 2:
                        result_code_i = a_item.reload_title()
                        if result_code_i == -1:
                            self.label_1.setText('Command error "item_retitle" : Failed to get title from web.')
                            return
                        elif result_code_i == 0:
                            self.draw_list_view()
                            self.save_to_txt()
                            self.label_1.setText('Command "item_retitle" : Title loaded from web. (\'{}\' -> \'{}\')'
                                                 .format(title_before_s, a_item.get_title()))
                            self.lineEdit.clear()
                            return
                        else:
                            raise WTF
                    elif args_len_i == 3:
                        a_item.set_title(args_l[2])
                        self.draw_list_view()
                        self.save_to_txt()
                        self.label_1.setText('Command "item_retitle" : Title edited. (\'{}\' -> \'{}\')'
                                             .format(title_before_s, args_l[2]))
                        self.lineEdit.clear()
                        return
                    else:
                        raise WTF
            else:
                self.label_1.setText('Command error "item_retitle" : The command takes one(int) or two(int, string) arguments.')
                return
        elif args_l[0] == "item_reload_thum":
            if args_len_i == 2:
                try:
                    index = int(args_l[1]) - 1
                except ValueError:
                    self.label_1.setText('Command error "item_reload_thum" : First argument must be int.')
                    return
                else:
                    item = self.item_l[index]
                    item.reload_thum()
                    item.set_thum()

                    self.label_1.setText('Command "item_reload_thum"')
                    self.lineEdit.clear()
                    return
            else:
                self.label_1.setText('Command error "item_reload_thum" : The command takes one(int) argument.')
                return
        elif args_l[0] == "item_delete":
            if args_len_i == 2:
                try:
                    index_i = int(args_l[1]) - 1
                except ValueError:
                    self.label_1.setText('Command error "item_delete" : First argument must be int.')
                    return
                else:
                    title_s = self.item_l[index_i].get_title()
                    self.item_l[index_i].delete()
                    self.item_l[index_i] = 0
                    self.label_1.setText('Command "item_delete" : \'{}\' has been deleted.'.format(title_s))
                    self.lineEdit.clear()
                    return
            else:
                self.label_1.setText('Command error "item_delete" : The command takes one argument(int).')
                return
        elif args_l[0] == "item_swap":
            if args_len_i == 3:
                try:
                    a_index = int(args_l[1]) - 1
                    b_index = int(args_l[2]) - 1
                except ValueError:
                    self.label_1.setText('Command error "item_swap" : First and second arguments must be int.')
                    return
                else:
                    result_t = self.swap_place(a_index, b_index)
                    if result_t[0] == -1:
                        self.label_1.setText('Command error "item_swap" : Invalid argument \'{}\''.format(result_t[1] + 1))
                        return
                    elif result_t[0] == -2:
                        self.label_1.setText('Command error "item_swap" : This command is currently not available.')
                        return
                    else:
                        self.draw_list_view()
                        self.label_1.setText('Command "item_swap" : \'{}\' and \'{}\' have swapped their place.'
                                             .format(self.item_l[a_index].get_title(), self.item_l[b_index].get_title()))
                        self.lineEdit.clear()
                        return
            else:
                self.label_1.setText('Command error "item_swap" : The command takes two(int, int) arguments.')
                return
        elif args_l[0] == "all_delete":
            if args_len_i == 1:
                self.delete_all_items()
                self.draw_list_view()
                self.save_to_txt()
                self.label_1.setText('Command "all_delete"')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command "all_delete" : The command takes no argument.')
                return
        elif args_l[0] == "all_sort":
            if args_len_i == 3:
                try:
                    a1 = int(args_l[1])
                    a2 = bool(args_l[2])
                except ValueError:
                    self.label_1.setText('Command error "all_sort" : First and second arguments must be int.')
                    return
                else:
                    self.entire_task_for_sorting(a1, a2)
                    self.label_1.setText('Command "all_sort"')
                    self.lineEdit.clear()
                    return
            else:
                self.label_1.setText('Command error "all_sort" : The command takes two(int, int) arguments.')
                return
        elif args_l[0] == "all_fetch":
            if args_len_i == 1:
                self.start_multi_fetch(True)
                self.label_1.setText('Command "all_fetch"')
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command error "all_fetch" : The command takes no argument.')
                return
        elif args_l[0] == "all_export":
            if args_len_i == 1:
                file_name_s = "printed.txt"
                file = open(DATA_FOL_LOC_S + file_name_s, 'w', encoding="utf8")
                self.print_all(True, file)
                file.close()

                self.label_1.setText('Command "all_export" : Unread chapter list has been exported in \'{}\'.'
                                     .format(DATA_FOL_LOC_S + file_name_s))
                self.lineEdit.clear()
                return
            else:
                self.label_1.setText('Command "all_export" : The command takes no argument.')
                return

        ####

        else:
            prints("invalid marumaru URL or command: {}".format(args_l[0]))
            NoticeWindow(self.data.get_value("ui", "main-label-invalid"), self).exec_()

    def btn_search_f(self):
        self.every_time()

        self.start_multi_fetch()

    def list_view_f(self):
        self.every_time()

        option = 2

        if option == 1:
            vbar = self.scrollArea.verticalScrollBar()
            index = self.list_view.selectedIndexes()[0].row()
            length = len(self.item_l)
            step = vbar.maximum() / (length - 1)
            vbar.setValue(step * index)

        elif option == 2:
            index = self.list_view.selectedIndexes()[0].row()
            self.focus_in_scroll(index)

    def list_view_double_f(self):
        self.every_time()

        index = self.list_view.selectedIndexes()[0].row()
        url_s = self.item_l[index].get_url()
        webbrowser.open(url_s)

    ######## Item class functions ########

    def item_readall(self, index:int):
        self.every_time()

        target_I = self.item_l[index]
        if target_I.btn_readall.text() == self.data.ld_ui_get_a_value("item-btn_readall-false"):
            target_I.read_all(1)
            target_I.draw_list()
            self.save_to_txt()
            self.draw_list_view()
            target_I.update_btn_readall()
        elif target_I.btn_readall.text() == self.data.ld_ui_get_a_value("item-btn_readall-true"):
            target_I.read_all(0)
            target_I.draw_list()
            self.save_to_txt()
            self.draw_list_view()
            target_I.update_btn_readall()
        else:
            raise WTF
        #print(self.item_l[index].graphic_view.size())

    def item_checked(self, index, wtf, check_state):
        self.every_time()

        target_I = self.item_l[index]
        if check_state > 0:
            target_I.set_search_flag(True)
        elif check_state == 0:
            target_I.set_search_flag(False)
        else:
            raise WTF
        target_I.check_box.setChecked(target_I.get_search_flag())
        self.save_to_txt()

    def item_checked_2(self, index, wtf, check_state):
        self.every_time()

        target_I = self.item_l[index]
        if check_state > 0:
            target_I.set_show_unread_flag(True)
        elif check_state == 0:
            target_I.set_show_unread_flag(False)
        else:
            raise WTF
        target_I.check_box_2.setChecked(target_I.get_show_unread_flag())
        target_I.draw_list()
        target_I.set_last_checked_count_i(target_I.get_num_of_checked())

        self.save_to_txt()

    def item_btn_load(self, index:int):
        self.every_time()

        self.load_a_item(self.item_l[index].get_number())

    def item_btn_delete(self, index: int):
        self.every_time()

        target_I = self.item_l[index]
        if target_I.btn_delete.text() == self.data.ld_ui_get_a_value("item-btn_delete-false"):
            target_I.set_delete_flag(True)
            target_I.update_btn_delete()
            target_I.update_label()

        elif target_I.btn_delete.text() == self.data.ld_ui_get_a_value("item-btn_delete-true"):
            target_I.set_delete_flag(False)
            target_I.update_btn_delete()
            target_I.update_label()

        self.save_to_txt()
        self.draw_list_view()

    def item_btn_open_url(self, index:int):
        self.every_time()

        url_s = self.item_l[index].get_url()
        webbrowser.open(url_s)

    def item_btn_up_down(self, argument_t:tuple):
        self.every_time()

        index, vector = argument_t

        if not self.can_replace:
            print("failed to swap place : {}, {}".format(index, index + vector))

        self.focus_in_scroll(index + vector)
        self.focus_in_list(index + vector)
        result_code_i = self.swap_place(index, index + vector)
        if result_code_i == 0:
            self.draw_list_view()
            self.save_to_txt()
        elif result_code_i == -1:
            print("failed to swap place : {}, {}".format(index, index + vector))
            self.focus_in_scroll(index)
            self.focus_in_list(index)

    def item_list_clicked(self, index:int):
        self.every_time()

        target_I = self.item_l[index]
        checked_i = target_I.get_num_of_checked()
        if checked_i == target_I.get_last_checked_count_i():
            selected_index = target_I.list_view.selectedIndexes()[0].row()
            seleted_item = target_I.list_view.model().item(selected_index)
            clicked_text_s = seleted_item.text().rstrip("  " + self.data.get_value("ui", "item-list_view-new"))
            if not clicked_text_s:
                return
            elif clicked_text_s == self.data.get_value("ui", "item-list_view-read_all"):
                return
            elif clicked_text_s == self.data.get_value("ui", "item-list_view-empty"):
                return

            if self.cfg["check_on_open"]:
                seleted_item.setCheckState(2)
                target_I.update_check_state()
                self.save_to_txt()
                target_I.update_btn_readall()
                self.draw_list_view()

            print("just clicked {}".format(selected_index))
            url_s = target_I.drawn_chap_l[selected_index]
            webbrowser.open(url_s)
        else:
            print("checked")
            target_I.update_check_state()
            self.save_to_txt()
            target_I.update_btn_readall()
            self.draw_list_view()
        checked_i = target_I.get_num_of_checked()
        target_I.set_last_checked_count_i(checked_i)

    ######## single fetch ########

    def load_a_item(self, number: int):
        target_I = self.get_item_from_number_safe(number)

        target_I.btn_load.setDisabled(True)

        new_index = len(self.thread_single_l)
        self.thread_single_l.append(FetchOne(target_I.get_number(), target_I.get_url(), new_index))
        self.connect(self.thread_single_l[new_index], QtCore.SIGNAL("fetch_one_finished(PyQt_PyObject)"),
                     self.fetch_one_finished_sig)
        self.thread_single_l[new_index].start()

    def fetch_one_finished_sig(self, result_t: tuple):
        if len(result_t) == 6:
            number, last_up_i, title_s, chapter_t_zip, thum_s, thread_index = result_t
            self.thread_single_l[thread_index].terminate()

            target_I = self.get_item_from_number_safe(number)

            if not target_I.get_title():
                target_I.set_title(title_s)
            target_I.set_last_up(last_up_i)

            if (target_I.get_thum_url() != thum_s) or not target_I.image_exists():
                if thum_s:
                    target_I.set_thum_url(thum_s)
                    target_I.reload_thum()

            temp_chapter_l = []
            for cha_name_s, cha_url_s in chapter_t_zip:
                temp_chapter_l.append((0, cha_name_s, cha_url_s, last_up_i))
            target_I.update_chapter_list(temp_chapter_l)
            target_I.draw_list()

            target_I.btn_load.setDisabled(False)
            self.save_to_txt()
            self.draw_list_view()
            prints("finished fetching : {}".format(target_I.get_url()))

        elif len(result_t) == 2:
            number, thread_index = result_t

            self.thread_single_l[thread_index].terminate()

            target_I = self.get_item_from_number_safe(number)

            target_I.set_last_up(-1)
            target_I.draw_list()

            target_I.btn_load.setDisabled(False)
            self.save_to_txt()
            prints("failed fetching: {}".format(target_I.get_url()))

    ######## multiple fetch ########

    def start_multi_fetch(self, fetch_all:bool=False):
        self.btn_search.setDisabled(True)

        queue_l = []
        for x_I in self.item_l:
            x_I.btn_load.setDisabled(True)
            if fetch_all or x_I.get_search_flag():
                queue_l.append(x_I.get_number())

        queue_len_i = len(queue_l)
        self.progressBar.setMaximum(queue_len_i)
        self.progressBar.setValue(0)
        self.label_1.setText("모두 검색 진행중")

        work_l = [[],[],[]]
        for x, x_s in enumerate(queue_l):
            work_l[x % 3].append(x_s)

        self.thread_l = []
        self.ended = 0
        self.failed_i = 0
        self.succeeded_i = 0
        self.new_accum_i = 0

        for x, x_l in enumerate(work_l):
            self.thread_l.append(FetchAll(self, x_l))
            self.connect(self.thread_l[x], QtCore.SIGNAL("fetch_all_one_finished(PyQt_PyObject)"), self.fetch_all_one_finished_sig)
            self.connect(self.thread_l[x], QtCore.SIGNAL("fetch_all_all_finished(PyQt_PyObject)"), self.fetch_all_all_finished_sig)
            self.thread_l[x].start()
            print("thread {} created".format(x))

    def fetch_all_one_finished_sig(self, result_t: tuple):
        if len(result_t) == 5:
            st = time.time()
            number, last_up_i, title_s, chapter_t_l, thum_s = result_t

            target_I = self.get_item_from_number_safe(number)

            if not target_I.get_title() or 1:
                target_I.set_title(title_s)
            target_I.set_last_up(last_up_i)

            if (target_I.get_thum_url() != thum_s) or not target_I.image_exists():
                if thum_s:
                    target_I.set_thum_url(thum_s)
                    target_I.reload_thum()

            temp_chapter_l = []
            for cha_name_s, cha_url_s in chapter_t_l:
                temp_chapter_l.append((0, cha_name_s, cha_url_s, last_up_i))
            target_I.update_chapter_list(temp_chapter_l)
            target_I.draw_list()

            self.save_to_txt()
            self.draw_list_view()
            self.progressBar.setValue(self.progressBar.value() + 1)

            self.succeeded_i += 1
            prints("finished fetching : {}".format(target_I.get_url()))

        elif len(result_t) == 1:
            number = result_t[0]
            target_I = self.get_item_from_number_safe(number)

            target_I.set_last_up(-1)
            target_I.draw_list()

            self.save_to_txt()
            self.progressBar.setValue(self.progressBar.value() + 1)
            prints("failed fetching: {}".format(target_I.get_url()))

            self.failed_i += 1
            if self.failed_i >= self.cfg["fail_count_to_force_out"] and self.failed_i > self.succeeded_i:
                self.fetch_all_terminate()

    def fetch_all_all_finished_sig(self, result:int):
        failed_i, new_i = result

        self.new_accum_i += new_i
        self.ended += 1

        if self.ended >= 3:
            for x_thread in self.thread_l:
                x_thread.terminate()
            for x_I in self.item_l:
                x_I.btn_load.setDisabled(False)
            self.label_1.setText(self.data.get_value("ui", "main-label_1"))
            NoticeWindow("모두 검색 완료\n{}개 실패\n새로운 챕터 {}개".format(self.failed_i, self.new_accum_i), self).exec_()
            self.btn_search.setDisabled(False)

    def fetch_all_terminate(self):
        for x_thread in self.thread_l:
            x_thread.terminate()
        print("fetch all threads terminated")
        for x_I in self.item_l:
            x_I.btn_load.setDisabled(False)
        self.label_1.setText(self.data.get_value("ui", "main-label_1"))
        self.progressBar.setValue(0)
        NoticeWindow("{}개의 항목을 불러오는 데 실패했습니다.\n네트워크 연결이 불안정하거나\n마루마루 서버가 응답을 하지 않습니다.".format(self.failed_i, self.new_accum_i), self).exec_()
        self.btn_search.setDisabled(False)

    ####### img fetch ########

    def start_downloading_thum(self, number):
        target_item = self.get_item_from_number_safe(number)
        self.thread_image = DownloadImage(target_item)
        self.connect(self.thread_image, QtCore.SIGNAL("thum_finished(PyQt_PyObject)"), self.img_finished_sig)
        self.thread_image.start()

    def img_finished_sig(self, result:tuple):
        result_code_i, number = result
        if result_code_i == 0:
            a_item = self.get_item_from_number_safe(number)
            print("finished downloading thum")
            a_item.set_thum()
        else:
            raise WTF

    ######## task #######

    def focus_in_scroll_dum(self, index:int):
        vbar = self.scrollArea.verticalScrollBar()
        step = self.item_l[index].group_box.size().height() + 7
        vbar.setValue(step * index)
        print("focus in scroll to {}".format(index))

    def focus_in_scroll(self, index:int):
        vbar = self.scrollArea.verticalScrollBar()
        a = self.item_l[index].group_box.geometry().top() - 10
        vbar.setValue(a)
        print("focus in scroll to {}".format(index))

    def focus_in_list(self, index:int):
        vbar = self.list_view.verticalScrollBar()
        step = 1
        plus = self.list_view.height() / 60
        vbar.setValue(step*index - plus)
        print("focus in list to {}".format(index))

    ######## task for all items ########

    def delete_all_items(self):
        for x, x_item in enumerate(self.item_l):
            x_item.delete()
        self.item_l = []

    def get_all_data_gen(self):
        for x_item in self.item_l:
            yield x_item.get_full_data()

    def set_all_items(self, a:iter, draw_thum:bool=True):
        for x_t in a:
            index = len(self.item_l)
            self.item_l.append(Item(self, index, draw_thum, tuple(x_t)))
            self.connect_item_signals(self.item_l[index].get_number())

    def print_all(self, not_read_only:bool=True, file=None):
        for x in self.item_l:
            x.print_string(not_read_only, file)

    ######## sorting ########

    def entire_task_for_sorting(self, option:int, reverse:bool):
        data_l = list(self.get_all_data_gen())
        self.delete_all_items()

        data_l = self.sort_data(data_l, option, reverse)

        self.set_all_items(data_l)
        self.draw_list_view()
        self.save_to_txt()

    def sort_data(self, data_l:list, option:int, reverse:bool):
        if option == 1:  # title
            data_l.sort(key=lambda x: x[3], reverse=reverse)
        elif option == 2:  # the number of chapters
            data_l.sort(key=lambda x: len(x[4]), reverse=reverse)
        elif option == 3: # the number of remaining chapters
            data_l.sort(key=self.sort_opt_2_remaining_chap, reverse=reverse)

        return data_l

    def sort_opt_2_remaining_chap(self, x_t:tuple):
        c = 0
        for x_l in x_t[4]:
            if x_l[0] == 0:
                c += 1
        return c

    ######## util ########

    def get_item_from_number_safe(self, number):
        index = self.find_index_by_num(number)
        target_I = self.item_l[index]

        return target_I

    def swap_place(self, a_index, b_index) -> tuple:
        if not self.can_replace:
            return -2, 0
        else:
            for x_i in (a_index, b_index):
                if x_i < 0:
                    return -1, x_i
                elif x_i >= len(self.item_l):
                    return -1, x_i

            a_item = self.item_l[a_index]
            b_item = self.item_l[b_index]

            a_full_data_t = a_item.get_full_data()
            b_full_data_t = b_item.get_full_data()

            a_item.delete()
            self.item_l[a_index] = 0
            b_item.delete()
            self.item_l[b_index] = 0

            self.item_l[b_index] = Item(self, b_index, True, a_full_data_t)
            self.item_l[a_index] = Item(self, a_index, True, b_full_data_t)

            self.connect_item_signals(self.item_l[b_index].get_number())
            self.connect_item_signals(self.item_l[a_index].get_number())

            self.save_to_txt()

            print("swaped")
            return 0, 0

    def set_font(self, *args):
        if len(args) > 2:
            raise WTF
        for x in args:
            try:
                x = int(x)
            except ValueError:
                BFONT.setFamily(x)
                print("change font to {}".format(x))
            else:
                BFONT.setPointSize(x)
                print("change font size to {}".format(x))

        self.retranslate_all()

    def retranslate_all(self, file_name:str=''):
        if not isinstance(file_name, str):
            return WTF

        if file_name:
            self.data.ld_reload(file_name)
            self.cfg["language"] = file_name
            self.save_config()
        else:
            pass

        self.retranslateUi()
        self.draw_list_view()
        for x_I in self.item_l:
            x_I.retranslate()
            x_I.draw_list()

    def backup_data(self):
        self.save_to_txt()
        file_name_s = "data-backup-{}".format(int(time.time()))
        clear_dirt_way(BACKUP_FOL_S)
        shutil.copy(SAVE_TXT_S, BACKUP_FOL_S + file_name_s)
        print("data backup completed.")

    def backup_load_data(self):
        for x_s in os.listdir(BACKUP_FOL_S):
            print("backup data : {}".format(x_s))

    def option_window(self):
        a = OptionWindow(self)
        a.exec_()

    def refresh_all_label(self):
        for x_I in self.item_l:
            x_I.update_label()

    def refresh_all_listviews(self):
        self.draw_list_view()

        for x_I in self.item_l:
            x_I.draw_list()

        print("refreshed all list views")

    def clear_thread_list(self):
        alive_count_i = 0
        for x_thread in self.thread_single_l:
            if not x_thread.isFinished():
                alive_count_i += 1
        if not alive_count_i:
            self.thread_single_l = []

    def draw_list_view(self):
        self.model.clear()
        printed = False

        if self.cfg["main_list-index-same_len_num"]:
            len_i = len(str(len(self.item_l)))
        else:
            len_i = 1

        for x_I in self.item_l:
            vitem = QtGui.QStandardItem()
            vitem.setFont(BFONT)
            vitem.setCheckable(False)
            vitem.setEditable(False)

            basic_s = "({:0>" + str(len_i) + "}) {}"
            if not x_I.get_title():
                a_text = basic_s.format(int(x_I.get_index()) + 1, "(정보 없음)")
            else:
                a_text = basic_s.format(int(x_I.get_index()) + 1, x_I.get_title())
                remain_i, new_chap_i = x_I.remaining_chaps()
                if self.cfg["main_list-show_stat-remaining"] and remain_i:
                    contain_s = CONTAINER_T[self.cfg["main_list-show_stat-remaining-container"]]
                    string_s = self.data.get_value("ui", "main-list_view-show_stat-remaining").format(remain_i)
                    a_text += "  " + contain_s[0] + string_s + contain_s[1]
                if self.cfg["main_list-show_stat-new_ones"] and new_chap_i:
                    contain_s = CONTAINER_T[self.cfg["main_list-show_stat-new_ones_container"]]
                    string_s = self.data.get_value("ui", "main-list_view-show_stat-new_ones").format(new_chap_i)
                    a_text += "  " + contain_s[0] + string_s + contain_s[1]
                if self.cfg["main_list-show_stat-last_failed"] and x_I.get_last_up() == -1:
                    contain_s = CONTAINER_T[self.cfg["main_list-show_stat-last_failed-container"]]
                    string_s = self.data.get_value("ui", "main-list_view-show_stat-last_failed")
                    a_text += "  " + contain_s[0] + string_s + contain_s[1]
                elif self.cfg["main_list-show_stat-over_month"] and time.time() - x_I.get_last_up() > 2592000:
                    contain_s = CONTAINER_T[self.cfg["main_list-show_stat-over_month-container"]]
                    string_s = self.data.get_value("ui", "main-list_view-show_stat-over_month")
                    a_text += "  " + contain_s[0] + string_s + contain_s[1]
                elif self.cfg["main_list-show_stat-last_chap_too_old"] and x_I.last_chap_date_distance() > 60*60*24*30:
                    contain_s = CONTAINER_T[self.cfg["main_list-show_stat-last_chap_too_old-container"]]
                    string_s = self.data.get_value("ui", "main-list_view-show_stat-last_chap_too_old")
                    a_text += "  " + contain_s[0] + string_s + contain_s[1]
                if self.cfg["main_list-show_stat-delete"] and x_I.get_delete_flag():
                    contain_s = CONTAINER_T[self.cfg["main_list-show_stat-delete-container"]]
                    string_s = self.data.get_value("ui", "main-list_view-show_stat-delete")
                    a_text += "  " + contain_s[0] + string_s + contain_s[1]
            vitem.setText(a_text)

            self.model.appendRow(vitem)
            printed = True

        if not printed:
            vitem = QtGui.QStandardItem()
            vitem.setFont(BFONT)
            vitem.setCheckable(False)
            vitem.setEditable(False)
            vitem.setText("항목 없음")
            self.model.appendRow(vitem)

        self.list_view.setModel(self.model)

    def connect_item_signals(self, number:int):
        target_I = self.get_item_from_number_safe(number)

        target_I.btn_readall.clicked.connect(functools.partial(self.item_readall, target_I.get_index()))
        target_I.btn_load.clicked.connect(functools.partial(self.item_btn_load, target_I.get_index()))
        target_I.btn_open_url.clicked.connect(functools.partial(self.item_btn_open_url, target_I.get_index()))
        target_I.btn_delete.clicked.connect(functools.partial(self.item_btn_delete, target_I.get_index()))
        target_I.btn_up.clicked.connect(functools.partial(self.item_btn_up_down, (target_I.get_index(), -1)))
        target_I.btn_down.clicked.connect(functools.partial(self.item_btn_up_down, (target_I.get_index(), 1)))

        target_I.list_view.clicked.connect(functools.partial(self.item_list_clicked, target_I.get_index()))
        target_I.check_box.stateChanged.connect(functools.partial(self.item_checked, target_I.get_index(), target_I.check_box.checkState()))
        target_I.check_box_2.stateChanged.connect(functools.partial(self.item_checked_2, target_I.get_index(), target_I.check_box.checkState()))

    def save_to_txt(self):
        print("Save to data")
        while True:
            try:
                file = open(SAVE_TXT_S, 'w', encoding='utf8')
            except PermissionError:
                continue
            else:
                file.close()
                break

        while True:
            try:
                file = open(SAVE_TXT_S, 'a', encoding="utf8")
            except PermissionError:
                continue
            else:
                for x_I in self.item_l:
                    file.write(x_I.get_save_string())
                file.close()
                break

    def save_data_json(self):
        while True:
            try:
                file = open(SAVE_JSON_S, 'w', encoding='utf8')
            except PermissionError:
                continue
            else:
                json.dump(list(self.get_all_data_gen()), file)
                file.close()
                break
        print("Save to data.json")

    def save_config(self):
        file = open(CONFIG_TXT_S, 'w')
        file.close()

        for x_key in self.cfg:
            save_s = "{} : {}\n".format(x_key, self.cfg[x_key])
            with open(CONFIG_TXT_S, 'a') as file:
                file.write(save_s)


        print("config saved")

    def add_url_to_item_class(self, url_s:str):
        for x_I in self.item_l:
            if x_I.get_url() == url_s:
                return -1
        index = len(self.item_l)

        while True:
            rand_i = random.randint(1,10000)
            for x_I in self.item_l:
                if x_I.get_number() == rand_i:
                    break
            else:
                number = rand_i
                break

        try:
            self.item_l.append(Item(self, index, False, (number, url_s)))
        except UnboundLocalError:
            print("All number spaces are filled.")
            raise UnboundLocalError
        target_I = self.item_l[index]
        self.connect_item_signals(target_I.get_number())
        prints("added : {}".format(url_s))
        self.save_to_txt()
        return 0

    def find_index_by_num(self, num):
        for x, x_I in enumerate(self.item_l):
            if x_I.get_number() == num:
                return x
        print("not existing number : {}".format(num))
        raise WTF


class Item:  # QtGui.QMainWindow
    def __init__(self, ui_class, index:int, draw_thum:bool, data_t: tuple):
        self.ui_class = ui_class

        if len(data_t) == 2:
            number, url = data_t

            self.__number = number
            self.__index = index
            self.__url = url
            self.__thum_url = ''
            self.__title = ""
            self.__chapter_l = []
            self.__last_up = 0
            self.__search_flag = True
            self.__delete_flag = False
            self.__show_unread_flag = True

            self.__last_checked_count_i = 0
            self.drawn_chap_l = []

            self.set_ui()
            self.retranslate()
            self.connect_signals()

        elif len(data_t) == 9:
            number, url, thum_url, title, chapter_l, last_up, search_flag, delete_flag, show_unread_flag = data_t

            self.__number = number
            self.__index = index
            self.__url = url
            self.__thum_url = thum_url
            self.__title = title
            self.__chapter_l = chapter_l
            self.__last_up = last_up
            self.__search_flag = search_flag
            self.__delete_flag = delete_flag
            self.__show_unread_flag = show_unread_flag

            self.drawn_chap_l = []

            self.set_ui()
            self.retranslate()
            self.connect_signals()
            self.draw_list()
            if draw_thum and self.image_exists():
                self.set_thum()

            self.__last_checked_count_i = self.get_num_of_checked()

            self.update_label()

        else:
            raise WTF

    def set_ui(self):
        self.group_box = QtGui.QGroupBox(self.ui_class.scrollAreaWidgetContents)
        self.group_box.setObjectName(_fromUtf8("group_box"))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.group_box.setSizePolicy(sizePolicy)

        self.group_box_grid = QtGui.QGridLayout(self.group_box)
        self.group_box_grid.setObjectName(_fromUtf8("group_box_grid"))

        self.list_view = QtGui.QListView(self.group_box)
        self.list_view.setObjectName(_fromUtf8("l1"))
        self.group_box_grid.addWidget(self.list_view, 0, 3, 1, 1)

        self.model = QtGui.QStandardItemModel()

        self.label = QtGui.QLabel(self.group_box)
        self.label.setObjectName(_fromUtf8("label"))
        self.group_box_grid.addWidget(self.label, 1, 0, 1, 4)

        self.ver_lay1 = QtGui.QVBoxLayout()
        self.ver_lay1.setObjectName(_fromUtf8("ver_lay1"))

        self.check_box = QtGui.QCheckBox(self.group_box)
        self.check_box.setObjectName(_fromUtf8("c1"))
        self.ver_lay1.addWidget(self.check_box)
        self.check_box.setChecked(self.__search_flag)

        self.check_box_2 = QtGui.QCheckBox(self.group_box)
        self.check_box_2.setObjectName(_fromUtf8("check_box_2"))
        self.ver_lay1.addWidget(self.check_box_2)
        self.check_box_2.setChecked(self.__show_unread_flag)

        self.btn_readall = QtGui.QPushButton(self.group_box)
        self.btn_readall.setObjectName(_fromUtf8("b1"))
        self.ver_lay1.addWidget(self.btn_readall)

        self.btn_open_url = QtGui.QPushButton(self.group_box)
        self.btn_open_url.setObjectName(_fromUtf8("b2"))
        self.ver_lay1.addWidget(self.btn_open_url)

        self.btn_load = QtGui.QPushButton(self.group_box)
        self.btn_load.setObjectName(_fromUtf8("b2"))
        self.ver_lay1.addWidget(self.btn_load)

        self.btn_delete = QtGui.QPushButton(self.group_box)
        self.btn_delete.setObjectName(_fromUtf8("b3"))
        self.ver_lay1.addWidget(self.btn_delete)

        self.ver_lay2 = QtGui.QVBoxLayout()
        self.ver_lay2.setObjectName(_fromUtf8("ver_lay2"))

        self.btn_up = QtGui.QPushButton(self.group_box)
        self.btn_up.setObjectName(_fromUtf8("btn_up"))
        self.ver_lay2.addWidget(self.btn_up)

        self.label_empty = QtGui.QLabel(self.group_box)
        self.ver_lay2.addWidget(self.label_empty)

        self.btn_down = QtGui.QPushButton(self.group_box)
        self.btn_down.setObjectName(_fromUtf8("btn_down"))
        self.ver_lay2.addWidget(self.btn_down)

        self.group_box_grid.addLayout(self.ver_lay1, 0, 1, 1, 1)
        self.group_box_grid.addLayout(self.ver_lay2, 0, 4, 1, 1)

        self.graphic_view = QtGui.QGraphicsView(self.group_box)
        #self.graphic_view.setRenderHint(QtGui.QPainter.Antialiasing)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphic_view.sizePolicy().hasHeightForWidth())
        self.graphic_view.setSizePolicy(sizePolicy)
        self.graphic_view.setMinimumSize(QtCore.QSize(140, 200))
        self.graphic_view.setMaximumSize(QtCore.QSize(140, 200))
        self.graphic_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphic_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphic_view.setObjectName(_fromUtf8("graphic_view"))
        self.group_box_grid.addWidget(self.graphic_view, 0, 0, 1, 1)
        self.graphic_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.__scene = QtGui.QGraphicsScene()

        self.ui_class.scroll_con_grid.addWidget(self.group_box, self.__index, 0, 1, 1)

    def retranslate(self):
        self.group_box.setFont(BFONT)
        self.group_box.setTitle(_fromUtf8("({}) {}".format(self.__index + 1, self.__title)))

        ######## btn ########

        self.btn_readall.setFont(BFONT)
        self.update_btn_readall()

        self.btn_open_url.setFont(BFONT)
        self.btn_open_url.setText(_translate("MainWindow", self.ui_class.data.ld_ui_get_a_value("item-btn_open_url"), None))

        self.btn_load.setFont(BFONT)
        self.btn_load.setText(_translate("MainWindow", self.ui_class.data.ld_ui_get_a_value("item-btn_load"), None))

        self.btn_delete.setFont(BFONT)
        self.update_btn_delete()

        self.btn_up.setText(self.ui_class.data.get_value("ui", "item-btn_up"))

        self.btn_down.setText(self.ui_class.data.get_value("ui", "item-btn_down"))

        ######## etc ########

        self.check_box.setFont(BFONT)
        self.check_box.setText(_translate("MainWindow", self.ui_class.data.ld_ui_get_a_value("item-check_box"), None))

        self.check_box_2.setFont(BFONT)
        self.check_box_2.setText(_translate("MainWindow", self.ui_class.data.ld_ui_get_a_value("item-check_box_2"), None))

        self.update_label()

        ######## tooltip ########

        QtGui.QToolTip.setFont(BFONT)

        self.check_box.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-check_box-tooltip"))
        self.check_box_2.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-check_box_2-tooltip"))
        self.btn_readall.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-btn_readall-tooltip"))
        self.btn_open_url.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-btn_open_url-tooltip"))
        self.btn_load.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-btn_open_url-tooltip"))
        self.btn_delete.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-btn_delete-tooltip"))

        self.graphic_view.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-graphic_view-tooltip"))
        self.list_view.setToolTip(self.ui_class.data.ld_ui_get_a_value("item-list_view-tooltip"))

    def connect_signals(self):
        self.graphic_view.customContextMenuRequested.connect(self.open_con_graphic)

    ######## ui ########

    def set_thum(self):
        pic = QtGui.QPixmap(self.get_img_dir_s())

        size = self.graphic_view.size()

        height_i = size.height() - 2
        width_i = size.width() - 2
        size.setHeight(height_i)
        size.setWidth(width_i)
        if self.ui_class.cfg["item_list-hq_thum"]:
            pic = pic.scaled(size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        else:
            pic = pic.scaled(size, QtCore.Qt.KeepAspectRatio)

        self.__scene.addItem(QtGui.QGraphicsPixmapItem(pic))
        self.graphic_view.setScene(self.__scene)

    def draw_list(self):
        self.model.clear()
        self.drawn_chap_l = []
        printed = False
        if len(self.__chapter_l) == 0:
            vitem = QtGui.QStandardItem()
            vitem.setFont(BFONT)
            vitem.setCheckable(False)
            vitem.setEditable(False)
            vitem.setText(self.ui_class.data.get_value("ui", "item-list_view-empty"))
            self.model.appendRow(vitem)
        else:
            for x in self.__chapter_l:
                vitem = QtGui.QStandardItem()
                vitem.setFont(BFONT)
                if is_new(x[3]):
                    vitem.setText("{}  {}".format(x[1], self.ui_class.data.get_value("ui", "item-list_view-new")))
                else:
                    vitem.setText("{}".format(x[1]))
                vitem.setCheckable(True)
                vitem.setEditable(False)
                if x[0]:
                    if self.__show_unread_flag:
                        continue
                    vitem.setCheckState(2)
                else:
                    vitem.setCheckState(0)
                self.model.appendRow(vitem)
                self.drawn_chap_l.append(x[2])
                printed = True

            if not printed:
                vitem = QtGui.QStandardItem()
                vitem.setFont(BFONT)
                vitem.setCheckable(False)
                vitem.setEditable(False)
                if self.ui_class.cfg["show_read_all"]:
                    vitem.setText(self.ui_class.data.get_value("ui", "item-list_view-read_all"))
                else:
                    vitem.setText("")
                self.model.appendRow(vitem)

        self.update_btn_readall()
        self.list_view.setModel(self.model)

    ########

    def open_con_graphic(self, position):
        menu_action_t = (
            {"name":self.ui_class.data.get_value("ui", "con_menu-show_thum"), "func":self.show_thum,
             "icon":self.get_img_dir_s()},
        )

        menu = QtGui.QMenu()
        menu.setFont(BFONT)
        for x_d in menu_action_t:
            action = QtGui.QAction(x_d["name"], menu)
            if "icon" in x_d.keys():
                icon = QtGui.QIcon(x_d["icon"])
                action.setIcon(icon)
            menu.addAction(action)

        selected_action = menu.exec_(self.graphic_view.viewport().mapToGlobal(position))
        if not selected_action:
            return

        selected_s = selected_action.text()
        for x_d in menu_action_t:
            if selected_s == x_d["name"]:
                x_d["func"]()

    def show_thum(self, option=2):
        if option == 1:
            min_size_i = 600
            smaller_i = 50

            win_width = self.ui_class.MainWindow.size().width() - smaller_i
            if win_width < min_size_i:
                win_width = min_size_i
            win_height = self.ui_class.MainWindow.size().height() - smaller_i
            if win_height < min_size_i:
                win_height = min_size_i
            win_size_t = (win_width, win_height)
        elif option == 2:
            a = win32api.GetSystemMetrics(0) // 1.2
            b = win32api.GetSystemMetrics(1) // 1.2
            win_size_t = (a, b)
        elif option == 3:
            a = win32api.GetSystemMetrics(0) // 1.5
            b = win32api.GetSystemMetrics(1) // 1.5
            win_size_t = (a, b)
        elif option == 4:
            a = win32api.GetSystemMetrics(0) // 2.2
            b = win32api.GetSystemMetrics(1) // 2.2
            win_size_t = (a, b)
        else:
            return -1

        a = ImageView(self.__title, self.get_img_dir_s(), win_size_t)
        a.exec_()

    ######## setters for members ########

    def set_title(self, a_str: str):
        if isinstance(a_str, str):
            self.__title = a_str
            self.group_box.setTitle(_fromUtf8("({}) {}".format(self.__index + 1, self.__title)))
        else:
            raise WTF

    def set_last_up(self, a_int: int):
        if isinstance(a_int, int):
            self.__last_up = a_int
            self.update_label()
        else:
            raise WTF

    def set_search_flag(self, boolean: bool):
        if isinstance(boolean, bool):
            self.__search_flag = boolean
        else:
            raise WTF

    def set_show_unread_flag(self, boolean: bool):
        if isinstance(boolean, bool):
            self.__show_unread_flag = boolean
        else:
            raise WTF

    def set_delete_flag(self, boolean: bool):
        if isinstance(boolean, bool):
            self.__delete_flag = boolean
        else:
            raise WTF

    def set_last_checked_count_i(self, a_int: int):
        if isinstance(a_int, int):
            self.__last_checked_count_i = a_int
        else:
            raise WTF

    def set_thum_url(self, a_str):
        if isinstance(a_str, str):
            self.__thum_url = a_str
        else:
            raise WTF

    ######## getters for members ########

    def get_last_checked_count_i(self):
        return self.__last_checked_count_i

    def get_search_flag(self):
        return self.__search_flag

    def get_show_unread_flag(self):
        return self.__show_unread_flag

    def get_delete_flag(self):
        return self.__delete_flag

    def get_url(self):
        return self.__url

    def get_number(self):
        return self.__number

    def get_thum_url(self):
        return self.__thum_url

    def get_img_dir_s(self):
        return "{}{}.jpg".format(THUMB_FOL_S, self.__number)

    def get_chapter_l(self):
        return self.__chapter_l

    def get_index(self):
        return self.__index

    def get_last_up(self):
        return self.__last_up

    def get_title(self):
        return self.__title

    def get_full_data(self):
        a = (self.__number, self.__url, self.__thum_url, self.__title, self.__chapter_l, self.__last_up,
             self.__search_flag, self.__delete_flag, self.__show_unread_flag)
        return a

    ######## ui retranslator according to context ########

    def update_btn_readall(self):
        if self.is_every_chapter_read():
            self.btn_readall.setText(self.ui_class.data.ld_ui_get_a_value("item-btn_readall-true"))
        else:
            self.btn_readall.setText(self.ui_class.data.ld_ui_get_a_value("item-btn_readall-false"))

    def update_btn_delete(self):
        if self.__delete_flag:
            self.btn_delete.setText(self.ui_class.data.ld_ui_get_a_value("item-btn_delete-true"))
        else:
            self.btn_delete.setText(self.ui_class.data.ld_ui_get_a_value("item-btn_delete-false"))

    def update_label(self):
        if self.__delete_flag:
            self.label.setText(self.ui_class.data.ld_ui_get_a_value("item-label-delete"))
        elif self.__last_up > 0:
            before_i = int(time.time() - self.__last_up)
            time_t = sec_to_string(before_i)
            time_multiplyer_s = self.ui_class.data.ld_ui_get_a_value("misc-time-{}".format(time_t[1]))
            time_s = "{}{}{}".format(time_t[0], time_multiplyer_s, self.ui_class.data.get_value("ui", "misc-time-plural"))
            self.label.setText(self.ui_class.data.ld_ui_get_a_value("item-label-last_update").format(time_s))
        elif self.__last_up == 0:
            self.label.setText(self.ui_class.data.ld_ui_get_a_value("item-label-search_required"))
        elif self.__last_up == -1:
            self.label.setText(self.ui_class.data.ld_ui_get_a_value("item-label-failed"))

    ######## bool inspection ########

    def image_exists(self):
        if os.path.isfile(self.get_img_dir_s()):
            return True
        else:
            return False

    def is_every_chapter_read(self):
        for x_t in self.__chapter_l:
            if not x_t[0]:
                return False
        return True

    ######## get info ########

    def last_chap_date_distance(self):
        last_one_i = -1
        for x_t in self.__chapter_l:
            if x_t[3] > last_one_i:
                last_one_i = x_t[3]
        distance_i = int(time.time()) - last_one_i

        if last_one_i == -1:
            raise WTF
        elif distance_i < 0:
            raise WTF
        else:
            return distance_i

    def get_save_string(self):
        chapter_s = ''
        for x_t in self.__chapter_l:
            chapter_s += "{}|{}|{}|{}>".format(*x_t)
        chapter_s.rstrip('&')
        return "{}<{}<{}<{}<{}<{}<{}<{}<{}<{}\n%divider%\n". \
            format(self.__number, self.__index, self.__url, self.__thum_url, self.__title, chapter_s,
                   self.__last_up, self.__search_flag, self.__delete_flag, self.__show_unread_flag)

    def get_num_of_checked(self):
        checked_i = 0
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.checkState() == 2:
                checked_i += 1
        return checked_i

    def find_url_by_name(self, chap_name: str):
        for x_t in self.__chapter_l:
            if x_t[1] == chap_name:
                return x_t[2]
        raise WTF

    def find_index_by_chap_name(self, chap_name: str):
        for x, x_t in enumerate(self.__chapter_l):
            if x_t[1] == chap_name:
                return x
        raise WTF(self.__chapter_l)

    def find_index_by_chap_url(self, chap_url:str):
        for x, x_t in enumerate(self.__chapter_l):
            if x_t[2] == chap_url:
                return x
        raise WTF(self.__chapter_l)

    def remaining_chaps(self):
        not_read_count_i = 0
        new_count_i = 0
        for x_t in self.__chapter_l:
            if x_t[0] == 0:
                not_read_count_i += 1
            if is_new(x_t[3]):
                new_count_i += 1
        return not_read_count_i, new_count_i

    def print_string(self, not_read_only:bool=True, file=None):
        title_printed = False
        for x_t in self.__chapter_l:
            if not not_read_only or not x_t[0]:
                if not title_printed:
                    print(file=file)
                    print(self.__title, file=file)
                    print(self.__url, file=file)
                    title_printed = True
                print("\n\t{}".format(x_t[1]), file=file)
                print("\t{}".format(x_t[2]), file=file)

    ######## task, returns None or result code ########

    def delete(self):
        self.check_box.deleteLater()
        self.check_box_2.deleteLater()
        self.btn_readall.deleteLater()

        self.ver_lay1.removeWidget(self.check_box)
        self.ver_lay1.removeWidget(self.check_box_2)
        self.ver_lay1.removeWidget(self.btn_readall)
        self.ver_lay1.removeWidget(self.btn_delete)
        self.ver_lay1.removeWidget(self.btn_load)
        self.ver_lay1.removeWidget(self.btn_open_url)

        self.list_view.deleteLater()
        self.label.deleteLater()
        self.graphic_view.deleteLater()
        self.ver_lay1.deleteLater()
        self.ver_lay2.deleteLater()

        self.group_box_grid.removeWidget(self.list_view)
        self.group_box_grid.removeWidget(self.label)
        self.group_box_grid.removeWidget(self.graphic_view)
        self.group_box_grid.removeItem(self.ver_lay1)
        self.group_box_grid.removeItem(self.ver_lay2)

        self.group_box.deleteLater()

        self.ui_class.scroll_con_grid.removeWidget(self.group_box)
        prints("deleted : {}".format(self.__url))

    def reload_title(self):
        try:
            html_s = url_urllib_html(self.__url)
        except:
            clear_dirt_way(LOG_FOL_S)
            file_name = "{}{}.txt".format(LOG_FOL_S, mk_log_name("ReloadTitle"))
            f = open(file_name, 'w', encoding="utf8")
            traceback.print_exc(file=f)
            f.close()
            print("failed to reload title from web")
            return -1
        else:
            manga = m.MarumaruManga(html_s)
            title_s = manga.manga_title()
            self.set_title(title_s)
            return 0

    def reload_thum(self):
        self.ui_class.start_downloading_thum(self.get_number())

    def update_chapter_list(self, new_l: list):
        updated_l = []
        for x, x_t in enumerate(new_l):
            for y_t in self.__chapter_l:
                if x_t[2] == y_t[2]:
                    a_tuple = (y_t[0], x_t[1], x_t[2], y_t[3])
                    updated_l.append(a_tuple)
                    break
            else:
                updated_l.append(x_t)
        self.__chapter_l = updated_l

    def update_check_state(self):
        for x in range(self.list_view.model().rowCount()):
            chap_url_s = self.drawn_chap_l[x]
            check_state_i = self.model.item(x).checkState()
            index = self.find_index_by_chap_url(chap_url_s)

            if check_state_i == 2:
                a, b, c = self.__chapter_l[index][1:]
                self.__chapter_l[index] = (1, a, b, c)
            elif check_state_i == 0:
                a, b, c = self.__chapter_l[index][1:]
                self.__chapter_l[index] = (0, a, b, c)

    def read_all(self, mark_i: int = 1):
        for x, x_t in enumerate(self.__chapter_l):
            a, b, c = x_t[1:]
            self.__chapter_l[x] = (mark_i, a, b, c)


#### QDialogs ####


class OptionWindow(QtGui.QDialog):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        self.general_setting_combo_l = []

        self.size_policy_label_extend = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        self.size_policy_label_extend.setHorizontalStretch(0)
        self.size_policy_label_extend.setVerticalStretch(0)
        # size_policy_label_extend.setHeightForWidth(self.label_backup_save.sizePolicy().hasHeightForWidth())

        self.size_policy_btn_left_align = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        self.size_policy_btn_left_align.setHorizontalStretch(0)
        self.size_policy_btn_left_align.setVerticalStretch(0)
        # size_policy_btn_left_align.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())

        self.resize(600,500)
        self.setFont(BFONT)

        self.main_grid = QtGui.QGridLayout(self)

        self.tap_widget = QtGui.QTabWidget(self)
        self.main_grid.addWidget(self.tap_widget, 0, 0, 1, 5)

        self.btn_ok = QtGui.QPushButton(self)
        self.main_grid.addWidget(self.btn_ok, 1, 1, 1, 1)

        self.btn_cancel = QtGui.QPushButton(self)
        self.main_grid.addWidget(self.btn_cancel, 1, 2, 1, 1)

        self.btn_apply = QtGui.QPushButton(self)
        self.main_grid.addWidget(self.btn_apply, 1, 3, 1, 1)

        self.ui_tab_general()
        self.ui_tab_backup()
        self.ui_tab_info()

        self.retranslate()
        self.connect_sig()

    def retranslate(self):
        #### main ####

        self.setWindowTitle(self.ui.data.get_value("st", "window"))
        self.btn_ok.setText(self.ui.data.get_value("st", "main-ok"))
        self.btn_cancel.setText(self.ui.data.get_value("st", "main-cancel"))
        self.btn_apply.setText(self.ui.data.get_value("st", "main-apply"))

        #### general ####

        self.tap_widget.setTabText(0, self.ui.data.get_value("st", "general-tab"))
        self.cb_show_read_all.setText(self.ui.data.get_value("st", "general-cb_show_read_all"))
        self.cb_check_on_open.setText(self.ui.data.get_value("st", "general-cb_check_on_open"))

        self.label_main_list_view.setText('\n' + self.ui.data.get_value("st", "general-label_main_list_view"))
        self.cb_main_list_show_stat_remaining.setText(self.ui.data.get_value("st", "general-cb_main_list_show_stat_remaining"))
        self.cb_main_list_show_stat_new_ones.setText(self.ui.data.get_value("st", "general-cb_main_list_show_stat_new_ones"))
        self.cb_main_list_show_stat_last_failed.setText(self.ui.data.get_value("st", "general-cb_main_list_show_stat_last_failed"))
        self.cb_main_list_how_stat_over_month.setText(self.ui.data.get_value("st", "general-cb_main_list_how_stat_over_month"))
        self.cb_main_list_show_stat_delete.setText(self.ui.data.get_value("st", "general-cb_main_list_show_stat_delete"))
        self.cb_main_list_show_no_chap_for_awhile.setText(self.ui.data.get_value("st", "general-cb_main_list_show_no_chap_for_awhile"))
        self.cb_main_list_index_same_len_num.setText(self.ui.data.get_value("st", "general-cb_main_list_index_same_len_num"))

        self.label_item_list_view.setText('\n' + self.ui.data.get_value("st", "general-label_item_list_view"))
        self.cb_item_list_hq_thum.setText(self.ui.data.get_value("st", "general-cb_item_list_hq_thum"))

        self.label_startup.setText('\n' + self.ui.data.get_value("st", "general-label_startup"))
        self.label_sort_on_start.setText(self.ui.data.get_value("st", "general-label_sort_one_start"))
        self.retranslsate_com_sort_opt()
        self.retranslate_com_sort_reverse()
        self.btn_general_sort_now.setText(self.ui.data.get_value("st", "general-btn_general_sort_now"))

        #### backup ####

        self.tap_widget.setTabText(1, self.ui.data.get_value("st", "backup-tab"))
        self.label_backup_save.setText("{}\n{}".format(self.ui.data.get_value("st", "backup-label_backup_save-1"),
                                                       self.ui.data.get_value("st", "backup-label_backup_save-2")))
        self.btn_backup_save.setText(self.ui.data.get_value("st", "backup-btn_backup_save"))
        self.label_backup_load.setText("\n{}\n{}".format(self.ui.data.get_value("st", "backup-label_backup_load-1"),
                                                         self.ui.data.get_value("st", "backup-label_backup_load-2")))
        self.btn_backup_load.setText(self.ui.data.get_value("st", "backup-btn_backup_load"))
        self.btn_backup_refresh.setText(self.ui.data.get_value("st", "backup-btn_backup_refresh"))

        #### info ####

        self.tap_widget.setTabText(2, self.ui.data.get_value("st", "info-tab"))
        full_l = []
        for x in range(1, 50):
            try:
                a_text = self.ui.data.get_value("st", "info-line-{}".format(x))
            except KeyError:
                break
            else:
                full_l.append(a_text)
        full_s = '\n'.join(full_l)

        self.empty_label.setText(full_s)

    def ui_tab_general(self):
        self.tap_general = QtGui.QWidget()

        self.grid_main_general = QtGui.QGridLayout(self.tap_general)

        self.scrolla_general = QtGui.QScrollArea(self.tap_general)
        self.scrolla_general.setWidgetResizable(True)

        self.scrolla_contnets_general = QtGui.QWidget()
        self.scrolla_contnets_general.setGeometry(QtCore.QRect(0, 0, 436, 249))

        self.grid_scoll_general = QtGui.QGridLayout(self.scrolla_contnets_general)

        self.general_setting_tf_l = []

        self.cb_show_read_all = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_show_read_all.setChecked(self.ui.cfg["show_read_all"])
        self.grid_scoll_general.addWidget(self.cb_show_read_all, 0, 0, 1, 2)
        self.general_setting_tf_l.append((self.cb_show_read_all, "show_read_all"))

        self.cb_check_on_open = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_check_on_open.setChecked(self.ui.cfg["check_on_open"])
        self.grid_scoll_general.addWidget(self.cb_check_on_open, 1, 0, 1, 2)
        self.general_setting_tf_l.append((self.cb_check_on_open, "check_on_open"))

        ######## Main List ########

        self.label_main_list_view = QtGui.QLabel(self.scrolla_contnets_general)
        self.label_main_list_view.setAlignment(QtCore.Qt.AlignCenter)
        self.label_main_list_view.setSizePolicy(self.size_policy_label_extend)
        self.grid_scoll_general.addWidget(self.label_main_list_view, 2, 0, 1, 2)

        self.cb_main_list_show_stat_remaining = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_show_stat_remaining.setChecked(self.ui.cfg["main_list-show_stat-remaining"])
        self.grid_scoll_general.addWidget(self.cb_main_list_show_stat_remaining, 3, 0, 1, 1)
        self.general_setting_tf_l.append((self.cb_main_list_show_stat_remaining, "main_list-show_stat-remaining"))

        self.com_main_list_show_stat_remaining_contain = ContainerComboBox(
            self.scrolla_contnets_general, self.ui.cfg["main_list-show_stat-remaining-container"])
        self.grid_scoll_general.addWidget(self.com_main_list_show_stat_remaining_contain, 3, 1, 1, 1)
        self.general_setting_combo_l.append((self.com_main_list_show_stat_remaining_contain,
                                             "main_list-show_stat-remaining-container"))

        self.cb_main_list_show_stat_new_ones = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_show_stat_new_ones.setChecked(self.ui.cfg["main_list-show_stat-new_ones"])
        self.grid_scoll_general.addWidget(self.cb_main_list_show_stat_new_ones, 4, 0, 1, 1)
        self.general_setting_tf_l.append((self.cb_main_list_show_stat_new_ones, "main_list-show_stat-new_ones"))

        self.com_main_list_show_stat_new_ones_contain = ContainerComboBox(
            self.scrolla_contnets_general, self.ui.cfg["main_list-show_stat-new_ones_container"])
        self.grid_scoll_general.addWidget(self.com_main_list_show_stat_new_ones_contain, 4, 1, 1, 1)
        self.general_setting_combo_l.append((self.com_main_list_show_stat_new_ones_contain,
                                             "main_list-show_stat-new_ones_container"))

        self.cb_main_list_show_stat_last_failed = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_show_stat_last_failed.setChecked(self.ui.cfg["main_list-show_stat-last_failed"])
        self.grid_scoll_general.addWidget(self.cb_main_list_show_stat_last_failed, 5, 0, 1, 1)
        self.general_setting_tf_l.append((self.cb_main_list_show_stat_last_failed, "main_list-show_stat-last_failed"))

        self.com_main_list_show_stat_last_failed_contain = ContainerComboBox(
            self.scrolla_contnets_general, self.ui.cfg["main_list-show_stat-last_failed-container"])
        self.grid_scoll_general.addWidget(self.com_main_list_show_stat_last_failed_contain, 5, 1, 1, 1)
        self.general_setting_combo_l.append((self.com_main_list_show_stat_last_failed_contain,
                                             "main_list-show_stat-last_failed-container"))

        self.cb_main_list_how_stat_over_month = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_how_stat_over_month.setChecked(self.ui.cfg["main_list-show_stat-over_month"])
        self.grid_scoll_general.addWidget(self.cb_main_list_how_stat_over_month, 6, 0, 1, 1)
        self.general_setting_tf_l.append((self.cb_main_list_how_stat_over_month, "main_list-show_stat-over_month"))

        self.com_main_list_show_stat_over_month_contain = ContainerComboBox(
            self.scrolla_contnets_general, self.ui.cfg["main_list-show_stat-over_month-container"])
        self.grid_scoll_general.addWidget(self.com_main_list_show_stat_over_month_contain, 6, 1, 1, 1)
        self.general_setting_combo_l.append((self.com_main_list_show_stat_over_month_contain,
                                             "main_list-show_stat-over_month-container"))

        self.cb_main_list_show_stat_delete = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_show_stat_delete.setChecked(self.ui.cfg["main_list-show_stat-delete"])
        self.grid_scoll_general.addWidget(self.cb_main_list_show_stat_delete, 7, 0, 1, 1)
        self.general_setting_tf_l.append((self.cb_main_list_show_stat_delete, "main_list-show_stat-delete"))

        self.com_main_list_show_stat_delete_contain = ContainerComboBox(
            self.scrolla_contnets_general, self.ui.cfg["main_list-show_stat-delete-container"])
        self.grid_scoll_general.addWidget(self.com_main_list_show_stat_delete_contain, 7, 1, 1, 1)
        self.general_setting_combo_l.append((self.com_main_list_show_stat_delete_contain,
                                             "main_list-show_stat-delete-container"))

        self.cb_main_list_show_no_chap_for_awhile = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_show_no_chap_for_awhile.setChecked(self.ui.cfg["main_list-show_stat-last_chap_too_old"])
        self.grid_scoll_general.addWidget(self.cb_main_list_show_no_chap_for_awhile, 8, 0, 1, 1)
        self.general_setting_tf_l.append((self.cb_main_list_show_no_chap_for_awhile, "main_list-show_stat-last_chap_too_old"))

        self.com_main_list_show_no_chap_for_awhile_contain = ContainerComboBox(
            self.scrolla_contnets_general, self.ui.cfg["main_list-show_stat-last_chap_too_old-container"])
        self.grid_scoll_general.addWidget(self.com_main_list_show_no_chap_for_awhile_contain, 8, 1, 1, 1)
        self.general_setting_combo_l.append((self.com_main_list_show_no_chap_for_awhile_contain,
                                             "main_list-show_stat-last_chap_too_old-container"))

        self.cb_main_list_index_same_len_num = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_main_list_index_same_len_num.setChecked(self.ui.cfg["main_list-index-same_len_num"])
        self.grid_scoll_general.addWidget(self.cb_main_list_index_same_len_num, 9,0,1,2)
        self.general_setting_tf_l.append((self.cb_main_list_index_same_len_num,"main_list-index-same_len_num"))

        ######## Item list ########

        self.label_item_list_view = QtGui.QLabel(self.scrolla_contnets_general)
        self.label_item_list_view.setAlignment(QtCore.Qt.AlignCenter)
        self.label_item_list_view.setSizePolicy(self.size_policy_label_extend)
        self.grid_scoll_general.addWidget(self.label_item_list_view, 10, 0, 1, 2)

        self.cb_item_list_hq_thum = QtGui.QCheckBox(self.scrolla_contnets_general)
        self.cb_item_list_hq_thum.setChecked(self.ui.cfg["item_list-hq_thum"])
        self.grid_scoll_general.addWidget(self.cb_item_list_hq_thum, 11,0,1,2)
        self.general_setting_tf_l.append((self.cb_item_list_hq_thum, "item_list-hq_thum"))

        ######## Start-up Option ########

        self.label_startup = QtGui.QLabel(self.scrolla_contnets_general)
        self.label_startup.setAlignment(QtCore.Qt.AlignCenter)
        self.label_startup.setSizePolicy(self.size_policy_label_extend)
        self.grid_scoll_general.addWidget(self.label_startup, 12, 0, 1, 2)

        self.label_sort_on_start = QtGui.QLabel(self.scrolla_contnets_general)
        self.label_sort_on_start.setSizePolicy(self.size_policy_label_extend)
        self.grid_scoll_general.addWidget(self.label_sort_on_start, 13, 0, 1, 2)

        self.com_main_startup_sort_opt = QtGui.QComboBox(self.scrolla_contnets_general)
        self.com_main_startup_sort_opt.currentIndexChanged.connect(self.everytime)
        self.grid_scoll_general.addWidget(self.com_main_startup_sort_opt, 14, 0, 1, 2)
        self.general_setting_combo_l.append((self.com_main_startup_sort_opt, "main-sort_on_init-option"))

        self.com_main_startup_sort_reverse = QtGui.QComboBox(self.scrolla_contnets_general)
        self.com_main_startup_sort_reverse.currentIndexChanged.connect(self.everytime)
        self.grid_scoll_general.addWidget(self.com_main_startup_sort_reverse, 15, 0 , 1, 2)
        self.general_setting_combo_l.append((self.com_main_startup_sort_reverse, "main-sort_on_init-reverse"))

        self.btn_general_sort_now = QtGui.QPushButton(self.scrolla_contnets_general)
        self.btn_general_sort_now.clicked.connect(self.btn_general_sort_now_func)
        self.grid_scoll_general.addWidget(self.btn_general_sort_now, 16, 0, 1, 2)

        self.empty_label_general = QtGui.QLabel(self.scrolla_contnets_general)
        self.grid_scoll_general.addWidget(self.empty_label_general, 100, 0, 1, 2)

        self.scrolla_general.setWidget(self.scrolla_contnets_general)
        self.grid_main_general.addWidget(self.scrolla_general)

        self.tap_widget.addTab(self.tap_general, '0')

    def ui_tab_backup(self):
        self.tap_backup = QtGui.QWidget()
        self.grid_backup = QtGui.QGridLayout(self.tap_backup)

        self.label_backup_save = QtGui.QLabel(self.tap_backup)
        self.label_backup_save.setSizePolicy(self.size_policy_label_extend)
        self.grid_backup.addWidget(self.label_backup_save, 0,0,1,3)

        self.btn_backup_save = QtGui.QPushButton(self.tap_backup)
        self.btn_backup_save.setSizePolicy(self.size_policy_btn_left_align)
        self.grid_backup.addWidget(self.btn_backup_save, 1,0,1,3)

        self.label_backup_load = QtGui.QLabel(self.tap_backup)
        self.label_backup_load.setSizePolicy(self.size_policy_label_extend)
        self.label_backup_load.setWordWrap(True)
        self.grid_backup.addWidget(self.label_backup_load, 2,0,1,3)

        self.list_widget_backup_load = QtGui.QListWidget(self.tap_backup)
        self.grid_backup.addWidget(self.list_widget_backup_load,3,0,1,3)
        self.refresh_list_view()

        self.btn_backup_load = QtGui.QPushButton(self.tap_backup)
        self.btn_backup_load.setSizePolicy(self.size_policy_btn_left_align)
        self.grid_backup.addWidget(self.btn_backup_load,4,0,1,1)

        self.btn_backup_refresh = QtGui.QPushButton(self.tap_backup)
        self.btn_backup_refresh.setSizePolicy(self.size_policy_btn_left_align)
        self.grid_backup.addWidget(self.btn_backup_refresh, 4, 1, 1, 1)

        self.label_backup_empty = QtGui.QLabel(self.tap_backup)
        self.grid_backup.addWidget(self.label_backup_empty, 4, 2, 1, 1)

        self.tap_widget.addTab(self.tap_backup, '1')

        self.label_tap_backup = QtGui.QLabel(self.tap_backup)
        self.grid_backup.addWidget(self.label_tap_backup)

    def ui_tab_info(self):
        self.tap_info = QtGui.QWidget()
        self.grid2 = QtGui.QGridLayout(self.tap_info)

        self.empty_label = QtGui.QLabel(self.tap_info)
        self.empty_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid2.addWidget(self.empty_label, 0, 0, 1, 1)

        self.tap_widget.addTab(self.tap_info, '2')

    def connect_sig(self):
        self.btn_ok.clicked.connect(self.btn_ok_func)
        self.btn_cancel.clicked.connect(self.btn_cancel_func)
        self.btn_apply.clicked.connect(self.btn_apply_func)

        self.btn_backup_save.clicked.connect(self.btn_backup_save_func)
        self.btn_backup_load.clicked.connect(self.btn_backup_load_func)
        self.btn_backup_refresh.clicked.connect(self.btn_backup_refresh_func)

    ######## btn signal interface ########

    def btn_ok_func(self):
        self.apply_settings()
        self.ui.save_config()

        self.ui.refresh_all_listviews()
        self.ui.refresh_all_label()

        self.close()

    def btn_cancel_func(self):
        self.close()

    def btn_apply_func(self):
        self.apply_settings()
        self.ui.save_config()

        self.ui.refresh_all_listviews()
        self.ui.refresh_all_label()

    def btn_backup_save_func(self):
        self.ui.backup_data()
        self.refresh_list_view()
        NoticeWindow(self.ui.data.get_value("st", "backup-notice-saved"), self.ui).exec_()

    def btn_backup_load_func(self):
        a = self.list_widget_backup_load.selectedIndexes()
        if len(a) == 1:
            selected_index = a[0].row()
            selected_file_s = self.backup_file_l[selected_index]
            prints("selected backup file : {}".format(selected_file_s))

            NoticeWindow(self.ui.data.get_value("st", "backup-notice-success"), self.ui).exec_()
        elif len(a) == 0:
            NoticeWindow(self.ui.data.get_value("st", "backup-notice-no_file"), self.ui).exec_()
        else:
            raise WTF

    def btn_backup_refresh_func(self):
        self.refresh_list_view()

    def btn_general_sort_now_func(self):
        self.btn_general_sort_now.setDisabled(True)
        option_i = self.com_main_startup_sort_opt.currentIndex()
        if not option_i:
            return
        reverse_i = self.com_main_startup_sort_reverse.currentIndex()
        self.ui.entire_task_for_sorting(option_i, bool(reverse_i))

    ######## retranslate ########

    def retranslsate_com_sort_opt(self):
        self.com_main_startup_sort_opt.addItem(self.ui.data.get_value("st", "general-com_main_startup_sort_opt-0"))
        self.com_main_startup_sort_opt.addItem(self.ui.data.get_value("st", "general-com_main_startup_sort_opt-1"))
        self.com_main_startup_sort_opt.addItem(self.ui.data.get_value("st", "general-com_main_startup_sort_opt-2"))
        self.com_main_startup_sort_opt.addItem(self.ui.data.get_value("st", "general-com_main_startup_sort_opt-3"))

        self.com_main_startup_sort_opt.setCurrentIndex(self.ui.cfg["main-sort_on_init-option"])

    def retranslate_com_sort_reverse(self):
        self.com_main_startup_sort_reverse.addItem(self.ui.data.get_value("st", "general-com_main_startup_sort_reverse-0"))
        self.com_main_startup_sort_reverse.addItem(self.ui.data.get_value("st", "general-com_main_startup_sort_reverse-1"))

        self.com_main_startup_sort_reverse.setCurrentIndex(self.ui.cfg["main-sort_on_init-reverse"])

    ######## task ########

    def apply_settings(self):
        for x_t in self.general_setting_tf_l:
            if x_t[0].checkState() == 2:
                self.ui.cfg[x_t[1]] = True
            else:
                self.ui.cfg[x_t[1]] = False

        for x_t in self.general_setting_combo_l:
            self.ui.cfg[x_t[1]] = x_t[0].currentIndex()

        print("setting applied")

    def refresh_list_view(self):
        self.list_widget_backup_load.clear()
        self.backup_file_l = get_backup_file_list()
        for x_s in self.backup_file_l:
            head_cut = x_s.rindex('-') + 1

            a = datetime.datetime.fromtimestamp(int(x_s[head_cut:]))
            text_s = a.strftime("%Y-%m-%d-%H-%M-%S")
            text_s = "{}-{}-{} {}:{}:{}".format(*text_s.split('-'))

            item = QtGui.QListWidgetItem(text_s)
            item.setFont(BFONT)
            self.list_widget_backup_load.addItem(item)

    def everytime(self):
        self.btn_general_sort_now.setDisabled(False)


class NoticeWindow(QtGui.QDialog):
    def __init__(self, text, ui_class, align_option:bool=True):
        super().__init__()

        self.setWindowTitle(ui_class.data.get_value("ui", "notice-window"))
        self.setFont(BFONT)
        self.setMinimumSize(200,80)

        self.grid = QtGui.QGridLayout(self)

        self.label_empty = QtGui.QLabel(self)
        self.grid.addWidget(self.label_empty, 1,0,1,1)
        self.grid.addWidget(self.label_empty, 1,2,1,1)

        self.label = QtGui.QLabel(self)
        self.label.setText(text)
        self.label.setFont(BFONT)
        self.label.setWordWrap(True)
        if align_option:
            self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(BFONT)
        self.grid.addWidget(self.label, 0,0,1,3)

        self.btn_ok = QtGui.QPushButton(ui_class.data.get_value("ui", "notice-ok"), self)
        self.btn_ok.clicked.connect(self.close_widget)
        self.btn_ok.setFont(BFONT)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.btn_ok.setSizePolicy(size_policy)
        self.grid.addWidget(self.btn_ok, 1,1,1,1)

    def close_widget(self):
        self.close()


class ImageView(QtGui.QDialog):
    def __init__(self, title_s:str, img_dir_s:str, size_t:tuple):
        super().__init__()
        self.setWindowTitle(title_s)

        pic = QtGui.QPixmap(img_dir_s)
        self.__scene = QtGui.QGraphicsScene()
        self.__gview = QtGui.QGraphicsView(self)

        a, b = resize_keep_aspect(size_t[0], size_t[1], *Image.open(img_dir_s).size)

        size = QtCore.QSize(a - 2, b - 2)
        pic = pic.scaled(size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        self.__scene.addItem(QtGui.QGraphicsPixmapItem(pic))
        self.__scene.setBackgroundBrush(QtCore.Qt.black)
        self.__gview.setScene(self.__scene)

        self.__gview.resize(a, b)
        self.setFixedSize(a, b)


#### QThreads ####


class FetchAll(QThread):
    def __init__(self, ui_class, number_l:list):
        QThread.__init__(self)
        self.number_l = number_l
        self.ui = ui_class

    def __del__(self):
        self.wait()

    def load_from_web(self):
        failed_i = 0
        new_accum_i = 0
        for x_number in self.number_l:
            try:
                target_I = self.ui.get_item_from_number_safe(x_number)
                assert target_I.get_number() == x_number

                try_count = 0
                while True:
                    try_count += 1
                    try:
                        html_s = url_urllib_html(target_I.get_url())
                    except ue.URLError:
                        if try_count >= TRY_I:
                            raise ue.URLError(": failed after {} retry.".format(TRY_I))
                        else:
                            print("retrying... URLError")
                            time.sleep(1)
                    else:
                        break

                manga = m.MarumaruManga(html_s)
                title_s = manga.manga_title()
                chapter_t_l = manga.chapters()
                new_i = len(chapter_t_l) - len(target_I.get_chapter_l())
                if new_i < 0:
                    new_i = 0
                if new_i > 0:
                    prints("here is new chapters : {}\n{}\n{}".format(title_s, chapter_t_l, target_I.get_chapter_l()))
                new_accum_i += new_i

                try:
                    thum_url_s = manga.thumbnail_link()
                except m.FailedToFindThumbnail:
                    print("failed to find thumbnail.")
                    thum_url_s = ''

                self.emit(QtCore.SIGNAL('fetch_all_one_finished(PyQt_PyObject)'),
                          (x_number, int(time.time()), title_s, chapter_t_l, thum_url_s))
            except:
                clear_dirt_way(LOG_FOL_S)
                file_name = "{}{}.txt".format(LOG_FOL_S, mk_log_name("FetchAll"))
                with open(file_name, 'w', encoding="utf8") as f:
                    traceback.print_exc(file=f)

                failed_i += 1
                self.emit(QtCore.SIGNAL('fetch_all_one_finished(PyQt_PyObject)'), (x_number,))
                continue

        self.emit(QtCore.SIGNAL('fetch_all_all_finished(PyQt_PyObject)'), (failed_i, new_accum_i))

    def run(self):
        self.load_from_web()


class FetchOne(QThread):
    def __init__(self, number:int, url:str, thread_index:int):
        QThread.__init__(self)
        self.number = number
        self.url = url
        self.thread_index = thread_index

    def __del__(self):
        self.wait()

    def load_from_web(self):
        prints("start fetching thread: {}".format(self.url))
        try:
            try_count = 0
            while True:
                try_count += 1
                try:
                    html_s = url_urllib_html(self.url)
                except ue.URLError:
                    if try_count >= TRY_I:
                        raise ue.URLError(": failed after {} retry.".format(TRY_I))
                    else:
                        print("retrying... URLError")
                        time.sleep(1)
                else:
                    break
            manga = m.MarumaruManga(html_s)
            title_s = manga.manga_title()
            chapter_t_l = manga.chapters()
            try:
                thum_url_s = manga.thumbnail_link()
            except m.FailedToFindThumbnail:
                print("failed to find thumbnail.")
                thum_url_s = ''
            self.emit(QtCore.SIGNAL('fetch_one_finished(PyQt_PyObject)'),
                      (self.number, int(time.time()), title_s, chapter_t_l, thum_url_s, self.thread_index))
        except:
            clear_dirt_way(LOG_FOL_S)
            file_name = "{}{}.txt".format(LOG_FOL_S, mk_log_name("FetchOne"))
            f = open(file_name, 'w', encoding="utf8")
            traceback.print_exc(file=f)
            f.close()
            self.emit(QtCore.SIGNAL('fetch_one_finished(PyQt_PyObject)'), (self.number, self.thread_index))
            print("failed signal sent")

    def run(self):
        self.load_from_web()


class DownloadImage(QThread):
    def __init__(self, item_class):
        QThread.__init__(self)
        self.item = item_class

    def __del__(self):
        self.wait()

    def load_from_web(self):
        try:
            clear_dirt_way(THUMB_FOL_S)

            opener = ur.URLopener()
            opener.addheader('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')
            filename, headers = opener.retrieve(self.item.get_thum_url(),self.item.get_img_dir_s())

            a_img = Image.open(self.item.get_img_dir_s())
            wid, hei = a_img.size
            a_img.save(self.item.get_img_dir_s())

            self.emit(QtCore.SIGNAL('thum_finished(PyQt_PyObject)'), (0, self.item.get_number()))
        except:
            clear_dirt_way(LOG_FOL_S)
            file_name = "{}{}.txt".format(LOG_FOL_S, mk_log_name("DownloadImage"))
            f = open(file_name, 'w', encoding="utf8")
            traceback.print_exc(file=f)
            f.write("\nurl : {}".format(self.item.get_thum_url()))
            f.close()
            print("failed to download image.")

    def run(self):
        self.load_from_web()


#### Misc ####


class DataContainer:
    def __init__(self, language:str):
        self.__ld_ui = dict()
        self.__ld_st = dict()

        self.__wrapper_s = "{}"
        self.__loaded_language_s = ""

        self.ld_reload(language)

    def ld_reload(self, file_name:str):
        file_dir_s = UI_DIR_S.format(file_name)
        self.__ld_ui = load_txt_into_dict(file_dir_s)

        file_dir_s = ST_DIR_S.format(file_name)
        self.__ld_st = load_txt_into_dict(file_dir_s)

        self.__loaded_language_s = file_name

    def ld_ui_get_a_value(self, key:str):
        return self.__wrapper_s.format(self.__ld_ui[key])

    def get_value(self, name:str, key:str):
        if name == "ui":
            return self.__wrapper_s.format(self.__ld_ui[key])
        elif name == "st":
            return self.__wrapper_s.format(self.__ld_st[key])
        else:
            raise WTF


class ContainerComboBox(QtGui.QComboBox):
    def __init__(self, QWidget_parent, current_s: str):
        super().__init__(QWidget_parent)

        for x_s in CONTAINER_T:
            self.addItem(x_s[0]+' '+x_s[1])

        self.setCurrentIndex(current_s)
        self.setMaximumWidth(65)


######## Main ########


def main():
    app = QtGui.QApplication(sys.argv)
    main_window = QtGui.QMainWindow()
    ui = UiMainWindow(main_window)
    main_window.show()
    ui.on_draw()
    a = app.exec_()
    ui.on_exit()
    sys.exit(a)


if __name__ == '__main__':
    main()
