import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import logging

# Logging configuration
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

class Plot:
    def __init__(self, df) -> None:
        self.df = df
        self.limitation_applied = False
        self.draving_chart()
        
    def draving_chart(self):
        """
        A method that creates a graph based on data retrieved from a Firebase database.
        """
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
        except Exception as e:
            logging.error(f"Error while creating a chart {e}")
            return False
    
    def convert_to_int(self, ylim_first, ylim_end):
        """Converting a chart range into variables of type int

        Args:
            ylim_first (_type_ str): Lower value of the y-axis range
            ylim_end (_type_ str): Higher value of the y-axis range

        """
        try:
            ylim_first = int(ylim_first) if ylim_first else None
            ylim_end = int(ylim_end) if ylim_end else None
            self.ylim = (ylim_first, ylim_end)
            return self.ylim
        except Exception as e:
            logging.error(f"Error when converting from str to int: {e}")
            return False
        
    def conv_time(self, xlim_first, xlim_end):
        """Changing values specified in FlaskForm to datetime values
        Args:
            xlim_first (_type_ str): Lower value of the x-axis range
            xlim_end (_type_ str): Higher value of the x-axis range
        """
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
        except Exception as e:
            logging.error(f"Error when converting variables to datetime: {e}")
            return False

    def limiation(self):
        """
        Introduction of xlim, ylim range for the created chart based on the data saved from the FireBase database.
        """
        try:
            if any(x is not None for x in self.xlim):
                self.limitation_applied = True
                if self.xlim[0] == None:
                    self.ax.set_xlim(right=self.xlim[1])
                elif self.xlim[1] == None:
                    self.ax.set_xlim(left=self.xlim[0])
                else:
                    self.ax.set_xlim(self.xlim[0], self.xlim[1])
        except Exception as e:
            logging.error(f"Error when using xlim for chart: {e}")

        try:
            if any(x is not None for x in self.ylim):
                if self.ylim[0] == None:
                    self.ax.set_ylim(top=self.ylim[1])
                elif self.ylim[1] == None:
                    self.ax.set_ylim(bottom=self.ylim[0])
                else:
                    self.ax.set_ylim(self.ylim[0], self.ylim[1])
        except Exception as e:
            logging.error(f"Error when using ylim for chart: {e}")
        
    def saving(self):
        """
        Save the chart with a .png extension.
        """
        plt.savefig("static/chart.png", bbox_inches="tight")
        
    def limitation_values(self):
        """
        Save the values xlim, ylim to the results dictionary for use in the Flask module.
        """
        results = {}
        try:
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
        except Exception as e:
            logging.error(f"Error when writing data to the dictionary: {e}")
            
    def selecting_border_data(self, value):
        """
        Selection of the value of electricity consumption corresponding to a specifically selected date on the basis of xlim, ylim.
        Args:
                value (_type_ int): 
                0: Calculation for the situation when xlim = (None, y) where y = any date
                1: Calculation for the situation when xlim = (y, None) where y = any date
                2: Calculation for the situation when xlim = (x, y) where x,y = any date
        """
        match value:
            case 0:
                try:
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
                except Exception as e:
                    logging.error(f"Error when reading a value for a fixed date: {e}")
            case 1:
                try:
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
                except Exception as e:
                    logging.error(f"Error when reading a value for a fixed date: {e}")
            case 2:
                try:
                    return self.selecting_border_data(0), self.selecting_border_data(1)
                except Exception as e:
                    logging.error(f"Error when reading a value for a fixed date: {e}")