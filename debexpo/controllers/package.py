# -*- coding: utf-8 -*-
#
#   package.py — Package controller
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonnylamb@jonnylamb.com
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

"""
Holds the PackageController.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

from datetime import datetime
import logging
import os

from debexpo.lib.base import *
from debexpo.lib import constants
from debexpo.lib.utils import get_package_dir

from debexpo.model import meta
from debexpo.model.packages import Package
from debexpo.model.package_versions import PackageVersion
from debexpo.model.users import User
from debexpo.model.package_comments import PackageComment
from debexpo.model.package_info import PackageInfo
from debexpo.model.source_packages import SourcePackage
from debexpo.model.binary_packages import BinaryPackage
from debexpo.model.package_files import PackageFile

log = logging.getLogger(__name__)

class PackageController(BaseController):

    def _get_package(self, packagename):
        """
        """
        log.debug('Details of package "%s" requested' % packagename)

        package = meta.session.query(Package).filter_by(name=packagename).first()

        if package is None:
            log.error('Could not get package information')
            return redirect_to(h.url_for(controller='packages', packagename=None))

        c.package = package
        c.config = config
        c.package_dir = get_package_dir(package.name)
        return package

    def index(self, packagename):
        """
        Entry point into the controller. Displays information about the package.

        ``packagename``
            Package name to look at.
        """
        package = self._get_package(packagename)
        if not isinstance(package, Package):
            return package

        c.session = session
        c.constants = constants
        c.outcomes = {
            _('Unreviewed') : constants.PACKAGE_COMMENT_OUTCOME_UNREVIEWED,
            _('Needs work') : constants.PACKAGE_COMMENT_OUTCOME_NEEDS_WORK,
            _('Perfect') : constants.PACKAGE_COMMENT_OUTCOME_PERFECT,
        }

        if 'user_id' in session:
            c.user = meta.session.query(User).filter_by(id=session['user_id']).one()
        else:
            c.user = None

        log.debug('Rendering page')
        return render('/package/index.mako')

    def rfs(self, packagename):
        """
        RFS boilerplate creation.

        ``packagename``
            Package name to look at.
        """
        package = self._get_package(packagename)
        if not isinstance(package, Package):
            return package

        log.debug('Rendering page')
        return render('/package/rfs.mako')

    def comment(self, packagename):
        """
        Comment submission.

        ``packagename``
            Package name to look at.
        """
        package = self._get_package(packagename)
        if not isinstance(package, Package):
            return package

        status = constants.PACKAGE_COMMENT_STATUS_NOT_UPLOADED
        if 'status' in request.POST and request.POST['status']:
            status = constants.PACKAGE_COMMENT_STATUS_UPLOADED

        comment = PackageComment(user_id=session['user_id'],
            package_version_id=request.POST['package_version'],
            text=request.POST['text'],
            time=datetime.now(),
            outcome=request.POST['outcome'],
            status=status)

        meta.session.save(comment)
        meta.session.commit()

        return h.rails.redirect_to('package', packagename=packagename)
