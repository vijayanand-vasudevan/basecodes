
import pandas as pd
from enum import Enum, auto
from abc import ABC, abstractmethod
import gc

from pure_tech.core.tools import Classes, FileSys
from pure_tech.core.Config import Config, ENV
from pure_tech.core.App import App
from pure_tech.core.Chart import Chart, ChartTypes
from pure_tech.dal.MarketData import *
from pure_tech.core.Logger import Logger

logger = Logger(__file__)

class GUIType(Enum):
    
    view = auto()
    text = auto()
    combo = auto()
    selMulti = auto()
    datePicker = auto()
    select = auto()
    checkbox = auto()
    radio = auto()
    button = auto()
    toggle = auto()
    tab = auto()
    accordion = auto()

    def all():
        return [i[1].name for i in GUIType.__members__.items()]

    def toEnum(s, defVal=None):
        for e in GUIType.__members__.items():
            if e[1].name.lower()==s.lower():
                return e[1]
        return defVal

class GUI(ABC):

    def __init__(self, name, dctArgs=None):
        self.name = name
        self.widgets = {}
        self.charts = {}
        self.chartColors = {}
        self.chartTypes = {}
        self.dctArgs = dctArgs
    
    @abstractmethod
    def addNewDisp(self, name):
        pass

    @abstractmethod
    def setupLogger(self):
        pass

    def build(self, components):
        gvTypes = [None] * (len(GUIType.all())+1)
        gvTypes[GUIType.view.value] = self.view
        gvTypes[GUIType.text.value] = self.textInput
        gvTypes[GUIType.select.value] = self.select
        gvTypes[GUIType.selMulti.value] = self.selMulti
        gvTypes[GUIType.combo.value] = self.combo
        gvTypes[GUIType.datePicker.value] = self.selDates
        gvTypes[GUIType.checkbox.value] = self.checkbox
        gvTypes[GUIType.button.value] = self.button
        gvTypes[GUIType.toggle.value] = self.toggles
        gvTypes[GUIType.tab.value] = self.tab
        gvTypes[GUIType.accordion.value] = self.accordion
        for c in components:
            cv = components[c]
            if cv['type'] in [GUIType.text]:
                gvTypes[cv['type'].value](c, cv['desc'], cv['defVal'] if 'defVal' in cv else None)
            elif cv['type'] in [GUIType.button]:
                gvTypes[cv['type'].value](c, cv['desc'],oper=cv['oper'])
            elif cv['type'] in [GUIType.view]:
                gvTypes[cv['type'].value](c)
            elif 'options' in cv:
                gvTypes[cv['type'].value](c, cv['desc'], options=cv['options'], 
                    defVal=cv['defVal'] if 'defVal' in cv else None, oper=cv['oper'] if 'oper' in cv else None)
            else:
                gvTypes[cv['type'].value](c, cv['desc'], 
                    defVal=cv['defVal'] if 'defVal' in cv else None, oper=cv['oper'] if 'oper' in cv else None)

    @abstractmethod
    def log(self,l,clear=False):
        pass

    def get(self,id):
        if id in self.widgets:
            return self.widgets[id]
        return None

    @abstractmethod
    def _showWidget(self,id,widget_,show=True):
        pass

    def showWidget(self,id,show=True):
        if id in self.widgets:
            wv = self.widgets[id]
            self._showWidget(id, wv, show=show)

    @abstractmethod
    def _setOptions(self,id,widget_,vals):
        pass

    def setOptions(self,id,vals):
        if id in self.widgets:
            wv = self.widgets[id]
            self._setOptions(id, wv, vals)
        else:
            raise Exception( f"Can't find the widget {id}" )

    def checkAndRaise(self,id,msg=""):
        if id in self.widgets:
            raise Exception(f"Widget with key already exists {id} {msg}")

    @abstractmethod
    def accordion(self,id,children,oper=None):
        pass

    @abstractmethod
    def tab(self,id,children,oper=None):
        pass

    @abstractmethod
    def _setVal(self,id,widget_,vals):
        pass

    def setVal(self,id,vals):
        if id in self.widgets:
            wv = self.widgets[id]
            self._setVal(id,wv,vals)
        else:
            raise Exception( f"Can't find the widget {id}" )

    @abstractmethod
    def _getVal(self,id,widget_):
        pass

    def getVal(self,id):
        if id in self.widgets:
            wv = self.widgets[id]
            return self._getVal(id,wv)
        raise Exception( f"Can't find the widget {id}" )

    @abstractmethod
    def radio(self,id,desc,options,defVal=None,oper=None):
        pass

    @abstractmethod
    def combo(self,id,desc,options,defVal=None,oper=None):
        pass

    @abstractmethod
    def button(self,id,desc,oper):
        pass

    @abstractmethod
    def toggles(self,id,desc,options,oper=None):
        pass

    @abstractmethod
    def checkbox(self,id,desc,defVal=False,oper=None):
        pass

    @abstractmethod
    def selDates(self,id,desc,defVal=None,oper=None):
        pass

    @abstractmethod
    def uploadFile(self,id,desc,fileType=None):
        pass

    @abstractmethod
    def view(self,id):
        pass

    @abstractmethod
    def select(self,id,desc,options=[],defVal=None,oper=None):
        pass

    @abstractmethod
    def selMulti(self,id,desc,options=[],defVal=[],oper=None):
        pass

    @abstractmethod
    def textInput(self,id,desc,defVal=None,h=None,w=None):
        pass

    @abstractmethod
    def label(self,id,value):
        pass

    @abstractmethod
    def refresh(self,disps=None):
        pass

    @abstractmethod
    def clearSelected(self,id):
        pass

    @abstractmethod
    def hBox(self,ids):
        pass

    @abstractmethod
    def vBox(self,ids):
        pass

    def isSimple(jo):
        if type(jo) not in [dict, list, set]:
            return True
        if type(jo) in [list, set]:
            return all([type(j1) not in [dict, list, set] for j1 in jo])
        return False
    
    @abstractmethod
    def setView(self,disps={},top=None):
        pass

    @abstractmethod
    def showGrid(self,id,df):
        pass

    @abstractmethod
    def showLink(self,id,link,linkTitle):
        pass

    def hasChartType(self,fld):
        return (fld in self.chartTypes)

    def setColorsAndTypes(self,fld,typ,color=None,mode=None,width=None,symbol=None):
        self.chartColors[fld] = color
        self.chartTypes[fld] = [typ]
        if mode is not None:
            self.chartTypes[fld] = [typ, mode, symbol, color, width]

    def clearCharts(self):
        del self.charts
        self.charts = {}

    def clearChart(self,id):
        if id in self.charts:
            del self.charts[id]

    def clearView(self,id):
        if id in self.widgets:
            del self.widgets[id]
            self.view(id)

    @abstractmethod
    def _displayChart(self,id,widget_,chartG_):
        pass

    def addChart(self,id,df,x,y1,y2, ch=None, row=1, col=1, desc=None,x1T=None,y1T=None,y2T=None,legendGroup=None):
        if ch is None and id not in self.charts:
            ch = Chart()
            self.charts[id] = ch
        elif id in self.charts and ch is None:
            ch = self.charts[id]
        ch.plot(df, x, y1, y2, y1Type=self.chartTypes, y2Type=self.chartTypes, title=desc, row=row, col=col, xT=x1T, y1T=y1T, y2T=y2T,
            showLegend=True, colors=self.chartColors, legendGroup=legendGroup)
        return ch

    def plotChart(self,id,node,desc=None,sharedX=False,sharedY=False,width=None,height=None,props=None):
        #print( self.charts )
        if node not in self.widgets:
            raise Exception( f"chart cannot be placed in widget {node} doesn't exist" )
        if id in self.charts:
            ch = self.charts[id]
            ch.final(desc, w=width, h=height,sharedX=sharedX,sharedY=sharedY,props=props)
            if node in self.widgets:
                self._displayChart(node, self.widgets[node], ch)
        else:
            raise Exception( f"Error chart {id} not found" )

global topUI
global pageUI
global topMenus
global topMenuKeys
global pDisp

topUI = None
pageUI = None
gPrevTop = None
gOldGUI = None
topMenus = None
topMenuKeys = []
pDisp = None

def onClickSubMenu(topMenu, subMenu,*args):
    global topUI
    global pageUI
    global topMenus
    global gPrevTop
    global gOldGUI
    if gPrevTop != (topMenu, subMenu):
        tm = topMenu
        lv = topMenus[tm][subMenu]
        if pageUI is not None:
            del pageUI
            pageUI = None
            print( 'Deleting old GUI object' )
            gc.collect()
        mode = Config.get("UI.type")
        pageUI  = Classes.getObject( mode, superClass=GUI, objKey=None, name=f"{topMenu}.{subMenu}", dctArgs={'disp':pDisp} )
        pageUI.setupLogger()
        print( f"{mode=} {topMenu=}.{subMenu=} {pageUI} module=[{lv['module']}.{lv['function']}]" )
        pageUI = Classes.callFunc( f"{lv['module']}.{lv['function']}", pageUI )
        gPrevTop = (topMenu, subMenu)

def onSubMenu(*args):
    lo=args[0]
    glv = 'new'
    global topUI
    logger.info(args)
    if 'name' in lo and lo['name']=='value':
        tmv = topUI.get('tab.1')
        tm = topMenuKeys[tmv.selected_index]
        onClickSubMenu(tm, lo[glv])

def genMainMenu():
    global pageUI
    global topUI
    global topMenus
    global topMenuKeys
    global pDisp

    uiCfg = Config.get( "UI" )
    if uiCfg is not None:
        mode = uiCfg.get("type")
    
        topUI = Classes.getObject( mode, superClass=GUI, objKey=None, name=mode )
        topUI.setupLogger()
        pDisp = topUI.addNewDisp('views')
    
        topMenus = Config.get('menus').asDict()
    
        dct = {'h.1':{'tab.1':{}}}
        for k in topMenus:
            topMenuKeys.append(k)
            topUI.toggles(k,k,(topMenus[k].keys()),onSubMenu)
            dct['h.1']['tab.1'][k] = k
    
        topUI.refresh(dct)
    else:
        print( "Unable to start UI" )
    return True

def runMenu():
    cfgFile = ENV.get('CONFIG_FILE')
    env = ENV.get('CONFIG_ENV')
    if env is None or cfgFile is None:
        raise Exception( f"CONFIG_ENV and CONFIG_FILE variable has to be setup properly both are mandatory" )
    App.ignoreAppIDCheck=True
    App.noAppStopAlerts=True
    if App.init({},inArgs=['--env',env,'--config',cfgFile,'--silent','1']):
        Config.loadConnections(App.env)
        App.start(genMainMenu)


