# -*- coding: utf-8 -*-
import wx
import dabo
import dabo.ui

if __name__ == "__main__":
	import dabo.ui
	dabo.ui.loadUI("wx")
	if __package__ is None:
		import dabo.ui.uiwx
		__package__ = "dabo.ui.uiwx"

from . import controlmixin as cm
from . import imagemixin as dim
from dabo.dLocalize import _
from . import icons
from dabo.ui import makeDynamicProperty


class dBitmap(cm.dControlMixin, dim.dImageMixin, wx.StaticBitmap):
	"""Creates a simple bitmap control to display images on your forms."""
	def __init__(self, parent, properties=None, attProperties=None, *args, **kwargs):
		self._baseClass = dBitmap
		preClass = wx.StaticBitmap
		picName = self._extractKey((kwargs, properties, attProperties), "Picture", "")

		dim.dImageMixin.__init__(self)
		cm.dControlMixin.__init__(self, preClass, parent, properties=properties,
				attProperties=attProperties, *args, **kwargs)

		if picName:
			self.Picture = picName



class _dBitmap_test(dBitmap):
	def initProperties(self):
		self.Picture = "daboIcon016"
#		self.Size = (40,30)

if __name__ == "__main__":
	from . import test
	test.Test().runTest(_dBitmap_test)
