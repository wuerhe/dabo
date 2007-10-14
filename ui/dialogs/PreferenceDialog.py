# -*- coding: utf-8 -*-
import dabo
if __name__ == "__main__":
	dabo.ui.loadUI("wx")
from dabo.dLocalize import _
from dabo.ui.dialogs.HotKeyEditor import HotKeyEditor

dayMins= 24*60



class PreferenceDialog(dabo.ui.dOkCancelDialog):
	def _afterInit(self):
		self._includeDefaultPages = True
		self._includeFrameworkPages = False
		self.Size = (700, 600)
		self.AutoSize = False
		self.Caption = _("Preferences")
		# Set up a list of functions to call when the user clicks 'OK' to accept changes,
		# and one for functions to call when the user cancels.
		self.callOnAccept = []
		self.callOnCancel = []
		# Create a list of preference key objects that will be have their AutoPersist turned
		# off when the dialog is shown, and either canceled or persisted, depending
		# on the user's action.
		self.preferenceKeys = []
		super(PreferenceDialog, self)._afterInit()
	

	def addControls(self):
		"""Add the base PageList, and then delete this method from the 
		namespace. Users will customize with addCategory() and then 
		adding controls to the category page.
		"""
		self._addPages()
		dabo.ui.callAfter(self.update)
		self.layout()
		# Use this to 'delete' addControls() so that users don't try to use this method.
		self.addControls = None
	
	
	def _addPages(self):
		self.pglCategory = dabo.ui.dPageList(self, TabPosition="Left",
				ListSpacing=20)
		self.addPages()
		incl = self.pglCategory.PageCount == 0
		if incl or self.IncludeDefaultPages:
			self._addDefaultPages()
		if incl or self.IncludeFrameworkPages:
			self._addFrameworkPages()
		self.Sizer.append1x(self.pglCategory)
		self.layout()
	
	
	def addPages(self): pass
	
	
	def _onAcceptPref(self):
		"""This is called by the app when the user clicks the OK button. Every method in
		the callOnAccept list is called, followed by a call to the user-configurable 
		onAccept() method.
		"""
		for fnc in self.callOnAccept:
			fnc()
		# Call the user-configurable method
		self.onAcceptPref()
	
	
	def onAcceptPref(self):
		"""Override this for subclasses where you need separate OK processing."""
		pass
		

	def _onCancelPref(self):
		"""This is called by the app when the user clicks the Cancel button. Every method 
		in the callOnCancel list is called, followed by a call to the user-configurable 
		onCancel() method.
		"""
		for fnc in self.callOnCancel:
			fnc()
		# Call the user-configurable method
		self.onCancelPref()
	
	
	def onCancelPref(self):
		"""Override this for subclasses where you need separate Cancel processing."""
		pass
	
	
	def addCategory(self, category, pos=None):
		"""Adds a page to the main PageList control, sets the caption to the
		passed string, and returns a reference to the page. If the optional 'pos'
		parameter is passed, the page is inserted in that position; otherwise, it
		is appended after any existing pages.
		"""
		if pos is None:
			pos = self.pglCategory.PageCount
		return self.pglCategory.insertPage(pos, caption=category)
	
	
	def _addDefaultPages(self):
		"""Called when no other code exists to fill the dialog, or when
		the class's IncludeDefaultPages property is True.
		"""
		try:
			mb = self.Application.ActiveForm.MenuBar
			menuOK = True
		except:
			menuOK = False
		if menuOK:
			pm = self.PreferenceManager.menu
			self.preferenceKeys.append(pm)
			menuPage = self.pgMenuKeys = self.addCategory(_("Menu Keys"))
			self._selectedItem = None	
			menuPage.Sizer.Orientation = "H"
			tree = dabo.ui.dTreeView(menuPage, OnTreeSelection=self._onMenuTreeSelection)
			root = tree.setRootNode(_("Menu"))
			for mn in mb.Children:
				cap = self._cleanMenuCaption(mn.Caption, "&")
				prefcap = self._cleanMenuCaption(mn.Caption)
				nd = root.appendChild(cap)
				nd.pref = pm
				nd.hotkey = "n/a"
				nd.object = mn
				menukey = pm.get(prefcap)
				self._recurseMenu(mn, nd, menukey)
			menuPage.Sizer.append1x(tree, border=10)
			root.expand()
			
			sz = dabo.ui.dGridSizer(MaxCols=2, HGap=5, VGap=10)
			lbl = dabo.ui.dLabel(menuPage, Caption=_("Current Key:"))
			txt = dabo.ui.dTextBox(menuPage, ReadOnly=True, Alignment="Center",
					RegID="txtMenuCurrentHotKey")
			sz.append(lbl, halign="right")
			sz.append(txt, "x")
			sz.appendSpacer(1)
			btn = dabo.ui.dButton(menuPage, Caption=_("Set Key..."),
					OnHit=self._setHotKey, DynamicEnabled=self._canSetHotKey)
			sz.append(btn, halign="center")
			sz.appendSpacer(1)
			btn = dabo.ui.dButton(menuPage, Caption=_("Clear Key"),
					OnHit=self._clearHotKey, DynamicEnabled=self._canClearHotKey)
			sz.append(btn, halign="center")
			sz.setColExpand(True, 1)
			menuPage.Sizer.append1x(sz, border=10)


	def _recurseMenu(self, mn, nd, pref):
		""" mn is the menu; nd is the tree node for that menu; pref is the pref key for the menu."""
		for itm in mn.Children:
			native = True
			try:
				cap = self._cleanMenuCaption(itm.Caption, "&")
				prefcap = self._cleanMenuCaption(itm.Caption)
			except:
				# A separator line
				continue
			kidnode = nd.appendChild(cap)
			subpref = pref.get(prefcap)
			kidnode.pref = subpref
			if itm.Children:
				self._recurseMenu(itm, kidnode, subpref)
			else:
				kidnode.hotkey = itm.HotKey
				kidnode.object = itm

	
	def _onMenuTreeSelection(self, evt):
		self._selectedItem = nd = evt.selectedNode
		if nd.IsRootNode:
			return
		if nd.hotkey == "n/a":
			self.txtMenuCurrentHotKey.Value = ""
		else:
			self.txtMenuCurrentHotKey.Value = nd.hotkey
		self.update()
	
	
	def _setHotKey(self, evt):
		dlg = HotKeyEditor(self)
		itm = self._selectedItem
		dlg.setKey(itm.hotkey)
		dlg.show()
		if dlg.Accepted:
			hk = dlg.KeyText
			self.txtMenuCurrentHotKey.Value = itm.hotkey = itm.object.HotKey = hk
			itm.pref.setValue("hotkey", hk)
		dlg.release()


	def _canSetHotKey(self):
		itm = self._selectedItem
		return (itm is not None) and (itm.hotkey != "n/a")
	
	
	def _clearHotKey(self, evt):
		itm = self._selectedItem
		self.txtMenuCurrentHotKey.Value = itm.hotkey = itm.object.HotKey = None
		itm.pref.setValue("hotkey", None)
		

	def _canClearHotKey(self):
		itm = self._selectedItem
		return (itm is not None) and (itm.hotkey not in ("n/a", None))
	
	
	def _cleanMenuCaption(self, cap, bad=None):
		if bad is None:
			bad = "&. "
		ret = cap
		for ch in bad:
			ret = ret.replace(ch, "")
		return ret
	
	
	def _addFrameworkPages(self):
		"""Called when no other code exists to fill the dialog, or when
		the class's IncludeFrameworkPages property is True.
		"""
		wuPage = self.pgWebUpdate = self.addCategory(_("Web Update"))
		# Set the framework-level pref manager
		fp = self.Application._frameworkPrefs
		self.preferenceKeys.append(fp)
		sz = wuPage.Sizer = dabo.ui.dSizer("v")
		hsz = dabo.ui.dSizer("h")
		chkUpdateCheck = dabo.ui.dCheckBox(wuPage, OnHit=self.onChkUpdate, 
				Caption=_("Check for framework updates"), RegID="chkForWebUpdates",
				DataSource=fp, DataField="web_update", 
				ToolTipText="Does the framework check for updates?")
		btnCheckNow = dabo.ui.dButton(wuPage, Caption=_("Check now..."),
				OnHit=self.onCheckNow, ToolTipText="Check the Dabo server for updates")
		hsz.append(chkUpdateCheck, valign="middle")
		hsz.appendSpacer(8)
		hsz.append(btnCheckNow, valign="middle")
		sz.append(hsz, halign="center", border=20)
		
		radFrequency = dabo.ui.dRadioList(wuPage, Orientation="Vertical", 
				Caption=_("Check every..."), RegID="radWebUpdateFrequency", 
				Choices=[_("Every time an app is run"), _("Once a day"), _("Once a week"), _("Once a month")],
				Keys = [0, dayMins, dayMins*7,dayMins*30],
				ValueMode="Keys", DataSource=fp, DataField="update_interval",
				ToolTipText=_("How often does the framework check for updates?"),
				DynamicEnabled = lambda: self.chkForWebUpdates.Value)
		sz.append(radFrequency, halign="center")
	
	
	def onChkUpdate(self, evt):
		self.update()
		
		
	def onCheckNow(self, evt):
		ret = self.Application.checkForUpdates()
		if ret:
			dabo.ui.info(_("No updates are available now."), title=_("Web Updates"))
	
	def _getIncludeDefaultPages(self):
		return self._includeDefaultPages

	def _setIncludeDefaultPages(self, val):
		if self._constructed():
			self._includeDefaultPages = val
		else:
			self._properties["IncludeDefaultPages"] = val


	def _getIncludeFrameworkPages(self):
		return self._includeFrameworkPages

	def _setIncludeFrameworkPages(self, val):
		if self._constructed():
			self._includeFrameworkPages = val
		else:
			self._properties["IncludeFrameworkPages"] = val


	IncludeDefaultPages = property(_getIncludeDefaultPages, _setIncludeDefaultPages, None,
			_("""When True, the _addDefaultPages() method is called to add the common 
			Dabo settings. Default=True  (bool)"""))

	IncludeFrameworkPages = property(_getIncludeFrameworkPages, _setIncludeFrameworkPages, None,
			_("""When True, the _addFrameworkPages() method is called to add the common 
			Dabo settings. Default=False  (bool)"""))


if __name__ == "__main__":
	class TestForm(dabo.ui.dForm):
		def afterInit(self):
			lbl = dabo.ui.dLabel(self, Caption="Preference Manager Demo\n" +
				"Select 'Preferences' from the menu.", WordWrap=True)
			self.Sizer.append(lbl, halign="center", border=20)

	app = dabo.dApp(MainFormClass=TestForm)
	app.start()
	
