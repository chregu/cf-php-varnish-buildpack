# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import os.path
import logging
    
_log = logging.getLogger('supervisor')

DEFAULTS = {
    'SUPERVISOR_HOST': 'raw.githubusercontent.com',
    'SUPERVISOR_VERSION': '3.0b2',
    'SUPERVISOR_PACKAGE': 'supervisor-{SUPERVISOR_VERSION}.tar.gz',
    'SUPERVISOR_DOWNLOAD_URL': 'supervisor-{SUPERVISOR_VERSION}.tar.gz'
}


class SupervisorInstaller(object):

    def __init__(self, ctx):
        self._log = _log
        self._ctx = ctx
        self._merge_defaults()


    def _merge_defaults(self):
        for key, val in DEFAULTS.iteritems():
            if key not in self._ctx:
                self._ctx[key] = val
                           
    def should_install(self):
        return self._ctx['SUPERVISORD'] == True
    
    def install(self):
        _log.info("Installing Supervisor")
        self._builder.install()._installer._install_binary_from_manifest(
                self._ctx['SUPERVISOR_DOWNLOAD_URL'],
                os.path.join('app'),
                extract=True)

        

def preprocess_commands(ctx):
    if ctx['SUPERVISORD'] == True:
        return (('mkdir', '/home/vcap/tmp/supervisor/'),
            ('$HOME/.bp/bin/rewrite', '"$HOME/supervisor/etc/conf.d"'))
    else:
        return ()


def service_commands(ctx):
    
    if ctx['SUPERVISORD'] == True:
        #return {'supervisor': ('echo $PYTHONPATH')}
        returnVal = {
                'supervisor': (
                    '$HOME/supervisor/bin/supervisord',
                    '--nodaemon',
                    '--configuration',
                    '$HOME/supervisor/etc/supervisord.conf',
                    '--logfile',
                    '-',
                    '--pidfile',
                    '$TMPDIR/supervisor.pid',
                    '2>&1'
                    )
                 }        
        return returnVal
    else:
        return {}


def service_environment(ctx):
    env = {}
    return env


def compile(install):
    supervisor = SupervisorInstaller(install.builder._ctx)
    if supervisor.should_install():
        _log.info("Installing Supervisor")
        (install
            .package('SUPERVISOR')
            .config()
                .from_application('.bp-config/supervisor')  # noqa
                #.or_from_build_pack('defaults/config/varnish/{VARNISH_VERSION}')
                .to('supervisor/etc/conf.d')
                .rewrite()
                .done()
             .builder
                .copy()
                .under('/tmp/app/supervisor/lib/python2.7/site-packages')
                .into('{BUILD_DIR}/.bp/lib')
                .done()
         )
        _log.info("Supervisor Installed.")
    return 0
    
