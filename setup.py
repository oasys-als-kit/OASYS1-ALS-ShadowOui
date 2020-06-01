#! /usr/bin/env python3

import imp
import os
import sys
import subprocess

NAME = 'OASYS1-ALS-ShadowOui'

VERSION = '0.0.53'
ISRELEASED = False

DESCRIPTION = 'WIDGETS DEVELOPED FOR ALS TO EXTEND OASYS FUNCTIONALITIES'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Luca Rebuffi and Antoine Wojdyla and Manuel Sanchez del Rio'
AUTHOR_EMAIL = 'awojdyla@lbl.gov, srio@lbl.gov'
URL = 'https://github.com/oasys-als-kit/OASYS1-ALS-ShadowOui'
DOWNLOAD_URL = 'https://github.com/oasys-als-kit/OASYS1-ALS-ShadowOui'
LICENSE = 'MIT'

KEYWORDS = (
    'ray-tracing',
    'simulator',
    'oasys1',
)

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Cython',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Science/Research',
)


SETUP_REQUIRES = (
                  'setuptools',
                  )

INSTALL_REQUIRES = (
                    'setuptools',
                    'shadow4>=0.0.16',
                    'wofry>=0.0.24',
                    'numba',
                   )

if len({'develop', 'release', 'bdist_egg', 'bdist_rpm', 'bdist_wininst',
        'install_egg_info', 'build_sphinx', 'egg_info', 'easy_install',
        'upload', 'test'}.intersection(sys.argv)) > 0:
    import setuptools
    extra_setuptools_args = dict(
        zip_safe=False,  # the package can run out of an .egg file
        include_package_data=True,
        install_requires=INSTALL_REQUIRES
    )
else:
    extra_setuptools_args = dict()

from setuptools import find_packages, setup

PACKAGES = find_packages(
                         exclude = ('*.tests', '*.tests.*', 'tests.*', 'tests'),
                         )

PACKAGE_DATA = {"orangecontrib.shadow.als.widgets.utility":["icons/*.png", "icons/*.jpg",],
                "orangecontrib.xoppy.als.widgets.srcalc":["icons/*.png", "icons/*.jpg",],
                "orangecontrib.syned.als.widgets.tools":["icons/*.png", "icons/*.jpg",],
                "orangecontrib.wofry.als.widgets.extensions":["icons/*.png", "icons/*.jpg",],
}

NAMESPACE_PACAKGES = ["orangecontrib",
                      "orangecontrib.shadow", "orangecontrib.shadow.als", "orangecontrib.shadow.als.widgets",
                      "orangecontrib.xoppy", "orangecontrib.xoppy.als", "orangecontrib.xoppy.als.widgets",
                      "orangecontrib.syned", "orangecontrib.syned.als", "orangecontrib.syned.als.widgets",
                      "orangecontrib.wofry", "orangecontrib.wofry.als", "orangecontrib.wofry.als.widgets",
                      ]

ENTRY_POINTS = {
    'oasys.addons' : (
        "Shadow ALS Extension = orangecontrib.shadow.als",
        "XOPPY ALS Extension = orangecontrib.xoppy.als",
        "Wofry ALS Extension = orangecontrib.wofry.als",
        "Syned ALS Extension = orangecontrib.syned.als",
    ),
    'oasys.widgets' : (
        "Shadow ALS Extension = orangecontrib.shadow.als.widgets.utility",
        "XOPPY ALS Extension = orangecontrib.xoppy.als.widgets.srcalc",
        "Syned ALS Extension = orangecontrib.syned.als.widgets.tools",
        "Wofry ALS Extension = orangecontrib.wofry.als.widgets.extensions",
    ),
}

if __name__ == '__main__':
    is_beta = False

    try:
        import PyMca5, PyQt4

        is_beta = True
    except:
        setup(
              name = NAME,
              version = VERSION,
              description = DESCRIPTION,
              long_description = LONG_DESCRIPTION,
              author = AUTHOR,
              author_email = AUTHOR_EMAIL,
              url = URL,
              download_url = DOWNLOAD_URL,
              license = LICENSE,
              keywords = KEYWORDS,
              classifiers = CLASSIFIERS,
              packages = PACKAGES,
              package_data = PACKAGE_DATA,
              #          py_modules = PY_MODULES,
              setup_requires = SETUP_REQUIRES,
              install_requires = INSTALL_REQUIRES,
              #extras_require = EXTRAS_REQUIRE,
              #dependency_links = DEPENDENCY_LINKS,
              entry_points = ENTRY_POINTS,
              namespace_packages=NAMESPACE_PACAKGES,
              include_package_data = True,
              zip_safe = False,
              )

    if is_beta: raise NotImplementedError("This version of <APP NAME> doesn't work with Oasys1 beta.\nPlease install OASYS1 final release: http://www.elettra.eu/oasys.html")
