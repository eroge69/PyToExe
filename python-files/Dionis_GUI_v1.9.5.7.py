from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import Qt  # это для отслеживания клавиши enter
from PyQt5.QtWidgets import QMessageBox  # для вывода ошибок
from n6600_ssh_dio import *
import os
import sys
from PyQt5.QtWidgets import QDesktopWidget, QApplication

hz = QApplication(sys.argv)  # нужно для размера экрана
window_size = QDesktopWidget().availableGeometry()
width = window_size.width() - 20
height = window_size.height() - 155


class Ui_MainWindow(object):
    def proverka_uz(self):
        uz = os.getlogin()
        spisok_uz = ['n6600-00-142', 'n6600-00142',  # Любенко
                     'n6600-00-151', 'n6600-00151']  # Соколов  

        if uz in spisok_uz:
            pass
        else:
            self.func_error('Учетная запись не принадлежит Администратору Диониса.\n'
                            'Дальнейшее функционирование недоступно.', 'Ошибка учетной записи')
            raise SystemExit(1)

    """основной метод """
    def func(self):
        self.kolvo_zapuskov = self.kolvo_zapuskov + 1
        self.list_finish = []
        self.list_index_all.clear()
        self.list_finish.clear()

        for delete_index in self.indexs_all:
            if self.indexs_all[0] < 10:  # удаляет индексы со знаками восклицания до 10 (ниже имени диониса)
                # чтобы потом со следующей строчки вывести
                del self.indexs_all[0]
            else:
                pass

        try:
            if self.indexs_all[0] != self.indexs_all[-1]:
                for a in range(self.indexs_all[0] + 1, self.indexs_all[1]):  # после того, как индекс 10 стал первым,
                    # наполняет список list_index_all индексами по порядку до следующего знака восклицания
                    self.list_index_all.append(a)
            else:
                pass

            for perebor_temp_index in self.list_index_all:
                vivod = self.dio.data[perebor_temp_index]  # сюда сохраняются индексы
                vivod_bez_enter = vivod.replace('\n', '')  # возвращает строку без enter
                self.list_finish.append(vivod_bez_enter)

            if self.indexs_all[0] == self.indexs_all[-1]:
                pass
            else:
                del self.indexs_all[0:1]

            # вкладка 7
            if 'cluster' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_7 = self.kolvo_zapuskov_vkladka_7 + 1
                self.tabWidget.addTab(self.vk7, "")
                self.vstavka_v_gui('Кластер', self.vk7, self.okno_vk7, self.kolvo_zapuskov_vkladka_7)

            elif 'ip forwarding' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_7 = self.kolvo_zapuskov_vkladka_7 + 1
                self.tabWidget.addTab(self.vk7, "")
                self.vstavka_v_gui('Прочее', self.vk7, self.okno_vk7, self.kolvo_zapuskov_vkladka_7)

            # вкладка 5
            elif 'ip access-list' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_5 = self.kolvo_zapuskov_vkladka_5 + 1
                self.vstavka_v_gui('Списки доступа', self.vk5, self.okno_vk5, self.kolvo_zapuskov_vkladka_5)

            elif 'ip nat-list' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_5 = self.kolvo_zapuskov_vkladka_5 + 1
                self.vstavka_v_gui('Списки доступа', self.vk5, self.okno_vk5, self.kolvo_zapuskov_vkladka_5)

            elif 'ip flow-export' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_5 = self.kolvo_zapuskov_vkladka_5 + 1
                self.vstavka_v_gui('Списки доступа', self.vk5, self.okno_vk5, self.kolvo_zapuskov_vkladka_5)

            # вкладка 3 (ip route). нужно делать так чтобы  поиск по IP и ip route не глючили
            elif 'ip route' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_3 = self.kolvo_zapuskov_vkladka_3 + 1
                self.vstavka_v_gui('Маршруты', self.vk3, self.okno_vk3, self.kolvo_zapuskov_vkladka_3)

            elif '1 ip' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_3 = self.kolvo_zapuskov_vkladka_3 + 1
                self.vstavka_v_gui('Маршруты', self.vk3, self.okno_vk3, self.kolvo_zapuskov_vkladka_3)

            #  вкладка 1
            elif 'controller' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_1 = self.kolvo_zapuskov_vkladka_1 + 1
                self.vstavka_v_gui('ip class-map', self.vk1, self.okno_vk1, self.kolvo_zapuskov_vkladka_1)

            # вкладка 6
            elif 'service iperf' in self.list_finish[0]:  # почему-то попадало в 1 вкладку. поэтому оно тут
                self.kolvo_zapuskov_vkladka_6 = self.kolvo_zapuskov_vkladka_6 + 1
                self.vstavka_v_gui('Службы', self.vk6, self.okno_vk6, self.kolvo_zapuskov_vkladka_6)

            elif 'ip' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_1 = self.kolvo_zapuskov_vkladka_1 + 1
                self.vstavka_v_gui('ip class-map', self.vk1, self.okno_vk1, self.kolvo_zapuskov_vkladka_1)

            #  вкладка 2
            elif 'interface' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_2 = self.kolvo_zapuskov_vkladka_2 + 1
                self.vstavka_v_gui('Интерфейсы', self.vk2, self.okno_vk2, self.kolvo_zapuskov_vkladka_2)

            # вкладка 3
            elif 'router igmp' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_3 = self.kolvo_zapuskov_vkladka_3 + 1
                self.vstavka_v_gui('Маршруты', self.vk3, self.okno_vk3, self.kolvo_zapuskov_vkladka_3)

            elif 'crypto' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_4 = self.kolvo_zapuskov_vkladka_4 + 1
                self.vstavka_v_gui('Туннели', self.vk4, self.okno_vk4, self.kolvo_zapuskov_vkladka_4)

            # вкладка 6
            elif 'service' in self.list_finish[0]:
                self.kolvo_zapuskov_vkladka_6 = self.kolvo_zapuskov_vkladka_6 + 1
                self.vstavka_v_gui('Службы', self.vk6, self.okno_vk6, self.kolvo_zapuskov_vkladka_6)

            else:
                self.func_error('Не описано в коде: ' + self.list_finish[0], 'Не описано в коде')

        except IndexError:
            pass

    def vstavka_v_gui(self, name_vkladki, number_vkladki, okno_vk, kolvo_zapuskov_vkladka):
        self.gui_vk(okno_vk, len(self.list_finish[:-1]))  # вставляет количество строк в ветку. Сделан срез чтобы
        # удалял лишнюю строчку так как первая строчка удаляется методом pop чуть ниже.
        okno_vk.headerItem().setText(0, self.translate("MainWindow", "---------------------------------------------"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(number_vkladki),
                                  self.translate("MainWindow", name_vkladki))  # задаем имя вкладки
        okno_vk.topLevelItem(kolvo_zapuskov_vkladka - 1).setText(0, self.translate("MainWindow", self.list_finish[
            0]))  # задаем имя ветки
        self.list_finish.pop(0)  # удаляется первый индекс чтобы название ветки не попадало в саму ветку
        for i in range(0,
                       len(self.list_finish)):  # цикл выполняется по количеству индексов в list_finish
            # (т.е. сколько передали данных, столько и выполнил раз)
            okno_vk.topLevelItem(kolvo_zapuskov_vkladka - 1).child(i).setText(0, self.translate("MainWindow", ''.join(
                self.list_finish[i])))  # вставляем данные в нужную ветку
        self.list_finish.clear()
        self.func()

    def gui_vk(self, okno_vk, number):
        item_0 = QtWidgets.QTreeWidgetItem(okno_vk)
        for i in range(0, number):
            item_1 = QtWidgets.QTreeWidgetItem(item_0)

    def setupUi(self, MainWindow):
        self.proverka_uz()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(730, 650)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 3, 331, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 70, width, height + 35))  # Размеры виджета где выводится информация
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tabWidget.setObjectName("tabWidget")
        self.vk1 = QtWidgets.QWidget()
        self.vk1.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.vk1.setObjectName("vk1")
        self.okno_vk1 = QtWidgets.QTreeWidget(self.vk1)
        # self.okno_vk1.setGeometry(QtCore.QRect(0, 0, 1900, 900))  # как было раньше
        self.okno_vk1.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk1.setObjectName("okno_vk1")
        self.tabWidget.addTab(self.vk1, "")

        self.vk2 = QtWidgets.QWidget()
        self.vk2.setObjectName("vk2")
        self.okno_vk2 = QtWidgets.QTreeWidget(self.vk2)
        self.okno_vk2.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk2.setObjectName("okno_vk2")
        self.tabWidget.addTab(self.vk2, "")

        self.vk3 = QtWidgets.QWidget()
        self.vk3.setObjectName("vk3")
        self.okno_vk3 = QtWidgets.QTreeWidget(self.vk3)
        self.okno_vk3.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk3.setObjectName("okno_vk3")
        self.tabWidget.addTab(self.vk3, "")

        self.vk4 = QtWidgets.QWidget()
        self.vk4.setObjectName("vk4")
        self.okno_vk4 = QtWidgets.QTreeWidget(self.vk4)
        self.okno_vk4.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk4.setObjectName("okno_vk4")
        self.tabWidget.addTab(self.vk4, "")

        ''' vk5 '''
        self.vk5 = QtWidgets.QWidget()
        self.vk5.setObjectName("vk5")
        self.okno_vk5 = QtWidgets.QTreeWidget(self.vk5)
        self.okno_vk5.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk5.setObjectName("okno_vk5")
        self.tabWidget.addTab(self.vk5, "")

        ''' vk6 '''
        self.vk6 = QtWidgets.QWidget()
        self.vk6.setObjectName("vk6")
        self.okno_vk6 = QtWidgets.QTreeWidget(self.vk6)
        self.okno_vk6.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk6.setObjectName("okno_vk6")
        self.tabWidget.addTab(self.vk6, "")

        ''' vk7 '''
        self.vk7 = QtWidgets.QWidget()
        self.vk7.setObjectName("vk7")
        self.okno_vk7 = QtWidgets.QTreeWidget(self.vk7)
        self.okno_vk7.setGeometry(QtCore.QRect(0, 0, width, height))
        self.okno_vk7.setObjectName("okno_vk7")
        # ------
        ''' окно ввода '''
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(10, 33, 301, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.lineEdit.setPlaceholderText('Введите IP адрес диониса для получения конфига...')
        ''' кнопка '''
        self.pushButton.setGeometry(QtCore.QRect(320, 33, 141, 31))
        self.pushButton.setObjectName("pushButton")
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        self.pushButton.setFont(font)
        MainWindow.setCentralWidget(self.centralwidget)
        ''' ----- '''
        #  статусбар
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar_oprogramme = QtWidgets.QMenuBar(MainWindow)
        self.menubar_oprogramme.setGeometry(QtCore.QRect(0, 0, 520, 21))
        self.menubar_oprogramme.setObjectName("menubar_oprogramme")
        self.oprogramme = QtWidgets.QMenu(self.menubar_oprogramme)
        self.oprogramme.setObjectName("oprogramme")
        MainWindow.setMenuBar(self.menubar_oprogramme)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar_oprogramme.addAction(self.oprogramme.menuAction())
        self.spravka = QtWidgets.QAction(MainWindow)
        self.spravka.setFont(font)
        self.spravka.setMenuRole(QtWidgets.QAction.TextHeuristicRole)
        self.spravka.setObjectName("spravka")

        self.spravka2 = QtWidgets.QAction(MainWindow)
        self.spravka2.setFont(font)
        self.spravka2.setMenuRole(QtWidgets.QAction.TextHeuristicRole)
        self.spravka2.setObjectName("spravka")

        self.oprogramme.addAction(self.spravka)
        self.oprogramme.addAction(self.spravka2)
        self.menubar_oprogramme.addAction(self.oprogramme.menuAction())
        # -----------Справка о программе----------
        self.spravka.triggered.connect(lambda: self.dio.get_config_txt(self.lineEdit.text()))
        self.spravka2.triggered.connect(lambda: self.dio.get_log_autorization(self.lineEdit.text()))

        #  Менюшка
        self.Menu_SOUN = QtWidgets.QComboBox(self.centralwidget)
        self.Menu_SOUN.setGeometry(QtCore.QRect(470, 33, 250, 31))  # x,y, ширина кнопки, высота кнопки
        self.Menu_SOUN.setMaxVisibleItems(33)
        self.Menu_SOUN.setFont(font)
        self.Menu_SOUN.setObjectName("Menu_SOUN")

        #  Пункты менюшки
        self.list_menu = ["Выберите дионис", "6600 Пушкина (66000)", "6600 Пушкина У.Ц. (66000)",
                     "6600 Пушкина интернет шлюз (66000)", "6600 Кузнечная (66001)", "6600 Уральская (66064)",
                     "6608 ц.о. крупняк (66004)", "6612 ц.о. Каменск (66007)", "6617 ц.о. Краснотурьинск (66008)",
                     "6617 ТОРМ Североуральск (66010)", "6617 ТОРМ Ивдель (66011)", "6619 ц.о. Красноуфимск (66012)",
                     "6619 ТОРМ Нижние Серги (66014)", "6623 ц.о. Нижний Тагил (66018)",
                     "6623 ТОРМ Верхняя Салда (66002)",
                     "6633 ц.о. Сухой Лог (66019)", "6633 ТОРМ Камышлов (66020)", "6633 ТОРМ Талица (66022)",
                     "6633 ТОРМ Богданович (66024)", "6633 ТОРМ Тугулым (66023)", "6658 ц.о. Екатеринбург (66025)",
                     "6670 ц.о. Екатеринбург (66026)", "6671 ц.о. Екатеринбург (66027)", "6676 ц.о. Ирбит (66028)",
                     "6676 ТОРМ Тавда (66029)", "6676 ТОРМ Туринск (66031)", "6677 ц.о. Артемовский (66033)",
                     "6677 ТОРМ Алапаевск (66034)", "6677 ТОРМ Реж (66035)", "6678 ц.о. Екатеринбург(66036)",
                     "6678 ТОРМ Березовский (66037)", "6679 ц.о. Екатеринбург (66038)", "6679 ТОРМ Полевской (66039)",
                     "6680 ц.о. Серов (66040)", "6681 ц.о. Качканар (66045)", "6681 ТОРМ Кушва (66047)",
                     "6681 ТОРМ Лесной (66046)", "6681 ТОРМ Нижняя Тура (66049)", "6682 ц.о. Невьянск (66050)",
                     "6682 ТОРМ Новоуральск (66051)", "6683 ц.о. Асбест (66053)", "6683 ТОРМ Заречный (66055)",
                     "6683 ТОРМ Белоярский (66054)", "6684 ц.о. Первоуральск (66056)", "6684 ТОРМ Ревда (66057)",
                     "6685 ц.о. Екатеринбург (66059)", "6685 ТОРМ Сысерть (66060)",
                     "6686 ц.о. Екатеринбург (66062)", "6686 ТОРМ Верхняя Пышма (66063)", "9955 Октябрьская (99550)",
                     "9955 Жукова (99551)", 'Филиал ФКУ (66901)']

        for i in range(0, 52):
            self.Menu_SOUN.addItem("")
        self.Menu_SOUN.currentIndexChanged.connect(self.chng)  # менюшка смотрит что нажали и запускает метод
        # -------------
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.tabWidget.setCurrentIndex(1)  # задаем вторую вкладку активной при запуске

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.translate = _translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dionis"))
        self.label.setText(_translate("MainWindow", "Дионис: "))
        self.tabWidget.setWhatsThis(_translate("MainWindow",
                                               "<html><head/><body><p><span style=\" font-size:20pt;\">bhjjbjnjn</span></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Получить конфиг"))
        self.pushButton.clicked.connect(lambda: self.push_button())
        #  статусбар
        self.oprogramme.setTitle(_translate("MainWindow", "Файл"))
        self.spravka.setText(_translate("MainWindow", "Сохранить конфиг"))
        self.spravka2.setText(_translate("MainWindow", "Сохранить журнал"))

        #  --- этот блок относится к менюшке
        for number_menu in range(0, len(self.list_menu)):
            self.Menu_SOUN.setItemText(number_menu, _translate("MainWindow", self.list_menu[number_menu]))
        #  ---------

        ''' Иконка '''
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setWindowIcon(QtGui.QIcon('config_python_icon.ico'))  # ДЛЯ РАБОТЫ исправить путь до иконки
        ''' ------ '''
        self.centralwidget.keyPressEvent = self.keyPressEvent  # Отслеживание нажатия клавиши Enter

    def chng(self):
        spisok = {'6600 Пушкина (66000)': '10.66.0.5',
                  "6600 Пушкина У.Ц. (66000)": '10.166.206.1',
                  "6600 Пушкина интернет шлюз (66000)": '10.66.0.26',
                  "6600 Кузнечная (66001)": '10.66.1.2',
                  "6600 Уральская (66064)": '10.66.61.2',
                  "6608 ц.о. крупняк (66004)": '10.66.9.2',
                  "6612 ц.о. Каменск (66007)": '10.66.13.2',
                  "6617 ц.о. Краснотурьинск (66008)": '10.66.18.2',
                  "6617 ТОРМ Североуральск (66010)": '10.66.34.2',
                  "6617 ТОРМ Ивдель (66011)": '10.66.35.2',
                  "6619 ц.о. Красноуфимск (66012)": '10.66.21.2',
                  "6619 ТОРМ Нижние Серги (66014)": '10.66.43.2',
                  "6623 ц.о. Нижний Тагил (66018)": '10.66.26.2',
                  "6623 ТОРМ Верхняя Салда (66002)": '10.66.7.2',
                  "6633 ц.о. Сухой Лог (66019)": '10.66.37.2',
                  "6633 ТОРМ Камышлов (66020)": '10.66.14.2',
                  "6633 ТОРМ Талица (66022)": '10.66.51.2',
                  "6633 ТОРМ Богданович (66024)": '10.66.38.2',
                  "6633 ТОРМ Тугулым (66023)": '10.66.50.2',
                  "6658 ц.о. Екатеринбург (66025)": '10.66.54.2',
                  "6670 ц.о. Екатеринбург (66026)": '10.66.56.2',
                  "6671 ц.о. Екатеринбург (66027)": '10.66.57.2',
                  "6676 ц.о. Ирбит (66028)": '10.66.11.2',
                  "6676 ТОРМ Тавда (66029)": '10.66.39.2',
                  "6676 ТОРМ Туринск (66031)": '10.66.52.2',
                  "6677 ц.о. Артемовский (66033)": '10.66.3.2',
                  "6677 ТОРМ Алапаевск (66034)": '10.66.2.2',
                  "6677 ТОРМ Реж (66035)": '10.66.31.2',
                  "6678 ц.о. Екатеринбург(66036)": '10.66.55.2',
                  "6678 ТОРМ Березовский (66037)": '10.66.5.2',
                  "6679 ц.о. Екатеринбург (66038)": '10.66.60.2',
                  "6679 ТОРМ Полевской (66039)": '10.66.29.2',
                  "6680 ц.о. Серов (66040)": '10.66.69.2',
                  "6681 ц.о. Качканар (66045)": '10.66.17.2',
                  "6681 ТОРМ Кушва (66047)": '10.66.22.2',
                  "6681 ТОРМ Лесной (66046)": '10.66.33.2',
                  "6681 ТОРМ Нижняя Тура (66049)": '10.66.16.2',
                  "6682 ц.о. Невьянск (66050)": '10.66.25.2',
                  "6682 ТОРМ Новоуральск (66051)": '10.66.32.2',
                  "6683 ц.о. Асбест (66053)": '10.66.4.2',
                  "6683 ТОРМ Заречный (66055)": '10.66.41.2',
                  "6683 ТОРМ Белоярский (66054)": '10.66.42.2',
                  "6684 ц.о. Первоуральск (66056)": '10.66.27.2',
                  "6684 ТОРМ Ревда (66057)": '10.66.30.2',
                  "6685 ц.о. Екатеринбург (66059)": '10.66.58.2',
                  "6685 ТОРМ Сысерть (66060)": '10.66.48.2',
                  "6686 ц.о. Екатеринбург (66062)": '10.66.59.2',
                  "6686 ТОРМ Верхняя Пышма (66063)": '10.66.6.2',
                  "9955 Октябрьская (99550)": '10.81.5.6',
                  "9955 Жукова (99551)": '10.81.15.5',
                  "Филиал ФКУ (66901)": '10.66.200.2'}
        SOUN_menu = self.Menu_SOUN.currentText()

        if SOUN_menu in spisok:
            for i in spisok[SOUN_menu]:
                self.lineEdit.setText(spisok[SOUN_menu])
            self.push_button()

    def start(self):
        # очистка вкладок для повторного запроса конфигурации
        self.okno_vk1.clear()
        self.okno_vk2.clear()
        self.okno_vk3.clear()
        self.okno_vk4.clear()
        self.okno_vk5.clear()
        self.okno_vk6.clear()
        self.okno_vk7.clear()
        try:
            if "!" in self.dio.data[9]:  # это сделано для Dionis NX 2.0
                MainWindow.setWindowTitle(
                    self.translate("MainWindow", self.dio.data[10][9:]))  # задаем имя диониса в шапке программы.
                self.label.setText(
                    self.translate("MainWindow", "Дионис: " + self.dio.data[10][9:]))  # задаем имя диониса в окне проги
                #  это сделано чтобы строчка появлялась в 4 вкладке + первый туннель отображался нормально на 2.0
                try:
                    index_mode_sync = self.dio.data.index('crypto disec mode sync')
                    self.dio.data.insert(index_mode_sync + 1, '!')
                except ValueError:
                    pass

                if '!' in self.dio.data[11]:  # это сделано для дионисов где DNS нет совсем
                    # это нужно чтобы ext_in не попадал в ip access-group no-invalid forward:
                    self.dio.data.insert(20, '!')
                    self.dio.data.insert(22, '!')
                else:
                    self.dio.data.insert(23, '!')  # это нужно чтобы ext_in не попадал в ip access-group no-invalid
                    # это сделано для того, чтобы при трех DNS серверах конфиг отображался в проге:
                    if '3 ip resolver nameserver' in self.dio.data[13]:
                        self.dio.data.insert(25, '!')
                    else:
                        self.dio.data.insert(22, '!')  # тоже самое
                    self.dio.data.insert(11, '!')  # добавляем знак ! чтобы отображались DNS

            # это для дионисов NX 1.2
            else:
                if "\x1b[H\x1b[3;J\x1bc" in self.dio.data:  # это сделано, чтобы в кластере не отображались эти символы
                    self.dio.data.remove("\x1b[H\x1b[3;J\x1bc")

                self.dio.data.append('!')  # знак восклицания нужно добавлять только на NX 1.2
                self.label.setText(
                    self.translate("MainWindow", "Дионис: " + self.dio.data[9][9:]))  # задаем имя диониса в окне проги
                MainWindow.setWindowTitle(
                    self.translate("MainWindow", self.dio.data[9][9:]))  # задаем имя диониса в шапке программы.

            self.indexs_all = ([index for index, value in enumerate(self.dio.data) if
                                value == '!'])  # узнаем индексы всех знаков восклицания
            self.kolvo_zapuskov = 0
            self.list_index_all = []
            self.list_finish = []
            self.kolvo_zapuskov_vkladka_1 = 0
            self.kolvo_zapuskov_vkladka_2 = 0
            self.kolvo_zapuskov_vkladka_3 = 0
            self.kolvo_zapuskov_vkladka_4 = 0
            self.kolvo_zapuskov_vkladka_5 = 0
            self.kolvo_zapuskov_vkladka_6 = 0
            self.kolvo_zapuskov_vkladka_7 = 0
            self.func()
        except FileNotFoundError:
            self.func_error('Блокнота с таким IP адресом нет в папке', 'Ошибка имени файла')
            pass

    def push_button(self):
        if len(self.lineEdit.text()) < 8:  # небольшая проверка на IP адрес
            self.func_error('Неверный IP адрес', 'Ошибка IP адреса')
            pass
        else:
            try:
                self.dio = Dio_connect()
                self.dio.get_config(self.lineEdit.text())  # сохранение конфига в txt
                self.start()
            except TimeoutError:
                self.func_error(f'Отсутствует сетевая доступность диониса {self.lineEdit.text()}', 'Ошибка соединения')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:  # return основной enter
            self.push_button()
        elif event.key() == Qt.Key_Enter:  # enter - это на num pad
            self.push_button()

    def func_error(self, text_error, text_title):
        error = QMessageBox()
        error.setWindowTitle(text_title)
        error.setText(text_error)
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok)
        error.exec_()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
