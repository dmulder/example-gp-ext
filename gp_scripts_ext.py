# Group Policy Scripts Client Side Extension
# Copyright (C) David Mulder <dmulder@suse.com> 2018
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
from samba.gpclass import gp_inf_ext

class gp_scripts_ext(gp_inf_ext):

    def __str__(self):
        return "Scripts"

    def process_group_policy(self, deleted_gpo_list, changed_gpo_list):
        '''
        process_group_policy() gets two parameters; deleted_gpo_list and
        changed_gpo_list. The deleted list is gpos that have been deleted from
        the server, and need to be unapplied. Running gpupdate --unapply will
        treat all gpos as though they've been removed. The changed list is gpos
        that have been modified, and need to be re-applied (or it could be new
        gpos also).
        '''
        for gpo in deleted_gpo_list:
            pass

        for gpo in changed_gpo_list:
            # You need to make sure a file_sys_path is provided. Local policies
            # (which don't really exist here) don't provide a path.
            if gpo.file_sys_path:
                # The gp_db is a cache of policy changes. You must call
                # set_guid() each time you work on a different gpo, and you
                # must call commit() at the end.
                self.gp_db.set_guid(gpo.name)
                # parse and apply the setting here
                # The manual call to commit() prevents accidental commiting of
                # settings if the apply fails (if we fail to apply the
                # settings, we don't want the cache to say it succeeded).
                self.gp_db.commit()

