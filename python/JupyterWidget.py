from ipywidgets import interact, HBox, VBox, Output, HTML, Layout, widgets
from IPython.display import Javascript, FileLink, FileLinks

from pure_tech.core.Logger import WidgetLog
from pure_tech.core.Chart import Chart, ChartTypes
import pandas as pd

from bqplot import LinearScale, ColorScale
from ipydatagrid import DataGrid, BarRenderer

from IPython.display import display, clear_output
import plotly.offline as pyo
import plotly.graph_objs as go
# Set notebook mode to work in offline
pyo.init_notebook_mode()

from pure_tech.core.Config import Config, ENV
from pure_tech.dal.MarketData import *
from ipywidgets import Box

from enum import Enum, auto

from pure_tech.core.GUI import *

class JupyterWidget(GUI):
    
    def __init__(self, name, dctArgs=None):
        super().__init__(name, dctArgs)
        disp = dctArgs['disp'] if dctArgs is not None and 'disp' in dctArgs else None
        self.hDisp = display(display_id=self.name) if disp is None else disp
        self.supportingDisp = None
    
    def addNewDisp(self, name):
        self.supportingDisp = display(display_id=name)
        return self.supportingDisp

    def setupLogger(self):
        self.view('log')

    def __del__(self):
        self.log( f'clearing out GUI loaders {self.name}' )
        with self.hDisp:
            clear_output()

    def log(self,l,clear=False):
        o3 = self.widgets['log'] if 'log' in self.widgets else None
        if o3 is None:
            #print(l)
            return
        with o3:
            if clear:
                o3.clear_output()
            display(l)

    def _showWidget(self,id,widget_,show=True):
        _widget.layout.visibility = 'visible' if show else 'hidden'

    def _setOptions(self,id,widget_,vals):
        if type(widget_) in [widgets.Select, widgets.SelectMultiple]:
            widget_.options = vals
        else:
            widget_.value = vals

    def accordion(self,id,children,oper=None):
        self.checkAndRaise(id)
        wv = widgets.Accordion(children = [self.widgets[children[i]] for i in children.keys()] )
        wv.titles = list(children.keys())
        self.widgets[id] = wv
        if oper is not None:
            wv.observe(oper,'value')
        return wv

    def tab(self,id,children,oper=None):
        self.checkAndRaise(id)
        wv = widgets.Tab()
        wv.children = [self.widgets[children[i]] for i in children.keys()]
        wv.titles = list(children.keys())
        self.widgets[id] = wv
        if oper is not None:
            wv.observe(oper)
        return wv

    def _setVal(self,id,widget_,vals):
        widget_.value = vals

    def _getVal(self,id,widget_):
        return widget_.value

    def radio(self,id,desc,options,defVal=None,oper=None):
        wv = widgets.RadioButtons(description = desc, options=options, value=defVal)
        wv.on_click(oper)
        self.widgets[id] = wv
        return wv

    def combo(self,id,desc,options,defVal=None,oper=None):
        wv = widgets.Dropdown(description = desc, options=options, value=defVal)
        wv.on_click(oper)
        self.widgets[id] = wv
        return wv

    def button(self,id,desc,oper):
        wv = widgets.Button(description = desc)
        wv.on_click(oper)
        self.widgets[id] = wv
        return wv

    def uploadFile(self,id,desc,fileType=None):
        wv = widgets.FileUpload(accept=fileType, multiple=True)
        self.widgets[id] = wv
        return wv

    def toggles(self,id,desc,options,oper=None):
        wv = widgets.ToggleButtons(options=options,description=desc,
            disabled=False,button_style='')
        self.widgets[id] = wv
        wv.selected_index=None
        if oper is not None:
            wv.observe(oper,'value')
        return wv

    def checkbox(self,id,desc,defVal=False,oper=None):
        wv = widgets.Checkbox(value=defVal, description=desc,disabled=False)
        if oper is not None:
            wv.observe(oper,'value')
        self.widgets[id] = wv
        return wv

    def selDates(self,id,desc,defVal=None,oper=None):
        wv = widgets.DatePicker(description=desc,disabled=False,value=defVal)
        wv.add_class('dateMinMaxSet')
        if oper is not None:
            wv.observe(oper,'value')
        self.widgets[id] = wv

    def view(self,id):
        wv = Output(layout=Layout(layout={'border':'1px solid black','overflow_x':'auto'}))
        self.widgets[id] = wv
        return wv

    def select(self,id,desc,options=[],defVal=None,oper=None):
        wv = widgets.Select(options=options,description=desc,disabled=False,value=defVal)
        if oper is not None:
            wv.observe(oper)
        self.widgets[id]=wv
        return wv

    def selMulti(self,id,desc,options=[],defVal=[],oper=None):
        wv = widgets.SelectMultiple(options=options,description=desc,disabled=False,value=defVal)
        if oper is not None:
            wv.observe(oper)
        self.widgets[id]=wv
        return wv

    def textInput(self,id,desc,defVal=None,h=None,w=None):
        layout=Layout() if h is None and w is None else Layout(height=h,width=w)
        wv = widgets.Textarea(description=desc,value=defVal,layout=layout)
        self.widgets[id] = wv
        return wv

    def label(self,id,value):
        wv = self.view(id)
        with wv:
            display(value)

    def refresh(self,disps=None):
        script = Javascript("\
                const query = '.dateMinMaxSet > input:first-of-type'; \
                document.querySelector(query).setAttribute('min', minDt); \
                document.querySelector(query).setAttribute('max', maxDt); \
                ")
        if disps is not None:
            self.disps = disps
        else:
            disps = self.disps
        x=self.setView(disps)
        self.hDisp.update(script)
        self.hDisp.update(x)

    def clearSelected(self,id):
        wv = self.widgets[id]
        if type(wv)==widgets.SelectMultiple:
            wv.value = []
        else:
            wv.value = None

    def hBox(self,ids):
        return HBox([self.widgets[i] for i in ids if i in self.widgets])

    def vBox(self,ids):
        return VBox([self.widgets[i] for i in ids if i in self.widgets])

    def setView(self,disps={},top=None):
        hs = []
        vs = []
        tlv = 'v.>>' if top is None else top
        for lv in disps:
            dvs = disps[lv]
            if lv.startswith('tab.'):
                hs.append(self.tab(lv,dvs))
            elif GUI.isSimple(dvs):
                if tlv.startswith('h.'):
                    hs.append(self.hBox(dvs) if lv.startswith('h.') else self.vBox(dvs))
                else:
                    vs.append(self.hBox(dvs) if lv.startswith('h.') else self.vBox(dvs))
            else:
                if tlv.startswith('h.'):
                    hs.append(self.setView(dvs,top=lv))
                else:
                    vs.append(self.setView(dvs,top=lv))
        if len(vs)>0 and len(hs)>0:
            return Box(children=[HBox(hs),VBox(vs)])
        elif len(vs)>0:
            return VBox(vs)
        else:
            return HBox(hs)

    def showGrid(self,id,df):
        if id in self.widgets:
            with self.widgets[id]:
                display( DataGrid(df, editable=False) )

    def showLink(self,id,link,linkTitle):
        if id in self.widgets:
            with self.widgets[id]:
                display( f"Download: {linkTitle}" )
                display( FileLink(link) )

    def _displayChart(self,id,widget_,chartG_):
        with widget_:
            display(go.FigureWidget(chartG_.fig.to_dict()).show())



