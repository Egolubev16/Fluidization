import sys
from PyQt6 import QtWidgets, uic

from scd_scheme import *


def main_click():
    capacity = float(window.edit_capacity.text())
    app_volume = window.comboBox_volume.currentText()
    app_volume = float(str.split(app_volume)[2])

    app_loading = 0.7
    material_loading = app_loading * app_volume

    number_of_ness_cycles = np.ceil(capacity / material_loading)
    print(number_of_ness_cycles)

    days_per_year = 300
    hours_per_day = 24
    hours_per_year = days_per_year * hours_per_day
    load_unload_time = 2
    total_drying_time = t + load_unload_time
    number_of_poss_cycles = np.ceil(hours_per_year / total_drying_time)
    print(number_of_poss_cycles)

    number_of_apparatuses = np.ceil(number_of_ness_cycles / number_of_poss_cycles)
    print(number_of_apparatuses)
    window.line_app_number.setText(str(min(number_of_apparatuses)))


app = QtWidgets.QApplication(sys.argv)

window = uic.loadUi("inter.ui")

window.pushButton.clicked.connect(main_click)


window.show()
app.exec()