from setuptools import setup, find_packages

setup(name              = 'Oxys_Video_Looper',
      version           = '2.0.8',
      author            = 'Andreas Radloff',
      author_email      = 'andreas@oxys.se',
      description       = 'Play H265 video using VLC on Rpi4',
      license           = 'GNU GPLv2',
      url               = 'https://github.com/Oxyssweden/rpi-video-looper',
      install_requires  = ['pyudev', 'inputs'],
      packages          = find_packages())
