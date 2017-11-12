# -*- coding: utf-8 -*-
"""Setup the addrbook application"""
from __future__ import print_function, unicode_literals
import transaction
from addrbook import model


def bootstrap(command, conf, vars):
    """Place any commands to setup addrbook here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        # manager user
        u = model.User()
        u.user_name = 'manager'
        u.display_name = 'Example manager'
        u.email_address = 'manager@somedomain.com'
        u.password = 'managepass'

        model.DBSession.add(u)

        # managers group
        g = model.Group()
        g.group_name = 'managers'
        g.display_name = 'Managers Group'
        # add last created manager to the group
        g.users.append(u)

        model.DBSession.add(g)

        # create manage permission
        p = model.Permission()
        p.permission_name = 'manage'
        p.description = 'This permission gives an administrative right'
        # add the managers group (g) to the groups that have 'manage' permission (p)
        p.groups.append(g)

        model.DBSession.add(p)

        # creates another user, with no permissions
        u1 = model.User()
        u1.user_name = 'editor'
        u1.display_name = 'Example editor'
        u1.email_address = 'editor@somedomain.com'
        u1.password = 'editpass'

        model.DBSession.add(u1)

        # sample entries in address book database
        c = model.Addressbook(name="Businessman", number="99999999")
        # saves this contact for the manager user (u)
        c.users.append(u)
        # creates and add a contact for editor user (u1)
        c1 = model.Addressbook(name="Giotto", number="0000")
        c1.users.append(u1)

        model.DBSession.add(c)

        # flush and commit
        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print('Warning, there was a problem adding your auth data, '
              'it may have already been added:')
        import traceback
        print(traceback.format_exc())
        transaction.abort()
        print('Continuing with bootstrapping...')

    # <websetup.bootstrap.after.auth>
