#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gökmen Göksel <gokmen@pardus.org.tr>
# Correct way.

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QMimeData

from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QDrag
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout

FREE, EXT, MS, UK = range(4)
VERTICAL, HORIZONTAL = range(2)
SHARED = 'QLabel{border:1px solid #585858;border-radius:4px;}'
STYLES = {FREE:'background-color:rgba(0,0,0,80); border:2px solid #585858;',
          EXT:'background-color:#008080;',
          MS:'background-color:#008000;color:white;',
          UK:'background-color:pink;color:black;'}

DRAG_STYLE = 'background-color:rgba(0,0,0,0);color:rgba(0,0,0,0);border:1px dotted #555;'

class Partition(QLabel):
    def __init__(self, parent, title = 'Free Space', fs_type = FREE, size = 0):
        QLabel.__init__(self, parent)
        self.parent = parent
        self._fs_type = fs_type
        self.setStyleSheet(STYLES[fs_type])
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred))
        self.setText(title)
        self._setSize(size)

        self.editButton = QPushButton('Edit', self)
        self.deleteButton = QPushButton('Del', self)
        self.editButton.clicked.connect(self.editButtonClicked)
        self.deleteButton.clicked.connect(self.deleteButtonClicked)

        QTimer.singleShot(0, self.leaveEvent)

    def _setSize(self, size):
        self._size = size
        self.setToolTip('Size: %s MB' % size)

    def editButtonClicked(self):
        print "Edit clicked on ", self.text()

    def deleteButtonClicked(self):
        self.parent.deletePartition(self)
        print "Delete clicked on ", self.text()

    def enterEvent(self, event):
        if not self._fs_type == FREE:
            self.editButton.move(self.width() - self.editButton.width(), self.height() / 2 - self.editButton.height() / 2)
            self.deleteButton.move(self.editButton.pos().x() - self.deleteButton.width(), self.height() / 2 - self.deleteButton.height() / 2)
            self.editButton.show()
            self.deleteButton.show()

    def leaveEvent(self, event=None):
        self.editButton.hide()
        self.deleteButton.hide()

class Block(QGroupBox):

    def __init__(self, parent, name, size, layout = HORIZONTAL):
        QGroupBox.__init__(self, '%s - %s MB' % (name, size), parent)

        if layout == HORIZONTAL:
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)

        self._name = name
        self._layout = layout
        self._size = size
        self._used_size = 0
        self._partitions = []
        self._accepted_blocks = []

    def addPartition(self, partition, index = None):

        if index == None:
            index = len(self._partitions)

        self._partitions.insert(index, partition)

        if partition._fs_type == FREE and not partition._size:
            size = self._size - self._used_size
            partition._setSize(size)

        self._used_size += partition._size

        self.layout.insertWidget(index, partition)
        self._updateSize()

    def setBlockAsFree(self):
        freePartition = Partition(self, 'free', FREE, self._size)
        self.addPartition(freePartition, 0)

    def deleteAllPartitions(self):
        self._used_size = 0
        for partition in self._partitions:
            partition.hide()
            self.layout.removeWidget(partition)
        self._partitions = []

    def deletePartition(self, partition, fillFree = False):
        if fillFree:
            pin = self._partitions.index(partition)
            newFreePartition = Partition(self, 'free', FREE, partition._size)
            self.addPartition(newFreePartition, pin)

        self._partitions.remove(partition)
        self.layout.removeWidget(partition)
        self._used_size -= partition._size
        partition.hide()
        del partition

        if all(partition._fs_type == FREE for partition in self._partitions):
            self.deleteAllPartitions()
            self.setBlockAsFree()

        for i in range(len(self._partitions) - 1):
            if self._partitions[i]._fs_type == FREE and self._partitions[i+1]._fs_type == FREE:
                newFreePartition = Partition(self, 'free', FREE, self._partitions[i]._size + self._partitions[i+1]._size)
                self.deletePartition(self._partitions[i])
                self.deletePartition(self._partitions[i])
                self.addPartition(newFreePartition, i)
                break

        self._updateSize()

    def updatePartition(self, oP, sP):
        oldIndex = self._partitions.index(oP)
        newPartition = Partition(self, sP.text(), sP._fs_type, sP._size)
        newFreePartition = Partition(self, 'free', FREE, oP._size - sP._size)
        self.addPartition(newPartition, oldIndex)
        self.addPartition(newFreePartition, oldIndex + 1)
        self.deletePartition(oP)

    def _updateSize(self):
        for i in range(len(self._partitions)):
            self.layout.setStretch(i, self._partitions[i]._size)

class Test(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setStyleSheet(SHARED)
        self.layout = QVBoxLayout(self)

        disk1 = Block(self, 'Western Digital ATA', 2220)#, layout = VERTICAL)
        disk1.addPartition(Partition(disk1, 'sda1', EXT, 800))
        disk1.addPartition(Partition(disk1, 'sda2', MS, 400))
        disk1.addPartition(Partition(disk1, 'sda3', UK, 620))
        disk1.addPartition(Partition(disk1, 'free', FREE))
        self.layout.addWidget(disk1)

        disk2 = Block(self, 'Seagate Falan Filan', 5330)#, layout = VERTICAL)
        disk2.addPartition(Partition(disk2, 'sdb1', UK, 120))
        disk2.addPartition(Partition(disk2, 'sdb2', EXT, 530))
        disk2.addPartition(Partition(disk2, 'sdb3', EXT, 2830))
        disk2.addPartition(Partition(disk2, 'free', FREE))
        self.layout.addWidget(disk2)

        disk3 = Block(self, 'Super USB Disk', 4330)#, layout = VERTICAL)
        disk3.addPartition(Partition(disk3, 'free', FREE, 2220))
        disk3.addPartition(Partition(disk3, 'sdc1', EXT, 1000))
        disk3.addPartition(Partition(disk3, 'sdc2', MS, 620))
        disk3.addPartition(Partition(disk3, 'free', FREE))
        self.layout.addWidget(disk3)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = Test()
    ui.resize(630, 300)
    ui.show()
    sys.exit(app.exec_())

