# -*- coding: utf-8 -*-
"""Controller for logged-in users"""

from tg import expose, flash, require, url, lurl
from tg import request, validate, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from addrbook import model
from addrbook.controllers.secure import SecureController
from addrbook.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from addrbook.lib.base import BaseController
from addrbook.controllers.error import ErrorController

from addrbook.model.addressbook import Addressbook
from addrbook.model import User

from sqlalchemy.orm.exc import *
from sqlalchemy import func

# widgets, forms
import tw2.core as twc
import tw2.forms as twf

# authorizations
from tg.predicates import not_anonymous


__all__ = ['UserController']


# class for form widget
class AddContactForm(twf.Form):
    class child(twf.TableLayout):
        name = twf.TextField(validator=twc.Required)
        number = twf.TextField(validator=twc.Required)
    action = '/contactlist/addcontact'

class UserController(BaseController):
    """
    The root controller for the addrbook application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    allow_only = not_anonymous()

    def username(self):
        try:
            username = request.identity['repoze.who.userid']
            return username
        except (KeyError,TypeError):
             raise

    @expose('addrbook.templates.contacts')
    def _default(self):
        """Handle the front-page."""
        contacts = self.contactlist()
        try:
            username = self.username()
        except TypeError:
            username = ""
        partial, total = self.count_contacts()
        return dict(page='index', contacts=contacts, user=username, partial=partial)

    def contactlist(self):
        try:
            username = self.username()
            contacts = DBSession.query(Addressbook).filter(Addressbook.users.any(user_name=username))
            return [contact for contact in contacts.order_by(Addressbook.name)]
        except TypeError:
            return []

    def count_contacts(self):
        try:
            username = self.username()
            partial = DBSession.query(Addressbook).filter(Addressbook.users.any(user_name=username)).count()
            total = DBSession.query(Addressbook.id).count()
            return partial, total
        except TypeError:
            return 0, 0

    @expose('addrbook.templates.add')
    def add(self):
        """Handle the 'add' page."""
        return dict(page='add', form=AddContactForm)

    # handles missing fields (failed validation)
    @expose()
    def fieldrequired_handler(self, name, number):
        flash(_('Insert both fields!'), 'error')
        redirect('/contactlist/add')

    @expose()
    @validate(AddContactForm, error_handler=fieldrequired_handler)
    def addcontact(self, name, number):
        username = self.username()
        try:
            new_contact = Addressbook(name=name, number=number)
            new_contact.users.append(DBSession.query(User).filter_by(user_name=username).one())
            DBSession.add(new_contact)
            flash(_('New contact added to '+username))
        except TypeError:
            flash(_('DB query failed'), 'error')
        redirect('/contactlist')

    @expose()
    def deletecontact(self, name, number):
        username = self.username()
        toBeDeleted = DBSession.query(Addressbook).filter(Addressbook.users.any(user_name=username)).filter(Addressbook.name==name).filter(Addressbook.number==number)
        toBeDeleted.delete(synchronize_session='fetch')
        flash(_('Contact deleted'))
        redirect('/contactlist')

    @expose('json')
    def export(self):
        username = self.username()
        contacts = self.contactlist()
        return dict(username=username, contacts=contacts)

    @expose('addrbook.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('addrbook.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('addrbook.templates.data')
    @expose('json')
    def data(self, **kw):
        """
        This method showcases how you can use the same controller
        for a data page and a display page.
        """
        return dict(page='data', params=kw)
    @expose('addrbook.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('addrbook.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')
