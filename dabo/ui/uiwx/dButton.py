# -*- coding: utf-8 -*-
import wx
import dabo
import dabo.ui

if __name__ == "__main__":
	dabo.ui.loadUI("wx")

import dControlMixin as cm
from dabo.dLocalize import _
import dabo.dEvents as dEvents
from dabo.ui import makeDynamicProperty


class dButton(cm.dControlMixin, wx.Button):
	"""Creates a button that can be pressed by the user to trigger an action.

	Example:

	class MyButton(dabo.ui.dButton):
		def initProperties(self):
			self.Caption = "Press Me"

		def onHit(self, evt):
			self.Caption = "Press Me one more time"

	"""
	def __init__(self, parent, properties=None, attProperties=None, *args, **kwargs):
		self._baseClass = dButton
		preClass = wx.PreButton
		cm.dControlMixin.__init__(self, preClass, parent, properties, attProperties,  
				*args, **kwargs)


	def _initEvents(self):
		super(dButton, self)._initEvents()
		self.Bind(wx.EVT_BUTTON, self._onWxHit)
		
	
	def __onCancelButton(self, evt):
		# This callback exists for when the user presses ESC and this button
		# is the cancel button. Raise dEvents.Hit.
		self.raiseEvent(dEvents.Hit)


	# Property get/set/del methods follow. Scroll to bottom to see the property
	# definitions themselves.
	def _getCancelButton(self):
# 		try:
# 			return self.Parent._acceleratorTable["esc"] == self.__onCancelButton
# 		except KeyError:
# 			return False
		try:
			v = self._cancelButton
		except AttributeError:
			v = self._cancelButton = False
		return v


	def _setCancelButton(self, val):
		if self._constructed():
			## pkm: We can bind the key to self, Parent, or Form (or any object).
			##      If bound to self, the <esc> keypress will only fire the Hit
			##      when self has the focus. If bound to self.Parent, Hit will 
			##      fire when self.Parent or any of its children has the focus.
			##      If bound to self.Form, Hit will fire whenever <esc> is pressed.
			##      I'm making the decision to bind it to self.Form, even though
			##      self.Parent is also a valid choice.
			### egl: changed the binding on OS X to the form. Parent just doesn't work.
			### pkm: followed suit with GTK (we should test Win too).
			target = self.Parent
			if self.Application.Platform in ("Mac", "GTK"):
				target = self.Form
			if val:
				target.bindKey("esc", self.__onCancelButton)
				self.SetId(wx.ID_CANCEL)
			else:
				target.unbindKey("esc")
				self.SetId(wx.NewId())
			self._cancelButton = val
		else:
			self._properties["CancelButton"] = value


	def _getDefaultButton(self):
		try:
			v = self._defaultButton
		except AttributeError:
			v = self._defaultButton = False
		return v

	def _setDefaultButton(self, value):
		if self._constructed():
			if value:
				# Need to unset default from any other buttons:
				for child in self.Parent.Children:
					if child is self:
						continue
					try:
						db = child.DefaultButton
					except AttributeError:
						db = False
					if db:
						child.DefaultButton = False
				# Now set it for this button
				self.SetDefault()
			else:
				# No wx-way to unset default button. Probably a rare need, anyway.
				# One idea would be to create a hidden button, set default to it,
				# and then destroy it.
				pass
			self._defaultButton = value
		else:
			self._properties["DefaultButton"] = value


	# Property definitions:
	CancelButton = property(_getCancelButton, _setCancelButton, None,
			_("Specifies whether this command button gets clicked on -Escape-."))
						
	DefaultButton = property(_getDefaultButton, _setDefaultButton, None, 
			_("Specifies whether this command button gets clicked on -Enter-."))
		
		
	DynamicCancelButton = makeDynamicProperty(CancelButton)
	DynamicDefaultButton = makeDynamicProperty(DefaultButton)



class _dButton_test(dButton):
	def initProperties(self):
		self.Caption = "You better not push me"
		self.FontSize = 8
		self.Width = 223

	def onContextMenu(self, evt):
		print "context menu"

	def onMouseRightClick(self, evt):
		print "right click"

	def onHit(self, evt):
		self.ForeColor = "purple"
		self.FontBold = True
		self.FontItalic = True
		self.Caption = "Ok, you cross this line, and you die."
		self.Width = 333

if __name__ == "__main__":
	import test
	test.Test().runTest(_dButton_test)
