import wx
import dabo.ui
from uiApp import uiApp

uiType = {'shortName': 'wx', 'moduleName': 'uiwx', 'longName': 'wxPython'}

# The wx app object must be created before working with anything graphically.
# As we don't want to require people to use dApp, and as dApp is the one that
# creates wx.App (via uiApp), let's create an initial app object just to get
# it loaded and make wx happy. It'll get replaced when dApp instantiates.
#app = wx.PySimpleApp()

# Import dPemMixin first, and then manually put into dabo.ui module. This is
# because dControlMixin, which is in dabo.ui, descends from dPemMixin, which 
# is in dabo.ui.uiwx.
from dPemMixin import dPemMixin
dabo.ui.dPemMixin = dPemMixin

# Import into public namespace:
from dAbout import dAbout
from dBox import dBox
from dBitmapButton import dBitmapButton
from dCheckBox import dCheckBox
from dComboBox import dComboBox
from dCommandButton import dCommandButton
from dDataNavForm import dDataNavForm
from dDateTextBox import dDateTextBox
from dDropdownList import dDropdownList
from dDialog import dDialog
from dEditBox import dEditBox
from dForm import dForm
from dFormDataNav import dFormDataNav
from dFormMain import dFormMain
from dGauge import dGauge
from dGrid import dGrid
from dGridDataNav import dGridDataNav
from dLabel import dLabel
from dLine import dLine
from dListbook import dListbook
from dLogin import dLogin
from dMainMenuBar import dMainMenuBar
from dMenuBar import dMenuBar
from dMenu import dMenu
from dRadioGroup import dRadioGroup
from dPanel import dPanel
from dPanel import dScrollPanel
from dPageFrame import dPageFrame
from dPage import dPage
from dSlider import dSlider
from dSpinner import dSpinner
from dTextBox import dTextBox
from dTimer import dTimer
from dToggleButton import dToggleButton
from dTreeView import dTreeView


# Tell Dabo Designer what classes to put in the selection menu:
__dClasses = [dBox, dBitmapButton, dBox, dCheckBox, dCommandButton,  
		dDateTextBox, dDropdownList, dEditBox, dForm, dFormDataNav, dFormMain, 
		dGauge, dLabel, dLine, dListbook, dPanel, dPageFrame, dPage, 
		dRadioGroup, dScrollPanel, dSlider, dSpinner, dTextBox, dToggleButton]

daboDesignerClasses = []
for __classRef in __dClasses:
	__classDict = {}
	__classDict['class'] = __classRef
	__classDict['name'] = __classRef.__name__
	__classDict['prompt'] = "%s&%s" % (__classRef.__name__[0], __classRef.__name__[1:])
	__classDict['topLevel'] = __classRef.__name__.find('Form') >= 0
	__classDict['doc'] = __classRef.__doc__
	daboDesignerClasses.append(__classDict)


def getEventData(wxEvt):
	ed = {}
	
	if isinstance(wxEvt, wx.KeyEvent) or isinstance(wxEvt, wx.MouseEvent):
		ed["mousePosition"] = wxEvt.GetPositionTuple()
		ed["altDown"] = wxEvt.AltDown()
		ed["commandDown"] = wxEvt.CmdDown()
		ed["controlDown"] = wxEvt.ControlDown()
		ed["metaDown"] = wxEvt.MetaDown()
		ed["shiftDown"] = wxEvt.ShiftDown()

	if isinstance(wxEvt, wx.KeyEvent):
		ed["keyCode"] = wxEvt.GetKeyCode()
		ed["rawKeyCode"] = wxEvt.GetRawKeyCode()
		ed["rawKeyFlags"] = wxEvt.GetRawKeyFlags()
		ed["unicodeChar"] = wxEvt.GetUniChar()
		ed["unicodeKey"] = wxEvt.GetUnicodeKey()
		ed["hasModifiers"] = wxEvt.HasModifiers()

	return ed
