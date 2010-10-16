#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gökmen Göksel <gokmen@pardus.org.tr>
# Correct way.

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout

FREE, EXT, MS, UK = range(4)
VERTICAL, HORIZONTAL = range(2)
STYLES = {FREE:'background-color:rgba(0,0,0,0); border:1px dotted red;',
          EXT:'background-color:blue;',
          MS:'background-color:darkgreen',
          UK:'background-color:pink; color:black;'}

class Partition(QLabel):
    def __init__(self, parent, title = 'Free Space', fs_type = FREE, size = 0):
        QLabel.__init__(self, parent)
        self._fs_type = fs_type
        self._setSize(size)
        self.setStyleSheet(STYLES[fs_type])
        self.setAlignment(Qt.AlignCenter)
        self.setText(title)
        self.dragPosition = None

    def _setSize(self, size):
        self._size = size
        self.sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.sizePolicy.setHorizontalStretch(self._size)
        self.sizePolicy.setVerticalStretch(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

class Block(QFrame):

    def __init__(self, parent, size, layout = HORIZONTAL):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        if layout == HORIZONTAL:
            self.layout = QHBoxLayout(self)
        else:
            self.layout = QVBoxLayout(self)

        self._layout = layout
        self._size = size
        self._used_size = 0
        self._parttions = []

    def addPartition(self, partition):
        self._parttions.append(partition)

        if partition._fs_type == FREE:
            size = self._size - self._used_size
            partition._setSize(size)
        self._used_size += partition._size

        self.layout.addWidget(partition)
        self._updateSize()

    def deletePartition(self, partition):
        self._parttions.remove(partition)
        self.layout.removeWidget(partition)

    def _updateSize(self):
        for i in range(len(self._parttions)):
            self.layout.setStretch(i, self._parttions[i]._size)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            epos = event.pos()
            for partition in self._parttions:
                if partition.rect().contains(QPoint(epos.x(), epos.y())):
                    partition.mousePressEvent(event)

class Test(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)

        disk1 = Block(self, 220)
        disk1.addPartition(Partition(disk1, 'sda1', EXT, 100))
        disk1.addPartition(Partition(disk1, 'sda2', MS, 30))
        disk1.addPartition(Partition(disk1, 'free', FREE))

        self.layout.addWidget(disk1)

        disk2 = Block(self, 330)
        disk2.addPartition(Partition(disk2, 'sdb1', UK, 20))
        disk2.addPartition(Partition(disk2, 'sdb2', EXT, 130))
        disk2.addPartition(Partition(disk2, 'sdb3', EXT, 30))
        disk2.addPartition(Partition(disk2, 'sdb4', MS, 130))
        disk2.addPartition(Partition(disk2, 'free', FREE))

        self.layout.addWidget(disk2)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = Test()
    ui.show()
    sys.exit(app.exec_())

