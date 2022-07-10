import pywinauto

def auto_open():
    app = pywinauto.application.Application()
    app.start('C:\\CREON\\STARTER\\coStarter.exe /prj:cp /id:{id} /pwd:{pwd} /pwdcert:{pwdcert} /autostart'.format(id='*****',
                                                                                                             pwd='*****',
                                                                                                         pwdcert='*****'))
