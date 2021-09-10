all:
	pyside6-uic ui/mainwindow.ui > ui/mainwindow.py
	pyside6-uic ui/addwalletfromwordsdialog.ui > ui/addwalletfromwordsdialog.py
	pyside6-uic ui/walletinfo.ui > ui/walletinfo.py
	pyside6-uic ui/addwalletfromxprvdialog.ui > ui/addwalletfromxprvdialog.py
	pyside6-uic ui/chooseutxosdialog.ui > ui/chooseutxosdialog.py
	pyside6-uic ui/privatekeydialog.ui > ui/privatekeydialog.py
