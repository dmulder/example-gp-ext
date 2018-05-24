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

import os.path, re
from samba.gpclass import gp_inf_ext
from samba.gp_file_append import gp_file_append

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

        inf_file = 'MACHINE/Scripts/scripts.ini'
        for gpo in changed_gpo_list:
            # You need to make sure a file_sys_path is provided. Local policies
            # (which don't really exist here) don't provide a path.
            if gpo.file_sys_path:
                # The gp_db is a cache of policy changes. You must call
                # set_guid() each time you work on a different gpo, and you
                # must call commit() at the end.
                self.gp_db.set_guid(gpo.name)
                path = gpo.file_sys_path.split('\\sysvol\\')[-1]
                # Each extension is required to provide a read() function. The
                # parse() function reads the raw text from the sysvol file
                # passed as the first parameter, then calls the extensions
                # read() function and returns the results. In our case, we've
                # inherited from the gp_inf_ext class which already implements
                # the read() function for us. Our read() function just returned
                # a ConfigParser object which has already parsed the ini file
                # for us.
                inf_conf = self.parse(os.path.join(path, inf_file))
                settings = {}
                for section in inf_conf.sections():
                    section_settings = {}
                    for key, value in inf_conf.items(section):
                        for param in ['CmdLine', 'Parameters']:
                            m = re.match('(\d+)%s' % param, key)
                            if m:
                                if not m.group(1) in section_settings.keys():
                                    section_settings[m.group(1)] = {}
                                section_settings[m.group(1)][param] = value
                    settings[section] = section_settings

                for key in settings.keys():
                    script_path = os.path.join(self.lp.cache_path('gpo_cache'),
                                               path.replace('\\', '/'),
                                               'MACHINE/Scripts', key)
                    if key == 'Startup':
                        profile = gp_file_append('/etc/cron.d/gp_startup')
                        for num, value in settings[key].items():
                            script = os.path.join(script_path,
                                                  value['CmdLine'])
                            cmd = ' '.join(['@reboot', script,
                                            value['Parameters']])
                            current = profile.get_section()
                            if not cmd in current:
                                current = current.strip() + '\n' + cmd
                                profile.set_section(current)
                                self.gp_db.store(str(self), num+key, None)
                # The manual call to commit() prevents accidental commiting of
                # settings if the apply fails (if we fail to apply the
                # settings, we don't want the cache to say it succeeded).
                self.gp_db.commit()

if __name__ == "__main__":
    from samba import gpo
    guid = '{40B6664F-4972-11D1-A7CA-0000F87571E3}'
    name = 'gp_scripts_ext'
    path = os.path.abspath(__file__)

    # The register_gp_extension() installs the extension in the registry path
    # Software/Microsoft/Windows NT/CurrentVersion/Winlogon/GPExtensions. The
    # required parameters are a unique guid which identifies the client side
    # extension, the name of the extension class, and a path to the extension.
    # There are also three optional parameters, smb_conf, which when provided,
    # effects the location of the registry (this is mostly for automated
    # testing), and a machine and user parameter. The machine and user
    # parameters both default to True, or the extension is enabled for both
    # machine and user policies. In our case we disable the user policy since
    # we won't be implementing that here.
    gpo.register_gp_extension(guid, name, path, machine=True, user=False)

