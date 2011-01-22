# -*- coding: utf-8 -*-
import wx

import dabo, dabo.ui
dabo.ui.loadUI("wx")

import dTextBoxMixin as tbm
from dabo.dLocalize import _
import dabo.dEvents as dEvents
from dabo.ui import makeDynamicProperty

class dSearchBox(tbm.dTextBoxMixin, wx.SearchCtrl):
	"""Creates a text box for editing one line of string data."""
	def __init__(self, parent, properties=None, attProperties=None, *args, **kwargs):
		self._baseClass = dSearchBox

		self._list = []
		self._cancelVisible = False
		self._searchVisible = True

		preClass = wx.PreSearchCtrl
		tbm.dTextBoxMixin.__init__(self, preClass, parent, properties=properties,
				attProperties=attProperties, *args, **kwargs)

	def _initEvents(self):
		super(dSearchBox, self)._initEvents()
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.__onWxSearchBtnPressed)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.__onWxCancelBtnPressed)


	#handle events
	def __onWxSearchBtnPressed(self, evt):
		self.raiseEvent(dEvents.SearchButtonClicked, evt)

	def __onWxCancelBtnPressed(self, evt):
		self.raiseEvent(dEvents.SearchCancelButtonClicked, evt)


	#private methods
	def _setupMenuFromList(self, valueList):
		menu = dabo.ui.dMenu()
		for value in valueList:
			if not type(value) in (str, unicode):
				raise ValueError("All elements in the List must be strings")
			else:
				menu.append(value)

		self.SetMenu(menu)


	#property getters and setters
	def _getCancelButtonVisible(self):
		return self._cancelVisible

	def _setCancelButtonVisible(self, val):
		if self._constructed():
			if val:
				self._cancelVisible = True
			else:
				self._cancelVisible = False

			self.ShowCancelButton(self._cancelVisible)
		else:
			self._properties["CancelButtonVisible"] = val


	#I thought a List was more appropriate then a dMenu.  You can still use
	#the Menu property but I wanted this to be a little more Dabo like. -nwl
	def _getList(self):
		return self._list

	def _setList(self, val):
		if self._constructed():
			if val == None or val == [] or val == ():
				self._list = []
				self.SetMenu(None)
			elif type(val) in (list, tuple):
				self._setupMenuFromList(val)
				self._list = val
			else:
				raise TypeError("List must be either a tuple, list, or None")
		else:
			self._properties["List"] = val

	def _getMenu(self):
		return self.GetMenu()


	def _getSearchButtonVisible(self):
		return self._searchVisible

	def _setSearchButtonVisible(self, val):
		if self._constructed():
			if val:
				self._searchVisible = True
			else:
				self._searchVisible = False

			self.ShowSearchButton(self._searchVisible)
		else:
			self._properties["SearchButtonVisible"] = val


	#Property definitions
	CancelButtonVisible = property(_getCancelButtonVisible, _setCancelButtonVisible, None,
		_("Tells whether or not the cancel button is visible (bool)"))

	List = property(_getList, _setList, None,
		_("A dropdown list that appears right below the search button (list)"))

	Menu = property(_getMenu, None, None,
		_("Menu used to display the controls.  Generated by List (dMenu)"))

	SearchButtonVisible = property(_getSearchButtonVisible, _setSearchButtonVisible, None,
		_("Tells whether or not the search button is visible (bool)"))



if __name__ == "__main__":
	import test
	import datetime

	# This test sets up several textboxes, each editing different data types.
	class TestBase(dSearchBox):
		def initProperties(self):
			self.super()
			self.LogEvents = ["ValueChanged","searchButtonClicked","SearchCancelButtonClicked"]
			self.CancelButtonVisible = True
			self.SearchButtonVisible = True
			self.List = ("item 1", "item 2", "item 3")

		def onValueChanged(self, evt):
			if self.IsSecret:
				print "%s changed, but the new value is a secret!" % self.Name
			else:
				print "%s.onValueChanged:" % self.Name, self.Value, type(self.Value)

		def onSearchButtonClicked(self, evt):
			print "you pressed the search button"

		def onSearchCancelButtonClicked(self, evt):
			print "you pressed the cancel button"


	class IntText(TestBase):
		def afterInit(self):
			self.Value = 23

	class FloatText(TestBase):
		def afterInit(self):
			self.Value = 23.5
			self.List = ['changed item 1', 'changed item 2']

	class BoolText(TestBase):
		def afterInit(self):
			self.Value = False

	class StrText(TestBase):
		def afterInit(self):
			self.Value = "Lunchtime"

	class PWText(TestBase):
		def __init__(self, *args, **kwargs):
			kwargs["PasswordEntry"] = True
			super(PWText, self).__init__(*args, **kwargs)
		def afterInit(self):
			self.Value = "TopSecret!"

	class DateText(TestBase):
		def afterInit(self):
			self.Value = datetime.date.today()
			self.List = ['historyItem 1', 'historyItem 2']

	class DateTimeText(TestBase):
		def afterInit(self):
			self.Value = datetime.datetime.now()

	testParms = [IntText, FloatText, StrText, PWText, BoolText, DateText, DateTimeText]

	import decimal
	class DecimalText(TestBase):
		def afterInit(self):
			self.Value = decimal.Decimal("23.42")
	testParms.append(DecimalText)


	test.Test().runTest(testParms)
