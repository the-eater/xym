import sys

# Remove current dir
sys.path.pop(0)
sys.path.append('..')

from xym import XbpsRepository
from ratking import Runtime, Ratking

runtime = Runtime()

local_repo = XbpsRepository('/var/db/xbps/pkgdb-0.38.plist', is_repo=False)

local_repo.name = 'Installed packages'

runtime.ratking = Ratking(local_repo=local_repo)
runtime.exec = 'xym'
runtime.description = 'A X Binary Package System package manager, with additional version control'
runtime.home = '~/.config/xym'
runtime.ratking.add_repository(XbpsRepository('https://repo.voidlinux.eu/current/x86_64-repodata'), load=False)
runtime.main()