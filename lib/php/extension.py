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
from compile_helpers import convert_php_extensions
from compile_helpers import is_web_app
from compile_helpers import find_stand_alone_app_to_run
from compile_helpers import load_manifest
from compile_helpers import find_all_php_versions
from compile_helpers import validate_php_version
from compile_helpers import validate_php_extensions
from extension_helpers import ExtensionHelper
import string


class PHPExtension(ExtensionHelper):
    def _should_compile(self):
        return self._ctx['PHP_VM'] == 'php'

    def _configure(self):
        manifest = load_manifest(self._ctx)
        dependencies = manifest['dependencies']
        self._ctx['ALL_PHP_VERSIONS'] = find_all_php_versions(dependencies)

    def _preprocess_commands(self):
        return (('$HOME/.bp/bin/rewrite', '"$HOME/php/etc"'),)

    def _service_commands(self):
        if is_web_app(self._ctx):
            return {
                'php-fpm': (
                    '$HOME/php/sbin/php-fpm',
                    '-p "$HOME/php/etc"',
                    '-y "$HOME/php/etc/php-fpm.conf"',
                    '-c "$HOME/php/etc"')
            }
        else:
            app = find_stand_alone_app_to_run(self._ctx)
            return {
                'php-app': (
                    '$HOME/php/bin/php',
                    '-c "$HOME/php/etc"',
                    app)
            }

    def _service_environment(self):
        env = {
            'LD_LIBRARY_PATH': '$LD_LIBRARY_PATH:$HOME/php/lib',
            'PATH': '$PATH:$HOME/php/bin:$HOME/php/sbin',
            'PHPRC': '$HOME/php/etc'
        }
        if 'snmp' in self._ctx['PHP_EXTENSIONS']:
            env['MIBDIRS'] = '$HOME/php/mibs'
        return env

    def _compile(self, install):
        print 'Installing PHP'
        ctx = install.builder._ctx
        validate_php_version(ctx)
        print 'PHP %s' % (ctx['PHP_VERSION'])

        major_minor = '.'.join(string.split(ctx['PHP_VERSION'], '.')[0:2])

        (install
            .package('PHP')
            .done())
        validate_php_extensions(ctx)
        convert_php_extensions(ctx)
        (install
            .config()
                .from_application('.bp-config/php')  # noqa
                .or_from_build_pack('defaults/config/php/%s.x' % major_minor)
                .to('php/etc')
                .rewrite()
                .done())
        return 0


# Register extension methods
PHPExtension.register(__name__)
