"""
Created 2023-12-24

@author: wf
"""
from nicegui import ui, run
from ceurws.wikidatasync import DblpEndpoint
from ngwidgets.progress import NiceguiProgressbar

class Admin:
    """
    Administration panel for managing DBLP endpoint and cache.

    Attributes:
        webserver: A server instance on which the admin panel is running.
        endpoint_url: The URL of the DBLP SPARQL endpoint to be used.
        endpoint: An instance of DblpEndpoint initialized with endpoint_url.
    """
    
    def __init__(self, webserver, endpoint_url: str = "https://qlever.cs.uni-freiburg.de/api/dblp/query"):
        """
        Initializes the Admin panel with given webserver and endpoint URL.

        Args:
            webserver: The server instance on which the admin panel is running.
            endpoint_url: The URL for the DBLP SPARQL endpoint, defaults to "https://qlever.cs.uni-freiburg.de/api/dblp/query".
        """
        self.webserver = webserver
        self.endpoint_url = None
        self.force_query = False
        self.set_endpoint(endpoint_url)
        # Initialize with the given endpoint URL
        self.setup()
        
    def set_endpoint(self,url):
        if self.endpoint_url is None or url!=self.endpoint_url: 
            self.endpoint_url = url  # Store the given or default endpoint URL
            self.endpoint = DblpEndpoint(self.endpoint_url) 
        
    def setup(self):
        """
        Sets up the UI elements of the Admin panel.
        """
        with ui.card() as self.card:
            with ui.row():
                ui.label('DBLP SPARQL Endpoint URL:')
                self.endpoint_input = ui.input(value=self.endpoint_url, on_change=self.update_endpoint_url).props("size=80")

            ui.label('Cache Status:')
            # Initialize the table with empty rows
            columns = [
                {'name': 'cache_name', 'label': 'Cache Name', 'field': 'cache_name'},
                {'name': 'size', 'label': 'Size (Bytes)', 'field': 'size'},
                {'name': 'entries', 'label': 'Entries', 'field': 'entries'},
                {'name': 'last_accessed', 'label': 'Last Accessed', 'field': 'last_accessed'},
            ]
            self.table = ui.table(columns=columns, rows=[], row_key='cache_name').classes('w-full')

            with ui.row():
                ui.button('Update Cache', on_click=self.update_cache)
                self.force_query_checkbox = ui.checkbox('Force Query').bind_value(self, "force_query")

            # Initialize the progress bar with total steps equal to the number of cache functions
            self.progress_bar = NiceguiProgressbar(total=len(self.endpoint.cache_functions), desc="Updating Caches", unit="cache")

            # Show initial cache status
            self.update_cache_info()
        
    def update_endpoint_url(self, event):
        """
        Updates the endpoint URL in the DblpEndpoint instance.

        Args:
            event: The event object containing the new URL value.
        """
        new_url = event.value
        self.set_endpoint(new_url)
                
    async def update_cache(self):
        """Triggers the long-running operation to refresh data in caches."""
        msg = f"Starting cache update for endpoint {self.endpoint_url} ..."
        ui.notify(msg)

        # Reset and display the progress bar
        self.progress_bar.reset()
        self.table.rows.clear()
        # Run the cache update process in the background
        await run.io_bound(self.background_cache_update)
        msg= f"Cache update finished"
        ui.notify(msg)

    def background_cache_update(self):
        """Background task to refresh data in caches."""
        for step, (cache_name, cache_function) in enumerate(self.endpoint.cache_functions.items(), start=1):
            # Call the corresponding function to refresh cache data
            cache_function(force_query=self.force_query)
            with self.card:
                ui.notify(f"{step}: {cache_name} updated")
                # Update progress bar after each cache is processed
                self.progress_bar.update(1)
                info = self.endpoint.json_cache_manager.get_cache_info(cache_name)
                self.update_cache_info_row(info)
                
    def update_cache_info_row(self,info):
        row = {
                'cache_name': info.name,
                'size': info.size if info else '❓',
                'entries': info.count if info else '❓',
                'last_accessed': info.last_accessed.strftime('%Y-%m-%d %H:%M:%S') if info and info.last_accessed else 'Never'
        }
        # Dynamically add each row to the table
        self.table.add_rows(row)
        
    def update_cache_info(self):
        """Retrieves and dynamically adds cache status rows to the table."""
        self.table.rows.clear()
        for cache_name in self.endpoint.cache_functions.keys():
            info = self.endpoint.json_cache_manager.get_cache_info(cache_name)
            self.update_cache_info_row(info)