from turbogears.database import PackageHub
from sqlobject import *

hub = PackageHub('swi')
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass

