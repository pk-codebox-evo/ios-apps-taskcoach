
from thirdparty import desktop
from mailer import thunderbird, outlook, readMail
from i18n import _

import os

class Attachment(object):
    def open(self):
        raise NotImplementedError

class FileAttachment(Attachment):
    def __init__(self, filename):
        self.filename = filename

    def open(self):
        desktop.open(os.path.normpath(self.filename))

    def __repr__(self):
        return 'FILE:%s' % self.filename

    def __unicode__(self):
        return unicode(self.filename)

    def __cmp__(self, other):
        try:
            return cmp(self.filename, other.filename)
        except AttributeError:
            return 1

class URIAttachment(Attachment):
    def __init__(self, uri):
        self.uri = uri

    def open(self):
        desktop.open(self.uri)

    def __repr__(self):
        return 'URI:%s' % self.uri

    def __unicode__(self):
        return self.uri

    def __cmp__(self, other):
        try:
            return cmp(self.uri, other.uri)
        except AttributeError:
            return 1

class MailAttachment(Attachment):
    def __init__(self, filename):
        self.filename = filename

        self.subject, self.description = readMail(filename)

        if self.subject is None:
            self.subject = _('Untitled e-mail')

    def open(self):
        desktop.open(self.filename) # FIXME

    def __repr__(self):
        return 'MAIL:' + self.filename

    def __unicode__(self):
        return self.subject

    def __cmp__(self, other):
        try:
            return cmp(self.filename, other.filename)
        except AttributeError:
            return 1


#==============================================================================
#

def AttachmentFactory(s):
    if s.startswith('URI:'):
        return URIAttachment(s[4:])
    elif s.startswith('FILE:'):
        return FileAttachment(s[5:])
    elif s.startswith('MAIL:'):
        return MailAttachment(s[5:])

    # Assume old task file

    return FileAttachment(s)
