version='1.1'
release=False

if not release:
    version += '.dev'
    import os
    svn_version_file = '__svn_version__.py'

    if os.path.isfile(svn_version_file):
        import imp
        svn = imp.load_module('numexpr.__svn_version__',
                              open(svn_version_file),
                              svn_version_file,
                              ('.py','U',1))
        version += svn.version