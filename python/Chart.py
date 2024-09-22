"""
Chart class to simplify ability to builds charts using simpler functions

Create a Chart object and use
addPlot to plot from a vector for x and y or use plot to add from a dataframe using ability 
addTrace add a layer on chart with series and plots
call final to assemble the charts
to check multiple y series or y1 series and switch types where required easily
Build save images and plot to notebooks
"""
import random
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from datetime import datetime, date, timedelta
from pure_tech.core.Logger import Logger
logger = Logger(__file__)

from enum import Enum, auto

class ChartTypes(Enum):
    Line = auto()
    Scatter = auto()
    Area = auto()
    Dots = auto()
    Column = auto()
    Bar = auto()

    def all():
        return [i[1].name for i in ChartTypes.__members__.items()]

    def toEnum(s, defVal=None):
        for e in ChartTypes.__members__.items():
            if e[1].name.lower()==s.lower():
                return e[1]
        return defVal

## Chart class to load and plot charts
## Ability bind and load multiple sub plots
## Load from and plot from dataframes
class Chart:

    def __init__(self, log=False):
        self.shouldLog = log
        self.traces = {}
        self.cols = 0
        self.specs = {}
        self.fig = None
        self.titles = {}

    def log(self,x,force=False):
        if self.shouldLog or force:
            logger.info( f"{datetime.now().strftime('%Y%m%d %H:%M:%S.%f')} {x}" )

    ## Set title for chart or Sub chart block
    def setTitle(self, r, c, title, xT = None, y1T = None, y2T = None ):
        self.titles[(r,c)] = {'title':title, 'xt':xT, 'y1':y1T, 'y2':y2T}

    ## Save chart to file
    def save(self,fName,fType='jpeg'):
        if self.fig is not None:
            self.fig.write_image( f"{fName}.{fType}" if fType not in fName else fName )

    ## Add a single plot for x and y and bind
    def addPlot(tp, x, y, name, color=None, showLegend=True, mode=None, legendGroup = None, width=2, symbol=None):
        if type(tp)==str:
            tp = ChartTypes.toEnum(tp)
        #if tp=='Bar':
        if tp==ChartTypes.Bar:
            return go.Bar( x=x, y=y, name=name, marker_color=color, showlegend=showLegend)
        #elif tp=='Area':
        elif tp==ChartTypes.Area:
            return go.Scatter( x=x, y=y, name=name, mode=mode, fill=color, legendgroup=legendGroup, showlegend=showLegend)
        #elif tp=='Dots':
        elif tp==ChartTypes.Dots:
            return go.Scatter( x=x, y=y, name=name, mode='markers', marker_color=color, marker_symbol='circle',
                        marker_line_color=color, marker_line_width=width, 
                        legendgroup=legendGroup, showlegend=showLegend )
        #elif tp=='Scatter':
        elif tp==ChartTypes.Scatter:
            return go.Scatter( x=x, y=y, name=name, mode=mode, marker_color=color, marker_symbol=symbol,
                        marker_line_color=color, marker_line_width=width, connectgaps=False,
                        legendgroup=legendGroup, showlegend=showLegend )
        else:
            return go.Scatter( x=x, y=y, name=name, mode='lines', connectgaps=True, legendgroup=legendGroup,
                        line_color=color, showlegend=showLegend)

    ## Plot columns from dataframe, by adding several chart points across
    def plot(self, df, x, y1s, y2s=[], y1Type={}, y2Type={}, colors={}, showLegend=True, row=1, col=1, 
            xT=None, y1T=None, y2T=None, title=None, legendGroup=None):
        y1s = [y1s] if isinstance(y1s,list)==False else y1s
        y2s = [y2s] if isinstance(y2s,list)==False else y2s
        for y1 in y1s:
            for ln in df.columns:
                if y1.lower() in ln.lower():
                    self.intAddPlot( df[x], df[ln], ln, y1, y1Type, colors, False, row, col, showLegend, legendGroup=legendGroup )
        
        for ln in df.columns:
            for y2 in y2s:
                if y2.lower() in ln.lower():
                    self.intAddPlot( df[x], df[ln], ln, y2, y2Type, colors, True, row, col, showLegend, legendGroup=legendGroup )
        if title is not None:
            self.setTitle( row, col, title, xT, y1T, y2T )

    ## Plot a dataframe as a tablewith columns and values  in chart
    def plotTable(self, dfe, row=1, col=1, title=None, fmts=None):
        headerColor = 'grey'
        rowEvenColor = 'lightgrey'
        rowOddColor = 'white'
        tr = go.Table(
            header=dict(values=dfe.columns,line_color='darkslategray',fill_color=headerColor,align=['left','center'],
            font=dict(color='white', size=12)),cells=dict(values=[dfe[c] for c in dfe.columns],line_color='darkslategray',
            format=fmts, fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
            align = ['left', 'center'],font = dict(color = 'darkslategray', size = 11)) )
        self.addTrace(tr, 'table', row, col, False)

    ## Internal function to attach plot
    def intAddPlot( self, x, y, ln, s1, dct, colors, secondY, row, col, showLegend, legendGroup=None ):
        s1t = dct[s1] if s1 in dct else ['Scatter']
        s1t = s1t if type(s1t)==list else [s1t]
        clr = colors[ln] if ln in colors else None
        if clr is not None:
            clr = colors[s1] if s1 in colors else None
        tr = None
        if len(s1t) >= 4:
            clr = clr if clr is not None else s1t[3]
            tr = Chart.addPlot( s1t[0], x, y, ln, color=clr, showLegend=showLegend,
                              symbol=s1t[2], width=s1t[4], mode=s1t[1], legendGroup=legendGroup )
        else:
            tr = Chart.addPlot( s1t[0], x, y, ln, color=clr, showLegend=showLegend, legendGroup=legendGroup )
        self.addTrace( tr, 'xy', row, col, secondY )
        
    ## Add a sub plot
    def addTrace(self, tr, trt, r, c, secondY = False ):
        if r not in self.traces:
            self.traces[r] = {}
        if c not in self.traces[r]:
            self.traces[r][c] = []
        self.traces[r][c].append( (tr,secondY) )
        self.cols = max( self.cols, c )
        if (r,c) not in self.specs:
            self.specs[(r,c)] = [trt,secondY]
        elif not self.specs[(r,c)][1] and secondY:
            self.specs[(r,c)][1] = True

    ## Show/Display chart
    def show(self, mode=None, handle=None):
        if self.fig is not None:
            if mode is None:
                self.fig.show()
            elif mode=='widget' and handle is None:
                go.FigureWidget(self.fig.to_dict()).show()
            elif mode=='widget':
                handle.update(self.fig)
    
    ## Assemble and plot charts
    def final(self,title=None,w=None,h=None,xAngle=None,yAngle=None,y1Range=None,y2Range=None,sharedX=True,sharedY=True,props=None):
        if len(self.traces) <=0:
            self.log( "No Chart available" )
            return None
        spcs = []
        self.log( f"num Traces:{len(self.traces)} traces:{len(self.traces[1])}, cols:{self.cols}" )
        self.log( self.specs )
        titls = []
        for r in range(1,len(self.traces)+1):
            st=self.traces[r]
            spcs.append( [ 
                {'type':self.specs[(r,c)][0],'secondary_y':self.specs[(r,c)][1]} if self.specs[(r,c)][0]=='xy' else {'type':'table'}
                          for c in range(1,len(st)+1)] )
            for c in range(1,len(st)+1):
                stt = self.titles[(r,c)] if (r,c) in self.titles else {'title':'', 'xt':'', 'y1':'', 'y2':''}
                if (r,c) not in self.titles:
                    self.titles[(r,c)] = stt
                titls.append( stt['title'] )
        self.log( spcs )
        vspace = 0.06 if len(self.traces)<10 else 0.01
        hspace = 0.08 if self.cols<10 else 0.01
        fig =  make_subplots( rows=len(self.traces), cols=self.cols, vertical_spacing=vspace, horizontal_spacing=hspace,
                             specs=spcs, subplot_titles=titls, shared_xaxes=sharedX, shared_yaxes=sharedY)
        for r in range(1,len(self.traces)+1):
            st=self.traces[r]
            self.log( f"Plot: Ploting Row:{r}" )
            for c in range(1,len(st)+1):
                sy = self.specs[(r,c)][1]
                lt=1
                for t in st[c]:
                    #self.log( "Plot:", r, c, lt, t, sy )
                    fig.add_trace( t[0], row=r, col=c , secondary_y=t[1] )
                    lt=lt+1
                stt = self.titles[(r,c)]
                #fig.update_layout( title_text=stt['title'], row=r, col=c )
                fig.update_xaxes( title_text=stt['xt'], row=r, col=c )
                if xAngle is not None:
                    fig.update_xaxes( tickangle=xAngle )
                if yAngle is not None:
                    fig.update_yaxes( tickangle=yAngle )
                    if sy:
                        fig.update_yaxes( tickangle=yAngle, secondary_y=True )
                fig.update_yaxes( title_text=stt['y1'], row=r, col=c )
                if y1Range is not None:
                    fig.update_yaxes(range=y1Range)
                if sy:
                    fig.update_yaxes( title_text=stt['y2'], row=r, col=c, secondary_y=True )
                    if y2Range is not None:
                        fig.update_yaxes(range=y2Range, secondary_y=True)
        if title is not None:
            fig.update_layout( title_text=title )
        if w is not None and h is not None:
            fig.update_layout( autosize=False, width=w, height=h )
        if True:
            fig.update_layout( template='plotly',
                paper_bgcolor="LightSteelBlue", plot_bgcolor="LightSteelBlue" )

        if props is not None:
            if 'cat' in props and props['cat']=='Category':
                fig.update_layout(xaxis_type='category')
            if 'stack' in props:
                fig.update_layout(barmode='stack')
            if 'logy' in props and props['logy']:
                fig.update_yaxes(type="log", row=row, col=col)
            if 'logy1' in props and props['logy1']:
                fig.update_yaxes(type="log", row=row, col=col, secondary_y=True)

            if all( [i in props for i in ['x','y','xanchor','yanchor','orientation']] ):
                fig.update_layout(legend=dict(orientation=props['orientation'],xanchor=props['xanchor'],yanchor=props['yanchor'],y=props['y'],x=props['x']))
            elif all( [i in props for i in ['xanchor','yanchor','orientation']] ):
                fig.update_layout(legend=dict(orientation=props['orientation'],xanchor=props['xanchor'],yanchor=props['yanchor']))
            #else:
            #    fig.update_layout(legend=dict(orientation='v',xanchor="center",yanchor="bottom",y=1.1,x=0))
        self.fig = fig
        return self.fig

if __name__=='__main__':
    g=Chart()
    opt = 2
    method = 2
    if opt == 1:
        dct = {'x':[1,2,3,4],'y1':[1,2,3,4],'y2':[90,30,34,80]}
        df=pd.DataFrame.from_dict(dct)
        self.log(df)
        if method==1:
            gsT = go.Scatter( x=df['x'], y=df['y1'], name='y1', mode='lines' )
            g.addTrace( gsT, 'xy', 1, 1, False )
            gsT = go.Scatter( x=df['x'], y=df['y1'], name='y1t', mode='markers')
            g.addTrace( gsT, 'xy', 1, 1, False )
            gsT = go.Scatter( x=df['x'], y=df['y2'], name='y2', mode='markers')
            g.addTrace( gsT, 'xy', 1, 1, True )
            g.setTitle( 1, 1, 'Testing chart r1c1', xT='numbers', y1T='Y1T a nums', y2T='Y2 T numbers' )
            gsT = go.Bar( x=df['x'], y=df['y2'], name='y23')
            g.addTrace( gsT, 'xy', 1, 2, False )
            g.setTitle( 1, 2, 'Testing chart r1c2', xT='numbers', y1T='Y1T b nums', y2T='Y2 T b numbers' )
        else:
            g.plot( df, 'x', ['y1'], ['y2'], 
                  y1Type={'y1':['Scatter','lines+markers','circle','green',3]}, y2Type={'y2':['Scatter','markers','circle','red',3]},
                  title="Testing chrt r1c1", xT="numbers", y1T="Y1T a nums", y2T="Y2 T numbers" )
            g.plot( df, 'x', ['y2'], [], 
                  y1Type={'y2':['Bar']}, row=1, col=2,
                  title="Testing chrt r1c2", xT="numbers", y1T="Y1T b nums", y2T="Y2 T b Tnumbers" )
    
    if opt == 2:
        n,dct=(100,{})
        useTime = True
        if useTime:
            dct['x'] = [datetime.now()-timedelta(seconds=i) for i in random.sample(range(1, n*100), n)]
        else:
            dct['x'] = [i for i in range(0, n)]
        for c in range(1,10):
            for tr in range(0,random.sample(range(1,4),1)[0]):
                c = str(c)+'_'+str(tr)
                dct[c] = [i for i in random.sample(range(1, n*100), n)]
        df=pd.DataFrame.from_dict(dct)
        if useTime:
            df['x']=df['x'].astype('datetime64[ns]')
            df = df.sort_values(by='x')
        rw=1
        t=1
        if method==1:
            for i in range(1,9,3):
                cl=1
                for l in range(i,i+2):
                    br = True if random.sample(range(1,10),1)[0]%2==0 else False
                    for tr in [cl for cl in df.columns if str(t)+'_' in cl]:
                        if br:
                            gsTmp = go.Scatter(x=df['x'], y=df[tr], name=tr, mode='markers')
                        else:
                            gsTmp = go.Scatter(x=df['x'], y=df[tr], name=tr, mode='lines', connectgaps=True)
                        g.addTrace( gsTmp, 'xy', rw, cl, True if rw==1 else False )
                    g.setTitle( rw, cl, f"r:{rw}.c:{cl}", xT='Time', y1T='Y1 n', y2T='Y2 n'+str(cl) )
                    cl=cl+1
                    t=t+1
                rw=rw+1
        else:
            t=1
            for i in range(1,9,3):
                cl = 1
                for l in range(i,i+3):
                    br = True if random.sample(range(1,10),1)[0]%2==0 else False
                    if br:
                        g.plot( df, 'x', [str(t)+'_'], y1Type={str(t)+'_':['Line']}, row=t, col=cl )
                    else:
                        g.plot( df, 'x', [str(t)+'_'], y1Type={str(t)+'_':['Bar']}, row=t, col=cl )
                    g.setTitle( t, cl, f"r:{rw}.c:{cl}", xT='Time', y1T='Y1 n', y2T='Y2 n'+str(cl) )
                    cl=cl+1
                t=t+1
            cl=1
            for i in range(1,9,3):
                c=['x']+[l for l in df.columns if str(t)+'_' in l]
                g.plotTable(df[c], row=t, col=cl, title="My table")
                cl=cl+1
    fig=g.final( "Test Charts" )
    g.save( "TestChart.jpeg" )

