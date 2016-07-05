import sys
import re
import psutil
from PyQt4 import QtGui, QtCore
from apscheduler.schedulers.qt import QtScheduler

class UpdateTableSignal(QtCore.QObject):
    updateTable = QtCore.pyqtSignal()

class ListTableView(QtGui.QTableView):
    def __init__(self):
        """docstring for __init__"""
        super(ListTableView, self).__init__()

class SearchBox(QtGui.QLineEdit):
    keyPressed = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        super(SearchBox, self).keyPressEvent(event)
        self.keyPressed.emit()

class PsKiller(QtGui.QWidget):
    def __init__(self):
        """docstring for __init__"""
        super(PsKiller, self).__init__()

        self.init_ui()

        self.updateTableSignal = UpdateTableSignal()
        self.updateTableSignal.updateTable.connect(lambda: self.refresh_list(self.search_edit.text()))
        self.scheduler = QtScheduler()
        self.scheduler.add_job(self.update_table_emitter, 'interval', seconds=2)
        self.scheduler.start()

    def init_ui(self):
        """docstring for init_ui"""
        self.pid_edit = QtGui.QLineEdit()
        kill_btn = QtGui.QPushButton("Kill Me", self)
        kill_btn.clicked.connect(self.kill_ps)

        self.header = ['PID', 'Process Name', 'Absolute Path', 'Command Line']
        self.table_view = ListTableView()
        self.table_view.setModel(PsInfoModel(self.get_ps_info(''), self.header, self))
        self.table_view.clicked.connect(self.cell_click)

        self.table_view.setMouseTracking(True)
        self.table_view.entered.connect(self.show_cell_content)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setColumnWidth(2, 300)
        self.table_view.setColumnWidth(3, 300)

        self.search_edit = SearchBox()
        self.search_edit.keyPressed.connect(self.search_by_keyword)

        self.status_bar = QtGui.QStatusBar()
        self.status_bar.showMessage("ready")

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.pid_edit, 1, 0)
        grid.addWidget(kill_btn, 1, 1)
        grid.addWidget(self.search_edit, 2, 0)
        grid.addWidget(self.table_view, 3, 0, 5, 2)
        grid.addWidget(self.status_bar, 9, 0)

        self.setLayout(grid)

        self.setWindowTitle("PS Killer")
        self.setGeometry(300, 300, 300, 150)
        self.resize(800, 400)

        self.show()

    def update_table_emitter(self):
        self.updateTableSignal.updateTable.emit()

    def refresh_list(self, keyword=''):
        self.table_view.setModel(PsInfoModel(self.get_ps_info(keyword), self.header, self))

    def get_ps_info(self, keyword):
        pinfo_arr = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'exe', 'cmdline'])
            except psutil.NoSuchProcess:
                pass
            else:
                if keyword == "":
                    pinfo_arr.append(pinfo)
                else:
                    if re.search(str(keyword).lower(), pinfo['name'].lower()) != None or re.search(str(keyword).lower(), str(pinfo['exe']).lower()) != None or (pinfo['cmdline'] != None and re.search(str(keyword).lower(), ' '.join(pinfo['cmdline']).lower()) != None):
                        pinfo_arr.append(pinfo)
        return pinfo_arr

    def search_by_keyword(self):
        """docstring for search_by_keyword"""
        keyword = self.search_edit.text()
        if keyword != "":
            self.refresh_list(keyword)
        else:
            self.refresh_list()
    def kill_ps(self):
        """docstring for kill_ps"""
        pid = self.pid_edit.text()
        try:
            pid = int(pid)
            process = psutil.Process(pid)
            for child in process.children(recursive=True):
                child.kill()
            process.kill()
            self.status_bar.showMessage("Process " + str(pid) + " is killed")
        except psutil.NoSuchProcess:
            self.status_bar.showMessage("Process " + str(pid) + " is not exist")
        except psutil.AccessDenied:
            self.status_bar.showMessage("Unable kill process " + str(pid) + ".Must be a root user.")
        except ValueError:
            self.status_bar.showMessage("Process " + str(pid) + " is an invalidated pid.")

    def closeEvent(self, event):
        self.scheduler.shutdown()

    def cell_click(self, item):
        cell_content = item.data()
        selected_val = cell_content.toPyObject()
        if isinstance(selected_val, int):
            self.pid_edit.setText(str(selected_val))
        else:
            self.status_bar.showMessage(selected_val + " is invalid!")

    def show_cell_content(self, item):
        """docstring for show_cell_content"""
        current_value = item.data().toPyObject()
        if current_value != None:
            self.status_bar.showMessage(str(current_value))

class PsInfoModel(QtCore.QAbstractTableModel):
    def __init__(self, ps_data, header, parent=None, *args):
        """docstring for __init__"""
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.ps_data = ps_data
        self.header = header
    def update(self, newpsdata):
        """docstring for update"""
        self.ps_data = newpsdata
    def rowCount(self, parent):
        """docstring for rowCount"""
        return len(self.ps_data)
    def columnCount(self, parent):
        """docstring for columnCount"""
        return 4
    def headerData(self, column, orientation, role):
        """initialize for header cells"""
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[column])
        return QtCore.QVariant()
    def data(self, idx, role):
        """docstring for data"""
        if not idx.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if idx.column() == 0:
            return QtCore.QVariant(self.ps_data[idx.row()]['pid'])
        elif idx.column() == 1:
            return QtCore.QVariant(self.ps_data[idx.row()]['name'])
        elif idx.column() == 2:
            return QtCore.QVariant(self.ps_data[idx.row()]['exe'])
        else:
            if self.ps_data[idx.row()]['cmdline'] != None:
                return QtCore.QVariant(' '.join(self.ps_data[idx.row()]['cmdline']))
            else:
                return QtCore.QVariant([])

def main():
    """docstring for main"""
    app = QtGui.QApplication(sys.argv)
    killer = PsKiller()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
