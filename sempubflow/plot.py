"""
Created on 2023-12-11

@author: wf

Histogram Class for Plotting and Saving Histograms

This class provides a utility for creating, plotting, and saving histograms using matplotlib. It allows you to customize various plot parameters, including the number of bins, title, and axis labels, as well as apply logarithmic scales to the X and Y axes.

Instructions for an LLM (Large Language Model) to create this class:
1. Import the required library:

import matplotlib.pyplot as plt


2. Create an instance of the Histogram class by providing the following parameters:
- `data` (list): The data for which you want to create a histogram.
- `bins` (int, optional): The number of bins for the histogram (default is 50).
- `title` (str, optional): The title for the histogram plot.
- `xlabel` (str, optional): The label for the X-axis.
- `ylabel` (str, optional): The label for the Y-axis.
- `log_scale_x` (bool, optional): Whether to apply a logarithmic scale to the X-axis (default is False).
- `log_scale_y` (bool, optional): Whether to apply a logarithmic scale to the Y-axis (default is False).

3. Use the `plot_histogram` method to generate and display the histogram plot:
- `with_show` (bool, optional): If True, the plot will be displayed interactively (default is False).

4. Use the `save_plot` method to save the histogram plot to a file:
- `filepath_prefix` (str): The path of the file to save the plot without the extension.
- `format` (str, optional): The format of the file ('png' or 'svg', default is 'png').

Example usage:
```python
# Create a histogram object
hist = Histogram(data, bins=20, title='Sample Histogram', xlabel='Value', ylabel='Frequency', log_scale_x=True)

# Plot and display the histogram
hist.plot_histogram(with_show=True)

# Save the histogram plot as a PNG file
hist.save_plot('histogram', format='png')

"""
import matplotlib.pyplot as plt

class Histogram:
    """
    Histogram plot utility
    """
    def __init__(self, data, bins=50, title='', xlabel='', ylabel='', log_scale_x=False, log_scale_y=False):
        """
        Initialize the HistogramPlotter with given data, plot parameters, and log scale options.

        Args:
            data (list): Data for plotting the histogram.
            bins (int): Number of bins for the histogram.
            title (str): Title of the histogram plot.
            xlabel (str): Label for the X-axis.
            ylabel (str): Label for the Y-axis.
            log_scale_x (bool): Whether to apply a logarithmic scale to the x-axis.
            log_scale_y (bool): Whether to apply a logarithmic scale to the y-axis.
        """
        if not isinstance(data, list) or not data:
            raise ValueError("Data must be a non-empty list.")

        self.data = data
        self.bins = bins
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.log_scale_x = log_scale_x
        self.log_scale_y = log_scale_y
        self.plt=None
    
    def create_histogram(self):
        """
        Plot the histogram based on the provided data and parameters, with optional logarithmic scales.
        """
        plt.hist(self.data, bins=self.bins)
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        
        if self.log_scale_x:
            plt.xscale('log')
        if self.log_scale_y:
            plt.yscale('log')
        
        plt.grid(True)
        self.plt=plt

    def save_plot(self, filepath_prefix, file_format='png'):
        """
        Save the histogram plot to a file.

        Args:
            filepath_prefix (str): path of the file to save the plot without extension.
            file_format (str): Format of the file ('png' or 'svg').
        """
        if not self.plt:
            self.create_histogram()
        self.plt.savefig(f"{filepath_prefix}.{file_format}", format=file_format)
