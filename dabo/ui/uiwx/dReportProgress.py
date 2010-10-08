# -*- coding: utf-8 -*-
import wx
import dabo
if __name__ == "__main__":
	dabo.ui.loadUI("wx")
from dabo.dLocalize import _
from dPanel import dPanel
from dGauge import dGauge
from dLabel import dLabel
from dButton import dButton


class dReportProgress(dPanel):
	def afterInit(self):
		ms = self.Sizer = dabo.ui.dBorderSizer(self, "v", DefaultBorder=5)
		self.gauge = dGauge(self, Size=(75,12))
		lblTitle = dLabel(self, Name="lblTitle", Caption="", FontBold=True)
		butCancel = dButton(self, Name="butCancelReportProgress", CancelButton=False,
				Caption="Cancel", Enabled=False, OnHit=self.onCancel)
		ms.append(lblTitle)
		ms.append(self.gauge, "expand")
		ms.append(butCancel, alignment="right")
		self.Visible = False

	def show(self):
		self.oldCancel = self.Form.FindWindowById(wx.ID_CANCEL)
		if self.oldCancel:
			self.oldCancelEnabled = self.oldCancel.Enabled
			self.oldCancel.Enabled = False
			self.oldCancel.CancelButton = False
		self.butCancelReportProgress.Enabled = True
		self.butCancelReportProgress.CancelButton = True
		self.Visible = True

	def hide(self):
		self.Visible = False
		self.butCancelReportProgress.Enabled = False
		self.butCancelReportProgress.CancelButton = False
		if self.oldCancel:
			if self.oldCancelEnabled:
				self.oldCancel.Enabled = True
			self.oldCancel.CancelButton = True

	def updateProgress(self, val, range_):
		self.gauge.Range = range_
		self.gauge.Value = val
		self.gauge.refresh()

	def onCancel(self, evt):
		evt.stop()  ## keep dialogs from automatically being closed.
		if not self.Visible:
			return
		self.ProcessObject.cancel()


	def _getCaption(self):
		return self.lblTitle.Caption

	def _setCaption(self, val):
		self.lblTitle.Caption = val
		self.fitToSizer()


	def _getProcessObject(self):
		self._processObject = getattr(self, "_processObject", None)
		return self._processObject

	def _setProcessObject(self, val):
		self._processObject = val



	Caption = property(_getCaption, _setCaption, None,
			_("""Specifies the caption of the progress bar."""))

	ProcessObject = property(_getProcessObject, _setProcessObject, None,
			_("""Specifies the object that is processing (a dReportWriter instance, for example)."""))


