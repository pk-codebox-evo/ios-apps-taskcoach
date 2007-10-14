import wx, os, re, tempfile
from thirdparty import desktop
from i18n import _

def readMail(filename, readContent=True):
    subject = None
    content = ''
    encoding = None
    s = 0
    rx = re.compile('charset=([-0-9a-zA-Z]+)')

    for line in file(filename, 'r'):
        if s == 0:
            if line.lower().startswith('subject:'):
                subject = line[8:].strip()
            if line.strip() == '':
                if not readContent:
                    break
                s = 1
            mt = rx.search(line)
            if mt:
                encoding = mt.group(1)
        elif s == 1:
            content += line

    if encoding is None:
        encoding = wx.Locale_GetSystemEncodingName()
	if not encoding:
	    encoding = 'ISO-8859-1'

    if subject is None:
        subject = _('Untitled e-mail')
    else:
        subject = subject.decode(encoding)

    content = content.decode(encoding)

    return subject, content

def openMailWithOutlook(filename):
    id_ = None
    for line in file(filename, 'r'):
        if line.startswith('X-Outlook-ID:'):
            id_ = line[13:].strip()
            break
        elif line.strip() == '':
            break

    if id_ is None:
        return False

    from win32com.client import GetActiveObject
    app = GetActiveObject('Outlook.Application')
    app.ActiveExplorer().Session.GetItemFromID(id_).Display()

    return True

def openMail(filename):
    if os.name == 'nt':
        # Find out if Outlook is the so-called 'default' mailer.
        import _winreg
        key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT,
                              r'mailto\shell\open\command')
        try:
            value, type_ = _winreg.QueryValueEx(key, '')
            if type_ in [_winreg.REG_SZ, _winreg.REG_EXPAND_SZ]:
                if 'outlook.exe' in value.lower():
                    try:
                        if openMailWithOutlook(filename):
                            return
                    except:
                        pass
        finally:
            _winreg.CloseKey(key)

    desktop.open(filename)
