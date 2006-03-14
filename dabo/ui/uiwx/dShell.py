import __builtin__
import wx
import wx.py
from wx.py import pseudo
import dabo
import dabo.dEvents as dEvents
from dabo.dLocalize import _
from dSplitForm import dSplitForm
from dabo.ui import makeDynamicProperty

dabo.ui.loadUI("wx")

class dShell(dSplitForm):
	def _onDestroy(self, evt):
		__builtin__.raw_input = self._oldRawInput

	def _afterInit(self):
		self._sashPct = 0.6

		super(dShell, self)._afterInit()

		# PyShell sets the raw_input function to a function of PyShell,
		# but doesn't set it back on destroy, resulting in errors later
		# on if something other than PyShell asks for raw_input (pdb, for
		# example).
		self._oldRawInput = __builtin__.raw_input
		self.bindEvent(dabo.dEvents.Destroy, self._onDestroy)

		splt = self.splitter
		splt.MinimumPanelSize = 80
		splt.unbindEvent()
		self.Orientation = "H"
		self.unsplit()
		self._splitState = False
		self.MainSplitter.bindEvent(dEvents.SashDoubleClick, 
				self.sashDoubleClick)
		self.MainSplitter.bindEvent(dEvents.SashPositionChanged, 
				self.sashPosChanged)
		
		cp = self.CmdPanel = self.Panel1
		op = self.OutPanel = self.Panel2
		cp.unbindEvent(dEvents.ContextMenu)
		op.unbindEvent(dEvents.ContextMenu)
		
		cp.Sizer = dabo.ui.dSizer()
		op.Sizer = dabo.ui.dSizer()
		self.shell = wx.py.shell.Shell(self.CmdPanel)
		cp.Sizer.append1x(self.shell)
		self.shell.Bind(wx.EVT_RIGHT_UP, self.shellRight)

		# create the output control
		outControl = dabo.ui.dEditBox(op, RegID="edtOut", 
				ReadOnly = True)
		op.Sizer.append1x(outControl)
		outControl.bindEvent(dEvents.MouseRightDown, 
				self.outputRightDown)
		
		self._stdOut = self.shell.interp.stdout
		self._stdErr = self.shell.interp.stderr
		self._pseudoOut = pseudo.PseudoFileOut(write=self.appendOut)
		self._pseudoErr = pseudo.PseudoFileOut(write=self.appendOut)
		self.SplitState = True
		
		
		# Make 'self' refer to the calling form, or this form if no calling form.
		if self.Parent is None:
			ns = self
		else:
			ns = self.Parent
		self.shell.interp.locals['self'] = ns

		self.Caption = _("dShell: self is %s") % ns.Name
		self.setStatusText(_("Use this shell to interact with the runtime environment"))
		self.fillMenu()
		self.shell.SetFocus()
		
	
	def appendOut(self, tx):
		ed = self.edtOut
		ed.Value += tx
		endpos = ed.GetLastPosition()
		# Either of these commands should scroll the edit box
		# to the bottom, but neither do (at least on OS X) when 
		# called directly or via callAfter().
		dabo.ui.callAfter(ed.ShowPosition, endpos)
		dabo.ui.callAfter(ed.SetSelection, endpos, endpos)


	def outputRightDown(self, evt):
		pop = dabo.ui.dMenu()
		pop.append(_("Clear"), bindfunc=self.onClearOutput)
		self.showContextMenu(pop)
		evt.stop()
	
	
	def onClearOutput(self, evt):
		self.edtOut.Value = ""
	
	
	def shellRight(self, evt):
		pop = dabo.ui.dMenu()
		if self.SplitState:
			pmpt = _("Unsplit")
		else:
			pmpt = _("Split")
		pop.append(pmpt, bindfunc=self.onSplitContext)
		self.showContextMenu(pop)
		evt.StopPropagation()
		

	def onSplitContext(self, evt):
		self.SplitState = (evt.EventObject.Caption == _("Split"))
		evt.stop()
		
		
	def onResize(self, evt):
		self.SashPosition = self._sashPct * self.Height
	

	def sashDoubleClick(self, evt):
		# We don't want the window to unsplit
		evt.stop()
		
		
	def sashPosChanged(self, evt):
		self._sashPct = float(self.SashPosition) / self.Height
		
		
	def fillMenu(self):
		viewMenu = self.MenuBar.getMenu(_("View"))
		if viewMenu.Children:
			viewMenu.appendSeparator()
		viewMenu.append(_("Zoom &In\tCtrl+="), bindfunc=self.onViewZoomIn, 
				bmp="zoomIn", help=_("Zoom In"))
		viewMenu.append(_("&Normal Zoom\tCtrl+/"), bindfunc=self.onViewZoomNormal, 
				bmp="zoomNormal", help=_("Normal Zoom"))
		viewMenu.append(_("Zoom &Out\tCtrl+-"), bindfunc=self.onViewZoomOut, 
				bmp="zoomOut", help=_("Zoom Out"))
		editMenu = self.MenuBar.getMenu(_("Edit"))
		if editMenu.Children:
			editMenu.appendSeparator()
		editMenu.append(_("Clear O&utput\tCtrl+Back"), 
				bindfunc=self.onClearOutput, help=_("Clear Output Window"))
		
		
	def onViewZoomIn(self, evt):
		self.shell.SetZoom(self.shell.GetZoom()+1)

	def onViewZoomNormal(self, evt):
		self.shell.SetZoom(0)

	def onViewZoomOut(self, evt):
		self.shell.SetZoom(self.shell.GetZoom()-1)
	

	def _getSplitState(self):
		return self._splitState

	def _setSplitState(self, val):
		if self._splitState != val:
			self._splitState = val
			if val:
				self.split()
				self.shell.interp.stdout = self._pseudoOut
				self.shell.interp.stderr = self._pseudoErr
			else:
				self.unsplit()
				self.shell.interp.stdout = self._stdOut
				self.shell.interp.stderr = self._stdErr
			

	SplitState = property(_getSplitState, _setSplitState, None,
			_("""Controls whether the output is in a separate pane (default) 
			or intermixed with the commands.  (bool)"""))
	DynamicSplitState = makeDynamicProperty(SplitState)
	
		

def main():
	app = dabo.dApp()
	app.MainFormClass = dShell
	app.setup()
	app.start()

if __name__ == "__main__":
	main()
