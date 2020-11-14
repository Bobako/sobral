import sys
import os
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication, QMessageBox, QListWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QLineEdit, QLabel, QTreeView, QTreeWidgetItem, QTreeWidget, 
                            QAbstractItemView, QCheckBox, QTabWidget)
from PyQt5.QtGui import QFont, QIcon, QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import QCoreApplication, QDir, Qt, QDataStream

import db

class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Конфигурация показа'
        self.top = 200
        self.left = 500
        self.width = 800
        self.height = 600
        self.listOfChilds = list()
        self.dictOfSignals = dict() # словарь с сигналами в которых мы потом производим поиск
        self.resultOfSearchList = list()
        self.numberOfSignals = 0 # считаем количество сигналов когда их выбираем после поиска

        self.initUI()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Сообщение', "Вы точно хотите выйти?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def showSystemsTree(self, event):
        if (self.treeSystems.isHidden()):
            self.treeSystems.show()
            self.labelSelected.show()

            self.searchResultTree.hide()
            self.searchLine.hide()
            self.nuberOfSelectedLabel.hide()
            self.buttonSearch.hide()
            self.embeddedSignalsCheckBox.hide()
            self.discreteSignalsCheckBox.hide()
            self.ProjectProtocolsTree.hide()
            self.countingLabel.hide()
            self.savedProtocolsTree.hide()

    def showSearchTree(self, event):
        if (self.searchResultTree.isHidden()):
            self.searchResultTree.show()
            self.searchLine.show()
            self.nuberOfSelectedLabel.show()
            self.buttonSearch.show()
            self.embeddedSignalsCheckBox.show()
            self.discreteSignalsCheckBox.show()

            self.treeSystems.hide()
            self.labelSelected.hide()
            self.ProjectProtocolsTree.hide()
            self.countingLabel.hide()
            self.savedProtocolsTree.hide()

    def showProjectProtocolsTree(self, event):
        if (self.ProjectProtocolsTree.isHidden()):
            self.ProjectProtocolsTree.show()
            self.countingLabel.show()

            self.treeSystems.hide()
            self.labelSelected.hide()
            self.searchResultTree.hide()
            self.searchLine.hide()
            self.nuberOfSelectedLabel.hide()
            self.buttonSearch.hide()
            self.embeddedSignalsCheckBox.hide()
            self.discreteSignalsCheckBox.hide()
            self.savedProtocolsTree.hide()

    def showSavedProtocolsTree(self,event):
        if (self.savedProtocolsTree.isHidden()):
            self.savedProtocolsTree.show()

            self.ProjectProtocolsTree.hide()
            self.countingLabel.hide()
            self.treeSystems.hide()
            self.labelSelected.hide()
            self.searchResultTree.hide()
            self.searchLine.hide()
            self.nuberOfSelectedLabel.hide()
            self.buttonSearch.hide()
            self.embeddedSignalsCheckBox.hide()
            self.discreteSignalsCheckBox.hide()

    def searchSignals(self):
        # ищем в slef.dictOfSignals
        string = self.searchLine.text()
        self.resultOfSearchList = []
        self.searchResultTree.clear()
        if (type(string) == str):
            if self.embeddedSignalsCheckBox.checkState() == 2: # 2 означает что на чекбокс тыкнули, 0 - нет
                for key in self.dictOfSignals.keys():
                    if string in key:
                        row = QTreeWidgetItem(self.searchResultTree, [key])
                        self.searchResultTree.addTopLevelItem(row)
                        for record in self.dictOfSignals[key]:
                            child = QTreeWidgetItem(row, [record])
                            row.addChild(child)
                            self.resultOfSearchList.append(record)   
            if self.discreteSignalsCheckBox.checkState() == 2:
                for key in self.dictOfSignals.keys():
                    for record in self.dictOfSignals[key]:
                        if string in record:
                            self.resultOfSearchList.append(record)
                            row = QTreeWidgetItem(self.searchResultTree, [record])
                            self.searchResultTree.addTopLevelItem(row)
            if (len(self.resultOfSearchList) == 0):
                self.nuberOfSelectedLabel.setText('Не найдено')
            else:
                self.nuberOfSelectedLabel.setText('{0} выбрано из {1}'.format(len(self.resultOfSearchList), self.numberOfSignals))

    def moveSelectedSignals(self):
        if self.treeSystems.isHidden():
            currentTree = self.searchResultTree
        else:
            currentTree = self.treeSystems
        for sel in currentTree.selectedIndexes():
            item = currentTree.itemFromIndex(sel) # убираем выделение
            item.setSelected(False)

            if (not sel.child(0,0).isValid()): # если нет дочерних элементов
                if (sel.data() not in self.listOfChilds): # если элемент уже добавлен
                    self.listOfChilds.append(sel.data())
                    self.listSelectedSignals.addItem(sel.data())
            else:
                index = 0
                while sel.child(index,0).isValid(): # проходимся по всем дочерним
                    item = currentTree.itemFromIndex(sel.child(index,0)) # убираем выделение
                    item.setSelected(False)
                    selChild = sel.child(index,0).data()
                    if (selChild not in self.listOfChilds): # если элемент уже добавлен
                        self.listOfChilds.append(selChild)
                        self.listSelectedSignals.addItem(selChild)
                    index += 1
        self.labelHowMuchSelected.setText('Выбрано {0} из {1}'.format(len(self.listOfChilds), self.numberOfSignals))

    def moveAllSelectedSignals(self):
        if self.treeSystems.isHidden():
            currentTree = self.searchResultTree
        else: 
            currentTree = self.treeSystems
        for index in range(currentTree.topLevelItemCount()):
            item = currentTree.topLevelItem(index)
            for childIndex in range(item.childCount()):
                childData = item.child(childIndex).data(0,0) # 0,0 потому что элемент у нас туту всего один и дочерних не имеет
                if (childData not in self.listOfChilds):
                    self.listOfChilds.append(childData) 
                    self.listSelectedSignals.addItem(childData)
        self.labelHowMuchSelected.setText('Выбрано {0} из {1}'.format(len(self.listOfChilds), self.numberOfSignals))

    def deleteSelectedSignals(self):
        for item in self.listSelectedSignals.selectedItems():
            deletedItem = self.listSelectedSignals.takeItem(self.listSelectedSignals.row(item))
            self.listOfChilds.remove(deletedItem.data(0))
        self.labelHowMuchSelected.setText('Выбрано {0} из {1}'.format(len(self.listOfChilds), self.numberOfSignals))

    def deleteAllSelectedSignals(self):
        self.listSelectedSignals.clear()
        self.listOfChilds = []
        self.labelHowMuchSelected.setText('Выбрано 0 из {}'.format(self.numberOfSignals))

    def fixSelection(self, modelSelectionOfSelectedItem):
        if self.treeSystems.isHidden():
            currentTree = self.searchResultTree
        else:
            currentTree = self.treeSystems
            model = modelSelectionOfSelectedItem
        if len(modelSelectionOfSelectedItem.indexes()) > 0:
            modelIndexOfSelectedItem = modelSelectionOfSelectedItem.indexes()[0]
            item = currentTree.itemFromIndex(modelIndexOfSelectedItem)
            if (item.isSelected()):
                if (modelIndexOfSelectedItem.child(0,0).isValid()):
                    childs = item.childCount()
                    for index in range(childs):
                        childItem = currentTree.itemFromIndex(modelIndexOfSelectedItem.child(index, 0))
                        childItem.setSelected(True) 
        else:
            for sel in currentTree.selectedIndexes():
                item = currentTree.itemFromIndex(sel)
                flag = False
                if (item.isSelected() and item.childCount() > 0):
                    for index in range(item.childCount()):
                        childItem = currentTree.itemFromIndex(sel.child(index, 0))
                        if not childItem.isSelected():
                            flag = True
                if flag:
                    item.setSelected(False)

    def countGroupsAndSignals(self, value):
        self.fixSelection(value)
        group = 0
        childs = 0
        for sel in self.treeSystems.selectedIndexes():
            if (not sel.child(0,0).isValid()): # нет дочерних элементов
                childs += 1
            else:
                group += 1
        self.labelSelected.setText('Выбрано: {0} групп, {1} сигналов'.format(group, childs))

    def initUI(self):
        # selectedTreeElemStyleSheet = '''.QStandardItem {background-color: blue}'''
        centralButtonsSS = 'max-width: 20%; padding: 6px; margin: 10px; border-radius: 5px; border: 1px solid black'
        self.setStyleSheet(open(os.path.join(os.path.dirname(__file__), 'style.css')).read())

        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        vboxList = QVBoxLayout()
        self.labelSignalSelection = QLabel('Выбор сигнала')
        self.labelSystems = QLabel('Системы')
        self.labelSystems.mousePressEvent = self.showSystemsTree

        '-------------------------ListWidget---------------------------'
        self.treeSystems = QTreeWidget()
        self.treeSystems.setAlternatingRowColors(1)
        self.treeSystems.setHeaderHidden(1)
        self.treeSystems.setColumnCount(1)
        self.treeSystems.setSelectionMode(QAbstractItemView.MultiSelection)
        self.treeSystems.selectionModel().selectionChanged.connect(self.countGroupsAndSignals) # это для подсчёта выбранных групп и сигналов

        kks = db.MPK.select_column('Суффикс', False, False, False) #проеверь чтобы postgres был запущен
        kks = set(kks)
        for record in kks:
            row = QTreeWidgetItem(self.treeSystems, [record])
            self.treeSystems.addTopLevelItem(row)
            self.dictOfSignals[record] = list()
            suffics = set(db.MPK.select_column('KKS', 'Суффикс', record, False))
            for elem in suffics:
                self.dictOfSignals[record].append(elem)
                child = QTreeWidgetItem(row, [elem])
                row.addChild(child)   
                self.numberOfSignals += 1
        '----------------------------ListWidget--------------------------'

        self.labelSelected = QLabel('Выбрано: 0 групп, 0 сигналов')
        self.labelSearch = QLabel('Поиск')
        self.labelSearch.mousePressEvent = self.showSearchTree

        '--------------------------HiddenSearch--------------------------------'
        self.buttonSearch = QPushButton('Искать', self)
        self.buttonSearch.clicked.connect(self.searchSignals)
        self.buttonSearch.hide()

        self.searchLine = QLineEdit(self)
        self.searchLine.hide()

        hboxSearchLayout = QHBoxLayout()
        hboxSearchLayout.addWidget(self.buttonSearch)
        hboxSearchLayout.addWidget(self.searchLine)

        self.embeddedSignalsCheckBox = QCheckBox('Упакованные сигналы', self)
        self.embeddedSignalsCheckBox.hide()
        self.discreteSignalsCheckBox = QCheckBox('Дискретные сигналы', self)
        self.discreteSignalsCheckBox.hide()

        hboxSearchParametersLayout = QHBoxLayout()
        hboxSearchParametersLayout.addWidget(self.embeddedSignalsCheckBox)
        hboxSearchParametersLayout.addWidget(self.discreteSignalsCheckBox)

        self.searchResultTree = QTreeWidget()
        self.searchResultTree.setHeaderHidden(1)
        self.searchResultTree.setColumnCount(1)
        self.searchResultTree.hide()
        self.searchResultTree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.searchResultTree.selectionModel().selectionChanged.connect(self.fixSelection)

        self.nuberOfSelectedLabel = QLabel('0 выбрано из {}'.format(self.numberOfSignals))
        self.nuberOfSelectedLabel.hide()
        '--------------------------HiddenSearch--------------------------------'

        '--------------------------ProjectProtocols----------------------------'
        self.ProjectProtocolsTree = QTreeWidget()
        self.ProjectProtocolsTree.setHeaderHidden(1)
        self.ProjectProtocolsTree.setColumnCount(1)
        self.ProjectProtocolsTree.hide()

        self.countingLabel = QLabel('Выбрано 0 групп, 0 сигналов')
        self.countingLabel.hide()
        '--------------------------ProjectProtocols----------------------------'

        '---------------------------SavedProtocols------------------------'
        self.savedProtocolsTree = QTreeWidget()
        self.savedProtocolsTree.setHeaderHidden(1)
        self.savedProtocolsTree.setColumnCount(1)
        self.savedProtocolsTree.hide()
        '---------------------------SavedProtocols------------------------'

        self.labelProjectProtocolSignals = QLabel('Сигналы проектных протоколов')
        self.labelProjectProtocolSignals.mousePressEvent = self.showProjectProtocolsTree
        self.labelStoredProtocols = QLabel('Сохраненные протоколы')
        self.labelStoredProtocols.mousePressEvent = self.showSavedProtocolsTree
        widgets = (self.labelSignalSelection, 
                   self.labelSystems, 
                   self.treeSystems, 
                   self.labelSelected, 
                   self.labelSearch, 
                   self.searchResultTree, 
                   self.nuberOfSelectedLabel, 
                   self.labelProjectProtocolSignals,
                   self.ProjectProtocolsTree,
                   self.countingLabel, 
                   self.labelStoredProtocols,
                   self.savedProtocolsTree)
        for widget in widgets:
            vboxList.addWidget(widget)
            if widget == self.labelSearch:
                vboxList.addLayout(hboxSearchLayout)
                vboxList.addLayout(hboxSearchParametersLayout)

        vbox4Btn = QVBoxLayout()
        self.btnRigth = QPushButton('>', self)
        self.btnRigth.setStyleSheet(centralButtonsSS)
        self.btnRigth.clicked.connect(self.moveSelectedSignals)
        
        self.btnLeft = QPushButton('<', self)
        self.btnLeft.setStyleSheet(centralButtonsSS)
        self.btnLeft.clicked.connect(self.deleteSelectedSignals)

        self.btnRigthAll = QPushButton('>>', self)
        self.btnRigthAll.setStyleSheet(centralButtonsSS)
        self.btnRigthAll.clicked.connect(self.moveAllSelectedSignals)
        
        self.btnLeftAll = QPushButton('<<', self)
        self.btnLeftAll.setStyleSheet(centralButtonsSS)
        self.btnLeftAll.clicked.connect(self.deleteAllSelectedSignals)

        widgets = (self.btnRigth, 
                   self.btnLeft, 
                   self.btnRigthAll, 
                   self.btnLeftAll)
        for widget in widgets:
            vbox4Btn.addWidget(widget)

        vboxSelectedList = QVBoxLayout()
        self.labelSelectedSignals = QLabel('Выбранные сигналы')

        self.listSelectedSignals = QListWidget()
        self.listSelectedSignals.setSelectionMode(QAbstractItemView.MultiSelection)

        self.labelHowMuchSelected = QLabel('Выбрано 0 из {}'.format(self.numberOfSignals))
        widgets = (self.labelSelectedSignals, 
                   self.listSelectedSignals, 
                   self.labelHowMuchSelected)
        for widget in widgets:
            vboxSelectedList.addWidget(widget)
        
        hboxLists = QHBoxLayout()
        layouts = (vboxList, vbox4Btn, vboxSelectedList)
        for lay in layouts:
            hboxLists.addLayout(lay)

        hboxInputLine = QHBoxLayout()
        self.labelDescription = QLabel('Описание')
        self.inputLine = QLineEdit(self)
        widgets = (self.labelDescription, 
                   self.inputLine)
        for widget in widgets:
            hboxInputLine.addWidget(widget)

        hboxBottomButtons = QHBoxLayout()
        self.buttonOK = QPushButton('OK', self)
        self.buttonCancel = QPushButton('Отмена', self)
        hboxBottomButtons.addStretch(1)
        widgets = (self.buttonOK, 
                   self.buttonCancel)
        for widget in widgets:
            hboxBottomButtons.addWidget(widget)

        mainVBox = QVBoxLayout()
        layouts = (hboxLists, hboxInputLine, hboxBottomButtons)
        for lay in layouts:
            mainVBox.addLayout(lay)

        '-------------------------Tabs-------------------------'
        self.signalsTabWrapper = QWidget()
        self.signalsTabWrapper.setLayout(mainVBox)

        self.signalsTab = QTabWidget()
        self.signalsTab.addTab(self.signalsTabWrapper, 'Сигналы для показа')
        self.signalsTab.addTab(QWidget(), 'Настройка показа') # Вместо QWidget() вставить содержимое вкладки

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.signalsTab)
        '-------------------------Tabs-------------------------'

        self.setLayout(mainLayout)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())