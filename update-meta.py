import os
import re
import sys
import json
import subprocess


class PackageUpdater:
    PKG_NAME = 'pfSense-pkg-FauxAPI'
    PKG_INTERNAL_NAME = 'fauxapi'

    def __init__(self, repo_path, bump_rev=False):
        self.__repo_path = repo_path.replace('\\', '/').rstrip('/')
        if not self.__repo_path:
            self.__repo_path = os.getcwd().replace('\\', '/').rstrip('/')
        self.__package_name = ''
        self.__bump_revision = bump_rev
        self.package_version = '0.0'
        self.package_revision = 0

    def repo_path(self):
        return self.__repo_path

    @staticmethod
    def __write_plist(plist_file, dir_list, file_list):
        with open(plist_file, 'w') as f:
            for dir_name in dir_list:
                f.write('@dir %s\n' % dir_name)
                for file_name in file_list:
                    if os.path.dirname(file_name) == dir_name:
                        f.write(file_name + '\n')
                f.write('\n')

    @staticmethod
    def __update_priv(priv_file, dir_list, file_list, prefix=PKG_INTERNAL_NAME):
        with open(priv_file, 'r') as f:
            in_lines = f.readlines()
        priv_name = ''
        # the regular expression to get the privilege name.
        priv_re = re.compile(r'\A\$priv_list\[\'([^\']+)\']\[\'name\']')
        for line in in_lines:
            m = priv_re.match(line)
            if m:
                priv_name = m.group(1)
        if not priv_name:
            raise RuntimeWarning('Failed to determine privilege name in %s' % priv_file)
        # the regular expression that creates the match array.
        priv_re = re.compile(r'\A\$priv_list\[\'%s\']\[\'match\']\s*=\s*array\(\)' % priv_name)
        priv_line = '$priv_list[\'%s\'][\'match\'][]' % priv_name
        web_root = '/usr/local/www'
        path_start = '%s/%s' % (web_root, prefix)
        with open(priv_file, 'w') as f:
            for line in in_lines:
                if priv_re.match(line):
                    f.write(line)
                    for dir_name in dir_list:
                        index = dir_name + '/index.php'
                        if dir_name.startswith(path_start):
                            if index in file_list:
                                f.write('%s = \'%s/\';\n' % (priv_line, dir_name[len(web_root):]))
                                f.write('%s = \'%s\';\n' % (priv_line, index[len(web_root):]))
                            for file_name in file_list:
                                if file_name.startswith(dir_name) and file_name.endswith('.php') and file_name != index:
                                    f.write('%s = \'%s\';\n' % (priv_line, file_name[len(web_root):]))
                elif not line.startswith(priv_line):
                    f.write(line)

    def __update_makefile(self, makefile, dir_list, file_list, versioned_files, config_file):
        self.package_version = '0.0'
        self.package_revision = 0
        with open(makefile, 'r') as f:
            in_lines = f.readlines()
        with open(makefile, 'w') as f:
            skip = False
            for line in in_lines:
                if line.startswith('do-install:'):
                    skip = True
                    f.write(line)
                    # do not include root files.
                    for dir_name in dir_list:
                        f.write('\t${MKDIR} ${STAGEDIR}%s\n' % dir_name)
                        for file_name in file_list:
                            if os.path.dirname(file_name) == dir_name:
                                if dir_name.startswith('/usr/local/bin'):
                                    f.write('\t${INSTALL_DATA} -m 0755 ${FILESDIR}%s ${STAGEDIR}%s\n' %
                                            (file_name, dir_name))
                                elif file_name == config_file:
                                    f.write('\t${INSTALL_DATA} -m 0644 ${FILESDIR}%s ${STAGEDIR}%s\n' %
                                            (file_name, dir_name))
                                else:
                                    f.write('\t${INSTALL_DATA} ${FILESDIR}%s ${STAGEDIR}%s\n' % (file_name, dir_name))
                        f.write('\n')
                    for file_name in versioned_files:
                        f.write(
                            '\t@${REINPLACE_CMD} -i \'\' -e "s|%%%%PKGVERSION%%%%|${PKGVERSION}|" ${STAGEDIR}%s\n' %
                            file_name)
                    f.write('\n')
                elif not skip:
                    if line.startswith('PORTVERSION'):
                        _, v = line.split('=', 2)
                        self.package_version = v.strip()
                        f.write(line)
                    elif line.startswith('PORTREVISION'):
                        _, v = line.split('=', 2)
                        self.package_revision = int(v.strip())
                        if self.__bump_revision:
                            self.package_revision += 1
                            line = "PORTREVISION=\t" + str(self.package_revision) + "\n"
                        f.write(line)
                    else:
                        f.write(line)
                elif line and line.strip() and line[0] != ' ' and line[0] != '\t':
                    skip = False
                    f.write(line)

    def __update_about(self):
        tmp_input = '/tmp/input.json'
        source_md = '%s/README.md' % self.__repo_path
        target_php = '%s/%s/files/usr/local/www/%s/admin/about.php' % (
            self.__repo_path,
            self.PKG_NAME,
            self.PKG_INTERNAL_NAME
        )
        data = {
            'mode': 'markdown'
        }
        with open(source_md, 'r') as f:
            data['text'] = f.read()
        data = json.dumps(data)
        with open(tmp_input, 'w') as f:
            f.write(data)
        content = subprocess.check_output([
            '/usr/local/bin/curl',
            '--silent',
            '--data',
            '@' + tmp_input,
            'https://api.github.com/markdown'
        ])
        head = ''
        tail = ''
        part = 1
        with open(target_php, 'r') as f:
            for line in f:
                if part == 1:
                    head += line
                elif part == 3:
                    tail += line
                if 'READMESTART' in line:
                    part = 2
                elif 'READMEEND' in line:
                    part = 3
                    tail = line
        data = head + content + tail
        with open(target_php, 'w') as f:
            f.write(data)

    def update_meta(self):
        # the metadata files we need to update.
        makefile = '%s/%s/Makefile' % (self.__repo_path, self.PKG_NAME)
        plist = '%s/%s/pkg-plist' % (self.__repo_path, self.PKG_NAME)
        priv = '%s/%s/files/etc/inc/priv/%s.priv.inc' % (self.__repo_path, self.PKG_NAME, self.PKG_INTERNAL_NAME)

        # the files that get the package version (relative to STAGEDIR)
        versioned_files = [
            '/usr/local/pkg/%s.xml' % self.PKG_INTERNAL_NAME,
            '/usr/local/share/%s/info.xml' % self.PKG_NAME,
            '/etc/inc/%s/%s_actions.inc' % (self.PKG_INTERNAL_NAME, self.PKG_INTERNAL_NAME)
        ]

        # the config file get rw access
        config_file = '/usr/local/pkg/%s.xml' % self.PKG_INTERNAL_NAME

        try:
            os.chdir(self.PKG_NAME)
            os.chdir('files')

            # construct the file and directory lists.
            file_list = []
            dir_list = []
            for (path, _dirs, files) in os.walk('.'):
                if files:
                    if len(path) > 2:
                        dir_list.append(path[1:].replace('\\', '/'))
                    for n in files:
                        if len(path) > 2:
                            file_list.append(path[1:].replace('\\', '/') + '/' + n)
                        else:
                            file_list.append(n)

            print('> Updating metadata...')
            self.__write_plist(plist, dir_list, file_list)
            self.__update_priv(priv, dir_list, file_list, '%s/admin' % self.PKG_INTERNAL_NAME)
            self.__update_makefile(makefile, dir_list, file_list, versioned_files, config_file)
            self.__update_about()
        finally:
            os.chdir(self.__repo_path)


bump = 'bump-revision' in sys.argv
pu = PackageUpdater(os.path.dirname(__file__), bump)
print('Repo: %s' % pu.repo_path())
pu.update_meta()
print('Package Version: %s_%d' % (pu.package_version, pu.package_revision))
