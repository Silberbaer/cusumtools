import pandas as pd
from pandasql import sqldf
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import pylab as pl
import tkFileDialog
import Tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg


    
class App(tk.Frame):
    def __init__(self, parent,eventsdb,column_list):
        tk.Frame.__init__(self, parent)
        self.eventsdb = eventsdb
        self.eventsdb_subset = eventsdb
        self.column_list = column_list
        self.x_col_options = tk.StringVar()
        self.x_col_options.set('Select X')
        self.y_col_options = tk.StringVar()
        self.y_col_options.set('Select Y')
        self.graph_list = tk.StringVar()
        self.graph_list.set('Graph Type')
        parent.deiconify()
        
        self.filter_button = tk.Button(parent,text='Apply Filter',command=self.filter_db)
        self.reset_button = tk.Button(parent,text='Reset DB',command=self.reset_db)
        self.plot_button = tk.Button(parent,text='Update Plot',command=self.update_plot)
        

        self.x_option = tk.OptionMenu(parent, self.x_col_options, *self.column_list)
        self.y_option = tk.OptionMenu(parent, self.y_col_options, *self.column_list)
        self.graph_option = tk.OptionMenu(parent, self.graph_list, 'XY Plot', '1D Histogram', '2D Histogram', command=self.disable_options)
        self.x_log_var = tk.IntVar()
        self.x_log_check = tk.Checkbutton(parent, text='Log X', variable = self.x_log_var)
        self.y_log_var = tk.IntVar()
        self.y_log_check = tk.Checkbutton(parent, text='Log Y', variable = self.y_log_var)

        self.db_info_string = tk.StringVar()
        self.db_info_string.set('Number of events: ' +str(len(self.eventsdb_subset)))
        self.db_info_display = tk.Label(parent, textvariable=self.db_info_string)
        
        self.f = Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.f, master=parent)
        

        self.toolbar_frame = tk.Frame(parent)
        
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        
        self.filter_entry = tk.Entry(parent)
        self.filter_label=tk.Label(parent,text='DB Filter String:')
        self.x_bins=tk.Label(parent,text='X Bins:')
        self.y_bins=tk.Label(parent,text='Y Bins:')

        self.xbin_entry = tk.Entry(parent)
        self.xbin_entry.insert(0,10)
        self.ybin_entry = tk.Entry(parent)
        self.ybin_entry.insert(0,10)

        self.x_log_check.grid(row=3,column=2)
        self.y_log_check.grid(row=4,column=2)
        
        self.x_bins.grid(row=3,column=3)
        self.y_bins.grid(row=4,column=3)
        self.xbin_entry.grid(row=3,column=4)
        self.ybin_entry.grid(row=4,column=4)
        
        self.graph_option.grid(row=3,column=0,rowspan=2)
        self.x_option.grid(row=3,column=1)
        self.y_option.grid(row=4,column=1)
        
        self.filter_button.grid(row=1,column=2)
        self.reset_button.grid(row=1,column=3)
        
        self.plot_button.grid(row=3,column=5,rowspan=2)

        self.toolbar_frame.grid(row=1,column=0,columnspan=6)
        self.canvas.get_tk_widget().grid(row=0,column=0,columnspan=6)
        
        self.filter_label.grid(row=2,column=0)
        self.filter_entry.grid(row=2,column=1)
        self.filter_button.grid(row=2,column=2)
        self.reset_button.grid(row=2,column=3)
        self.db_info_display.grid(row=2,column=4)


        
    def filter_db(self):
        filterstring = self.filter_entry.get()
        eventsdb_subset = self.eventsdb_subset
        self.eventsdb_subset = sqldf('SELECT * from eventsdb_subset WHERE %s' % filterstring,locals())
        self.db_info_string.set('Number of events: ' +str(len(self.eventsdb_subset)))

    def reset_db(self):
        self.eventsdb_subset = self.eventsdb
        self.db_info_string.set('Number of events: ' +str(len(self.eventsdb_subset)))

    def plot_xy(self):
        logscale_x = self.x_log_var.get()
        logscale_y = self.y_log_var.get()
        x_label = self.x_option.cget('text')
        y_label = self.y_option.cget('text')
        x_col = self.parse_db_col(x_label)
        y_col = self.parse_db_col(y_label)
        self.f.clf()
        a = self.f.add_subplot(111)
        a.set_xlabel(x_label)
        a.set_ylabel(y_label)
        self.f.subplots_adjust(bottom=0.14,left=0.16)
        a.plot(x_col,y_col,marker='.',linestyle='None')
        if logscale_x:
            a.set_xscale('log')
        if logscale_y:
            a.set_yscale('log')
        self.canvas.show()

    def plot_1d_histogram(self):
        logscale_x = self.x_log_var.get()
        logscale_y = self.y_log_var.get()
        x_label = self.x_option.cget('text')
        col = self.parse_db_col(x_label)
        numbins = self.xbin_entry.get()
        self.f.clf()
        a = self.f.add_subplot(111)
        if logscale_x:
            a.set_xlabel('Log(' +str(x_label)+')')
            a.set_ylabel('Count')
            self.f.subplots_adjust(bottom=0.14,left=0.16)
            a.hist(np.log(col),bins=int(numbins),log=bool(logscale_y))
        else:
            a.set_xlabel(x_label)
            a.set_ylabel('Count')
            self.f.subplots_adjust(bottom=0.14,left=0.16)
            a.hist(col,bins=int(numbins),log=bool(logscale_y))
        self.canvas.show()
        
    def plot_2d_histogram(self):
        logscale_x = self.x_log_var.get()
        logscale_y = self.y_log_var.get()
        x_label = self.x_option.cget('text')
        y_label = self.y_option.cget('text')
        x_col = self.parse_db_col(x_label)
        y_col = self.parse_db_col(y_label)
        xbins = self.xbin_entry.get()
        ybins = self.ybin_entry.get()
        self.f.clf()
        a = self.f.add_subplot(111)
        a.set_xlabel(x_label)
        a.set_ylabel(y_label)
        self.f.subplots_adjust(bottom=0.14,left=0.16)
        a.hist2d(np.log(x_col) if bool(logscale_x) else x_col,np.log(y_col) if bool(logscale_y) else y_col,bins=[int(xbins),int(ybins)],norm=matplotlib.colors.LogNorm())
        self.canvas.show()

    def disable_options(self, *args):
        option = self.graph_option.cget('text')
        if option == '1D Histogram':
            self.y_option['state']='disabled'
            self.ybin_entry['state']='disabled'
            self.xbin_entry['state']='normal'
        elif option == 'XY Plot':
            self.ybin_entry['state']='disabled'
            self.xbin_entry['state']='disabled'
            self.y_option['state']='normal'
        else:
            self.y_option['state']='normal'
            self.ybin_entry['state']='normal'
            self.xbin_entry['state']='normal'

    def update_plot(self):
        option = self.graph_option.cget('text')
        if option == 'XY Plot':
            self.plot_xy()
        elif option == '1D Histogram':
            self.plot_1d_histogram()
        elif option == '2D Histogram':
            self.plot_2d_histogram()
        else:
            pass

    def parse_db_col(self, col):
        if col in ['blockages_pA','level_current_pA','level_duration_us']:
            return_col = np.hstack([np.array(a,dtype=float) for a in self.eventsdb_subset[col].str.split(';')])
        else:
            return_col = self.eventsdb_subset[col]
        return return_col
       
def main():
    root=tk.Tk()
    root.withdraw()
    file_path_string = tkFileDialog.askopenfilename(initialdir='C:\Users\kbrig035\Analysis\CUSUM\output\\')
    eventsdb = pd.read_csv(file_path_string,encoding='utf-8')
    column_list = list(eventsdb)
    App(root,eventsdb,column_list).grid(row=0,column=0)
    root.mainloop()

if __name__=="__main__":
    main()

