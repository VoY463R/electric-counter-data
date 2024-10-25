import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


class Plot:
    def __init__(self, df) -> None:
        self.df = df
        self.draving_chart()
        
    def draving_chart(self):
        try:
            self.df["Czas"] = pd.to_datetime(self.df["Czas"], format="%y-%m-%d %H:%M:%S")
            self.df.sort_values("Czas", inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            time = self.df["Czas"]
            value = self.df["Odczytana wartosc"]
            self.fig, self.ax = plt.subplots(figsize=(10, 5))
            self.ax.plot(time, value, marker="o")
            self.ax.set_title("Wykres wartości w czasie (posortowane)")
            self.ax.set_xlabel("Data i czas")
            self.ax.set_ylabel("Wartość [kWh]")
            self.ax.tick_params(axis="x", rotation=45)
            self.ax.grid(True)
        except:
            return False
    
    def convert_to_int(self, ylim_first, ylim_end):
        try:
            ylim_first = int(ylim_first) if ylim_first else None
            ylim_end = int(ylim_end) if ylim_end else None
            self.ylim = (ylim_first, ylim_end)
            return self.ylim
        except:
            return False
        
    def conv_time(self, xlim_first, xlim_end):
        try:
            xlim_first = (
                datetime(
                    list(map(int, xlim_first.split("-")))[2],
                    list(map(int, xlim_first.split("-")))[1],
                    list(map(int, xlim_first.split("-")))[0],
                )
                if xlim_first
                else None
            )
            xlim_end = (
                datetime(
                    list(map(int, xlim_end.split("-")))[2],
                    list(map(int, xlim_end.split("-")))[1],
                    list(map(int, xlim_end.split("-")))[0],
                )
                if xlim_end
                else None
            )
            self.xlim = (xlim_first, xlim_end)
            return self.xlim
        except:
            print("Niepoprawny format daty")
            return False

    def limiation(self):

        if any(x is not None for x in self.xlim):
            if self.xlim[0] == None:
                self.ax.set_xlim(right=self.xlim[1])
            elif self.xlim[1] == None:
                self.ax.set_xlim(left=self.xlim[0])
            else:
                self.ax.set_xlim(self.xlim[0], self.xlim[1])

        if any(x is not None for x in self.ylim):
            if self.ylim[0] == None:
                self.ax.set_ylim(top=self.ylim[1])
            elif self.ylim[1] == None:
                self.ax.set_ylim(bottom=self.ylim[0])
            else:
                self.ax.set_ylim(self.ylim[0], self.ylim[1])

    def saving(self):
        plt.savefig("static/chart.png", bbox_inches="tight")