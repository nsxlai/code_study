import pywinauto
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from time import sleep


if __name__ == '__main__':

    app = Application().start(cmd_line=u'C:\Program Files\Insta360 Studio 2022\Insta360 Studio 2022.exe')
    sleep(2)
    app.Insta360Studio2022.MenuItem(u'&File(F)->&Open Files(O)').click()
