import asyncio
import time, sys
import matplotlib.pyplot as plt
from typing import List, Dict, Any
sys.path.append('Python_Practice/')
# Assume these imports exist from your environment
from device4 import DataParser  # type: ignore
from classes import Parameter, LimitValues, ParameterMessage  # type: ignore


class RealTimePlotter:
    def __init__(self):
        """
        Initializes the RealTimePlotter class which handles data collection, plotting, and updating in real-time.
        """
        self.PARAMETER = self.initialize_parameter_structure()
        self.fig, self.axes = plt.subplots(3, 1, figsize=(12, 8))
        self.lines = self.initialize_plot()
        
    def initialize_parameter_structure(self) -> Dict[str, List[Any]]:
        """
        Initialize the PARAMETER dictionary structure with empty lists for plotting.

        Returns:
            dict: A dictionary containing all parameter keys initialized to empty lists.
        """
        return {
            'timestamps': [],
            'par_udp.par_func_code': [],
            'par_udp.parcode': [],
            'par_udp.par_status': [],
            'par_udp.par_val': [],
            'ext_par_udp.par_func_code': [],
            'ext_par_udp.par_code': [],
            'ext_par_udp.par_val': [],
            'setup_n_lin.par_func_code': [],
            'setup_n_lin.parcode': [],
            'setup_n_lin.flag': [],
            'setup_n_lin.limit_values[0].lo_limit': [],
            'setup_n_lin.limit_values[0].hi_limit': [],
            'setup_n_lin.limit_values[1].lo_limit': [],
            'setup_n_lin.limit_values[1].hi_limit': [],
            'setup_n_lin.limit_values[2].lo_limit': [],
            'setup_n_lin.limit_values[2].hi_limit': [],
            'setup_n_lin.extra_limit': [],
            'par_mssg_s.par_func_code': [],
            'par_mssg_s.parcode': [],
            'par_mssg_s.messages[0].attribute': [],
            'par_mssg_s.messages[0].msg_index': [],
            'par_mssg_s.messages[1].attribute': [],
            'par_mssg_s.messages[1].msg_index': [],
            'par_mssg_s.messages[2].attribute': [],
            'par_mssg_s.messages[2].msg_index': [],
            'par_mssg_s.value': [],
            'par_type': [],
            'parcode': [],
            'pos': [],
        }

    def initialize_plot(self) -> Dict[str, plt.Line2D]:
        """
        Initialize the plot and return the line objects that will be updated.

        Returns:
            dict: A dictionary of Line2D objects for each parameter to be plotted.
        """
        lines = {}
        # First group of parameters (par_udp and ext_par_udp)
        self.axes[0].set_title('par_udp and ext_par_udp')
        lines['par_udp.par_func_code'], = self.axes[0].plot([], [], label='par_udp.par_func_code')
        lines['par_udp.parcode'], = self.axes[0].plot([], [], label='par_udp.parcode')
        lines['par_udp.par_status'], = self.axes[0].plot([], [], label='par_udp.par_status')

        # Second group of parameters (setup_n_lin)
        self.axes[1].set_title('setup_n_lin')
        lines['setup_n_lin.par_func_code'], = self.axes[1].plot([], [], label='setup_n_lin.par_func_code')
        lines['setup_n_lin.parcode'], = self.axes[1].plot([], [], label='setup_n_lin.parcode')
        lines['setup_n_lin.limit_values[0].lo_limit'], = self.axes[1].plot([], [], label='lo_limit[0]')
        lines['setup_n_lin.limit_values[0].hi_limit'], = self.axes[1].plot([], [], label='hi_limit[0]')
        lines['setup_n_lin.limit_values[1].lo_limit'], = self.axes[1].plot([], [], label='lo_limit[1]')
        lines['setup_n_lin.limit_values[1].hi_limit'], = self.axes[1].plot([], [], label='hi_limit[1]')

        # Third group of parameters (par_mssg_s and metadata)
        self.axes[2].set_title('par_mssg_s and Metadata')
        lines['par_mssg_s.par_func_code'], = self.axes[2].plot([], [], label='par_mssg_s.par_func_code')
        lines['parcode'], = self.axes[2].plot([], [], label='parcode')
        lines['pos'], = self.axes[2].plot([], [], label='pos')

        # Final adjustments
        for ax in self.axes:
            ax.set_xlabel('Timestamps')
            ax.set_ylabel('Values')
            ax.grid(True)
            ax.legend()

        plt.tight_layout()
        return lines

    def update_plot(self):
        """
        Update the existing plot lines with data from the PARAMETER dictionary.
        This function is called every time new data is added.
        """
        # Update the first subplot
        self.lines['par_udp.par_func_code'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['par_udp.par_func_code'])
        self.lines['par_udp.parcode'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['par_udp.parcode'])
        self.lines['par_udp.par_status'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['par_udp.par_status'])

        # Update the second subplot
        self.lines['setup_n_lin.par_func_code'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['setup_n_lin.par_func_code'])
        self.lines['setup_n_lin.parcode'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['setup_n_lin.parcode'])
        self.lines['setup_n_lin.limit_values[0].lo_limit'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['setup_n_lin.limit_values[0].lo_limit'])
        self.lines['setup_n_lin.limit_values[0].hi_limit'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['setup_n_lin.limit_values[0].hi_limit'])
        self.lines['setup_n_lin.limit_values[1].lo_limit'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['setup_n_lin.limit_values[1].lo_limit'])
        self.lines['setup_n_lin.limit_values[1].hi_limit'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['setup_n_lin.limit_values[1].hi_limit'])

        # Update the third subplot
        self.lines['par_mssg_s.par_func_code'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['par_mssg_s.par_func_code'])
        self.lines['parcode'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['parcode'])
        self.lines['pos'].set_data(self.PARAMETER['timestamps'], self.PARAMETER['pos'])

        # Adjust the axis limits to fit the data dynamically
        for ax in self.axes:
            ax.relim()
            ax.autoscale_view()

        plt.draw()  # Update the figure
        plt.pause(0.1)  # Allow the GUI to update

    def flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Flatten a nested dictionary, including lists of dictionaries, using dot notation.
        
        Args:
            d (dict): The dictionary to flatten.
            parent_key (str, optional): The prefix key for recursive flattening.
            sep (str, optional): The separator between keys. Defaults to '.'.
        
        Returns:
            dict: The flattened dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, sub_item in enumerate(v):
                    if isinstance(sub_item, dict):
                        items.extend(self.flatten_dict(sub_item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", sub_item))
            else:
                items.append((new_key, v))
        return dict(items)

    def get_parameter_dict(self, parameter: Parameter) -> dict:
        """
        Convert a Parameter object into a dictionary, including nested attributes.

        Args:
            parameter (Parameter): The Parameter object to convert.

        Returns:
            dict: A dictionary representation of the parameter.
        """
        parameter_dict = {
            'par_udp': parameter.par_udp.__dict__,
            'ext_par_udp': parameter.ext_par_udp.__dict__,
            'setup_n_lin': parameter.setup_n_lin.__dict__,
            'par_mssg_s': parameter.par_mssg_s.__dict__,
            'par_type': parameter.par_type,
            'parcode': parameter.parcode,
            'pos': parameter.pos,
        }

        # Flatten lists of objects within the parameter attributes
        for key, value in parameter_dict['setup_n_lin'].items():
            if isinstance(value, list) and all(isinstance(item, LimitValues) for item in value):
                parameter_dict['setup_n_lin'][key] = [item.__dict__ for item in value]
        for key, value in parameter_dict['par_mssg_s'].items():
            if isinstance(value, list) and all(isinstance(item, ParameterMessage) for item in value):
                parameter_dict['par_mssg_s'][key] = [item.__dict__ for item in value]

        return parameter_dict

    async def collect_data(self):
        """
        Asynchronous generator that simulates real-time data collection from the DataParser.

        Yields:
            Parameter: The next Parameter object from the data source.
        """
        data_parser = DataParser('Python_Practice/device_4.txt')
        data_parser.parse_data()
        for parameter in data_parser.parameters:
            yield parameter
            await asyncio.sleep(0.5)  # Simulate delay between data updates

    async def data_collector(self):
        """
        Continuously collect data, update the PARAMETER dictionary, and update the plot in real-time.
        """
        async for new_data in self.collect_data():
            parameter = new_data
            parameter_dict = self.get_parameter_dict(parameter)

            timestamp = time.time()
            flattened_data = self.flatten_dict(parameter_dict)

            for key in self.PARAMETER.keys():
                if key == 'timestamps':
                    continue
                self.PARAMETER[key].append(flattened_data.get(key, None))

            self.PARAMETER['timestamps'].append(timestamp)
            self.update_plot()

    async def run(self):
        """
        Run the real-time data collection and plotting.
        """
        plt.ion()
        while True:
            await self.data_collector()


# Main execution
if __name__ == "__main__":
    real_time_plotter = RealTimePlotter()
    asyncio.run(real_time_plotter.run())
