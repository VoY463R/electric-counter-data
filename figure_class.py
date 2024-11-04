import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


class Plot:
    def __init__(self, df) -> None:
        self.df = df
        self.limitation_applied = False
        self.draving_chart()
        
    def draving_chart(self):
        try:
            self.df["Czas"] = pd.to_datetime(self.df["Czas"], format="%y-%m-%d %H:%M:%S")
            self.df.sort_values("Czas", inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            self.time = self.df["Czas"]
            self.value = self.df["Odczytana wartosc"]
            self.fig, self.ax = plt.subplots(figsize=(10, 5))
            self.ax.scatter(self.time, self.value, marker="o")
            self.ax.set_title("Wykres wartości w czasie (posortowane)")
            self.ax.set_xlabel("Data i czas")
            self.ax.set_ylabel("Wartość [kWh]")
            self.ax.tick_params(axis="x", rotation=45)
            self.ax.grid(True)
            self.default_result = {
                'up_time': self.time.iloc[-1],
                'up_time_value': self.value.values[-1],
                'down_time': self.time.iloc[0],
                'down_time_value': self.value.values[0],
                }
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
            return False

    def limiation(self):

        if any(x is not None for x in self.xlim):
            self.limitation_applied = True
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
        
    def limitation_values(self):
        results = {}
        if self.limitation_applied:
            self.limitation_applied = False
            if self.xlim[0] == None:
                results = self.selecting_border_data(0)
                results.update({'down_time': self.time.iloc[0],'down_time_value': self.value.values[0]})
            elif self.xlim[1] == None:
                results = self.selecting_border_data(1)
                results.update({'up_time': self.time.iloc[-1],'up_time_value': self.value.values[-1]})
            else:
                results, results_second = self.selecting_border_data(2)
                results.update(results_second)
            return results
        else:
            return self.default_result
        
    def selecting_border_data(self, value):
        match value:
            case 0:
                if self.xlim[1] <= self.time.iloc[-1]:
                    for i in range(len(self.time)):
                        if self.time[i] <= self.xlim[1] <= self.time[i+1]:
                            self.up_time = self.time[i]
                            self.up_time_value = self.df[self.df['Czas'] == self.up_time]['Odczytana wartosc'].values[0]
                            result = {
                                'up_time': self.up_time,
                                'up_time_value': self.up_time_value,
                            }
                            return result
                else:
                    return self.default_result
            case 1:
                if self.xlim[0] >= self.time.iloc[0]:
                    for i in range(len(self.time)):
                        if self.time[i] <= self.xlim[0] <= self.time[i+1]:
                            self.down_time = self.time[i+1]
                            self.down_time_value = self.df[self.df['Czas'] == self.down_time]['Odczytana wartosc'].values[0]
                            result = {
                                'down_time' : self.down_time,
                                'down_time_value' : self.down_time_value
                            }
                            return result
                else:
                    return self.default_result
            case 2:
                return self.selecting_border_data(0), self.selecting_border_data(1)

            