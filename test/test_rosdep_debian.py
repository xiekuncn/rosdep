# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Willow Garage, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Author Ken Conley/kwc@willowgarage.com

import os

def get_test_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'debian'))

def test_dpkg_detect():
    from rosdep2.platforms.debian import dpkg_detect
    from mock import Mock
    
    m = Mock()
    m.return_value = ''
    val = dpkg_detect(['tinyxml-dev'], exec_fn=m)
    assert val == [], val
    #assert m.assert_called_with(['dpkg-query', '-W', '-f=\'${Package} ${Status}\n\''])

    with open(os.path.join(get_test_dir(), 'dpkg-python-apt'), 'r') as f:
        m.return_value = f.read()
    val = dpkg_detect(['apt', 'tinyxml-dev', 'python'], exec_fn=m)
    assert val == ['apt', 'python'], val

    # test version lock code (should be filtered out w/o validation)
    val = dpkg_detect(['apt=1.8', 'tinyxml-dev', 'python=2.7'], exec_fn=m)
    assert val == ['apt=1.8', 'python=2.7'], val


def test_AptInstaller():
    from rosdep2.platforms.debian import AptInstaller
    from mock import patch

    @patch.object(AptInstaller, 'get_packages_to_install')
    def test(mock_method):
        installer = AptInstaller()
        mock_method.return_value = []
        assert '' == installer.get_install_command(['fake'])

        mock_method.return_value = ['a', 'b']
        expected = "#!/bin/bash\n#Packages ['a', 'b']\nsudo apt-get install -y a b"
        val = installer.get_install_command(['whatever'], interactive=False)
        assert val == expected, val
        expected = "#!/bin/bash\n#Packages ['a', 'b']\nsudo apt-get install a b"
        val = installer.get_install_command(['whatever'], interactive=True)
        assert val == expected, val
    test()
    
class FakeDetector:
    def __init__(self, version):
        self.version = version
    def get_codename(self):
        return 'codename'
    def is_os(self):
        return True
    def get_version(self):
        return self.version

def test_MintOsDetect():
    from rosdep2.platforms.debian import MintOsDetect
    d = MintOsDetect(FakeDetector('11'))
    assert d.is_os()
    assert 'codename' == d.get_codename()
    assert '11.04' == d.get_version()
