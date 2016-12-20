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
    
_log = logging.getLogger('java')

DEFAULTS = {
    'JAVA_HOST': 'raw.githubusercontent.com',
    'JAVA_VERSION': '7',
    'JAVA_PACKAGE': 'openjdk-{JAVA_VERSION}-jre-headless.tar.gz',
    'JAVA_DOWNLOAD_URL': 'https://gitlab.liip.ch/chregu/cf-varnish-binary/raw/master/vendor/openjdk-7-jre-headless.tar.gz',
}


class JavaInstaller(object):

    def __init__(self, ctx):
        self._log = _log
        self._ctx = ctx
        self._merge_defaults()


    def _merge_defaults(self):
        for key, val in DEFAULTS.iteritems():
            if key not in self._ctx:
                self._ctx[key] = val
                           
    def should_install(self):
        return self._ctx['JAVA_JDK'] == True
    
    def install(self):
        _log.info("Installing Java")
        self._builder.install()._installer._install_binary_from_manifest(
                self._ctx['JAVA_DOWNLOAD_URL'],
                os.path.join('app'),
                extract=True)

        

def preprocess_commands(ctx):
    if ctx['JAVA_JDK'] == True:
        return (('mkdir', '/home/vcap/tmp/java/'))
    else:
        return ()


def service_environment(ctx):
    env = {}
    return env


def compile(install):
    java = JavaInstaller(install.builder._ctx)
    if java.should_install():
        _log.info("Installing Java")
        (install
            .package('JAVA')
         )
        _log.info("Java Installed.")
    return 0
    
