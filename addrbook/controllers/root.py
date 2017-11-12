# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl
from tg import request, redirect, tmpl_context
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

__all__ = ['RootController']


class RootController(BaseController):
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

    def _before(self, *args, **kw):
        tmpl_context.project_name = "addrbook"

    @expose('addrbook.templates.index')
    def _default(self):
        """Handle the front-page."""
        (contacts, partial) = self.contactlist()
        username = ""
        try:
            username = request.identity['repoze.who.userid']
        except:
            username = ""
        total = DBSession.query(Addressbook.id).count()
        return dict(page='index', contacts=contacts, user=username, total=total, partial=partial)

    def contactlist(self):
        try:
            username = request.identity['repoze.who.userid']
            contacts = DBSession.query(Addressbook).filter(Addressbook.users.any(user_name=username))
            number_of_contacts = contacts.count()
            return ([contact for contact in contacts.order_by(Addressbook.name)],number_of_contacts)
        except TypeError:
            return ([],0)

    @expose('addrbook.templates.add')
    def add(self, default_name="", default_number=""):
        """Handle the 'add' page."""
        return dict(page='add', default_name=default_name, default_number=default_number)

    @expose()
    def addcontact(self, redirectto, name, number, submit):
        if name.strip()=="":
            flash(_('Name required!'), 'error')
            redirect('/add', params=dict(default_number=number))
        elif number.strip()=="":
            flash(_('Number required!'), 'error')
            redirect('/add', params=dict(default_name=name))
        else:
            try:
                username = request.identity['repoze.who.userid']
                new_contact = Addressbook(name=name, number=number)
                print("""
                """+str(len(new_contact.users))+"""
                """)
                new_contact.users.append(DBSession.query(User).filter_by(user_name=username).one())
                DBSession.add(new_contact)
                print("""
                """+str(len(new_contact.users))+"""
                """)
                flash(_('New contact added to '+username))
            except TypeError:
                flash(_('No user logged. Login first.'), 'error')
            redirect("/")

    @expose()
    def deletecontact(self, name, number):
        username = request.identity['repoze.who.userid']
        toBeDeleted = DBSession.query(Addressbook).filter(Addressbook.users.any(user_name=username)).filter(Addressbook.name==name).filter(Addressbook.number==number)
        toBeDeleted.delete(synchronize_session='fetch')

        flash(_('Contact deleted'))
        redirect('/')

    # @expose(content_type='application/json')
    # def stream_db(self):
    #     def output_pause():
    #         num = 0
    #         yield '['
    #         while num < 9:
    #             u = DBSession.query(model.User).filter_by(user_id=num).first()
    #             num += 1
    #             yield u and '%d, ' % u.user_id or 'null, '
    #             time.sleep(1)
    #         yield 'null]'
    # return output_pause()

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

    @expose('addrbook.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)
