import sys
import os
import importlib
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QListWidget, 
    QListWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Plugin App")
        self.setGeometry(100, 100, 800, 600)

        # Load the CSS stylesheet
        self.load_stylesheet("styles.css")

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Create a tab widget for the sidebar
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # on_tab_changed event handler
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # Add the Home tab
        self.add_home_tab()

        # Add the Add-Ons tab
        self.add_addons_tab()

        # Load plugins
        self.plugins = self.load_plugins()
        self.plugin_states = {name: True for name in self.plugins}  # Track plugin states
        self.init_plugins()

        # Display plugin metadata in the Home tab
        self.display_plugin_metadata()

        # Start the metadata update timer
        self.metadata_timer = QTimer(self)
        self.metadata_timer.timeout.connect(self.update_plugin_METADATA)
        self.metadata_timer.start(1000)  # Update every 1000ms (1 second)

    def load_stylesheet(self, filename):
        """Load a CSS stylesheet from a file."""
        try:
            with open(filename, "r") as file:
                self.setStyleSheet(file.read())
        except Exception as e:
            print(f"Failed to load stylesheet: {e}")

    def add_home_tab(self):
        """Add the Home tab to the sidebar."""
        self.home_tab = QWidget()
        self.home_layout = QVBoxLayout(self.home_tab)
        self.home_layout.addWidget(QLabel("Installed Plugins:"))
        
        # Create a QListWidget to display plugin metadata
        self.plugin_list = QListWidget()
        self.home_layout.addWidget(self.plugin_list)

        self.tab_widget.addTab(self.home_tab, "Home")

    def add_addons_tab(self):
        """Add the Add-Ons tab to the sidebar."""
        self.addons_tab = QWidget()
        self.addons_layout = QVBoxLayout(self.addons_tab)
        self.addons_layout.addWidget(QLabel("Available Plugins:"))

        # Create a QListWidget to display available plugins
        self.addons_list = QListWidget()
        self.addons_layout.addWidget(self.addons_list)

        # Fetch and display available plugins
        self.fetch_available_plugins()

        self.tab_widget.addTab(self.addons_tab, "Add-Ons")

    def fetch_available_plugins(self):
        """Fetch available plugins from the remote repository."""
        try:
            # Fetch the plugin metadata from the remote JSON file
            response = requests.get("https://raw.githubusercontent.com/Faked2378/global-plugin-list/refs/heads/main/plugin-list.json")
            response.raise_for_status()  # Raise an error for bad status codes
            self.available_plugins = response.json()

            # Display the plugins in the Add-Ons tab
            self.display_available_plugins()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch plugins: {e}")

    def display_available_plugins(self):
        """Display available plugins in the Add-Ons tab."""
        self.addons_list.clear()  # Clear the list before adding items

        for plugin in self.available_plugins:
            # Create a widget for the plugin info and actions
            plugin_widget = QWidget()
            plugin_layout = QHBoxLayout(plugin_widget)

            # Add plugin info
            plugin_info = QLabel(f"{plugin['name']} ({plugin['version']})\n{plugin['description']}")
            plugin_layout.addWidget(plugin_info)

            # Add Install button
            install_button = QPushButton("Install")
            install_button.clicked.connect(lambda _, p=plugin: self.install_plugin(p))
            install_button.setAutoDefault(False)  # Disable beep on button click
            plugin_layout.addWidget(install_button)

            # Add the widget to the QListWidget
            item = QListWidgetItem()
            item.setSizeHint(plugin_widget.sizeHint())
            self.addons_list.addItem(item)
            self.addons_list.setItemWidget(item, plugin_widget)

    def install_plugin(self, plugin):
        """Install a plugin from the remote repository."""
        try:
            # Disable the plugin if it's already installed
            if plugin["name"] in self.plugins:
                self.toggle_plugin(plugin["name"], None, quietly=True)  # Disable the plugin

            # Download the plugin file
            response = requests.get(plugin["download_url"])
            response.raise_for_status()

            # Save the plugin to the plugins folder
            plugins_folder = "plugins"
            if not os.path.exists(plugins_folder):
                os.makedirs(plugins_folder)

            plugin_filename = os.path.join(plugins_folder, f"{plugin['name'].lower().replace(' ', '_')}.py")
            if os.path.exists(plugin_filename):
                os.remove(plugin_filename)  # Remove the old version of the plugin

            with open(plugin_filename, "wb") as file:
                file.write(response.content)

            # Reload plugins
            self.plugins = self.load_plugins(refresh=True)
            self.plugin_states = {name: True for name in self.plugins}
            self.init_plugins()
            self.display_plugin_metadata()

            # Re-enable the plugin after installation
            if plugin["name"] in self.plugins:
                self.toggle_plugin(plugin["name"], None, quietly=True)  # Enable the plugin

            QMessageBox.information(self, "Plugin Installed", f"{plugin['name']} has been installed.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to install plugin: {e}")

    def update_plugin_METADATA(self):
        """Update the plugin metadata in case its code changes during runtime."""
        for plugin_name, plugin_module in self.plugins.items():
            if hasattr(plugin_module, "PLUGIN_METADATA"):
                plugin_metadata = plugin_module.PLUGIN_METADATA
                vers = plugin_metadata.get("version", "Unknown")
                desc = plugin_metadata.get("description", "No description available.")
                name = plugin_metadata.get("name", plugin_name)

                # Find the corresponding plugin widget in the Home tab
                for i in range(self.plugin_list.count()):
                    item = self.plugin_list.item(i)
                    widget = self.plugin_list.itemWidget(item)
                    if widget:
                        plugin_info_label = widget.findChild(QLabel)
                        if plugin_info_label and name in plugin_info_label.text():
                            plugin_info_label.setText(f"{name} ({vers})\n{desc}")
                            break

    def load_plugins(self, refresh=False): # if refresh is true then it won't do ANY window opening
        """Load plugins from the plugins folder."""
        plugins = {}
        plugins_folder = "plugins"
        if not os.path.exists(plugins_folder):
            os.makedirs(plugins_folder)

        for plugin_name in os.listdir(plugins_folder):
            if plugin_name.endswith(".py"):
                module_name = plugin_name[:-3]  # Remove .py
                try:
                    module = importlib.import_module(f"{plugins_folder}.{module_name}")
                    if hasattr(module, "PLUGIN_METADATA"):
                        module_name = module.PLUGIN_METADATA["name"]
                    if hasattr(module, "disable"):
                        plugins[module_name] = module
                    else:
                        if not refresh:
                            QMessageBox.warning(self, "Error", f"Plugin {module_name} does not have a disable function therefore is too unsafe to run.")
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")
        return plugins

    def init_plugins(self):
        """Initialize plugins after loading."""
        for plugin_name, plugin_module in self.plugins.items():
            try:
                if hasattr(plugin_module, "register"):
                    plugin_module.register(self)
                if hasattr(plugin_module, "get_plugins"):
                    plugin_module.get_plugins(self, self.plugins)
            except Exception as e:
                print(f"Failed to initialize plugin {plugin_name}: {e}")

    def display_plugin_metadata(self, refresh=False):
        """Display plugin metadata in the Home tab."""
        self.plugin_list.clear()  # Clear the list before adding items

        for plugin_name, plugin_module in self.plugins.items():
            # Get plugin metadata (if available)
            metadata = getattr(plugin_module, "PLUGIN_METADATA", {})
            name = metadata.get("name", plugin_name)
            description = metadata.get("description", "No description available.")
            version = metadata.get("version", "Unknown")

            # Create a widget for the plugin info and actions
            plugin_widget = QWidget()
            plugin_layout = QHBoxLayout(plugin_widget)

            # Add plugin info
            plugin_info = QLabel(f"{name} ({version})\n{description}")
            plugin_layout.addWidget(plugin_info)

            # Add Enable/Disable button
            enable_button = QPushButton("Disable" if self.plugin_states[plugin_name] else "Enable")
            enable_button.clicked.connect(lambda _, p=plugin_name, b=enable_button: self.toggle_plugin(p, b))
            enable_button.setAutoDefault(False)  # Disable beep on button click
            plugin_layout.addWidget(enable_button)

            # Add Configure button
            configure_button = QPushButton("Configure")
            configure_button.clicked.connect(lambda _, p=plugin_name: self.configure_plugin(p))
            configure_button.setAutoDefault(False)  # Disable beep on button click
            plugin_layout.addWidget(configure_button)

            # Add the widget to the QListWidget
            item = QListWidgetItem()
            item.setSizeHint(plugin_widget.sizeHint())
            self.plugin_list.addItem(item)
            self.plugin_list.setItemWidget(item, plugin_widget)

    def toggle_plugin(self, plugin_name, button, quietly=False):
        """Enable or disable a plugin."""
        plugin_module = self.plugins.get(plugin_name)
        if plugin_module:
            # Toggle the plugin's state
            self.plugin_states[plugin_name] = not self.plugin_states[plugin_name]
            new_state = self.plugin_states[plugin_name]
            print(f"Plugin {plugin_name} is now {new_state}")
            # Update the button text
            if button and button.text() != "Configure":
                if new_state and new_state != None:
                    button.setText("Disable")
                else:
                    button.setText("Enable")
            print(button.text())
            # Call the plugin's enable/disable methods (if they exist)
            if new_state:
                if hasattr(plugin_module, "enable"):
                    plugin_module.enable(self)
            else:
                if hasattr(plugin_module, "disable"):
                    plugin_module.disable(self)

            # Notify the user
            state = "enabled" if new_state else "disabled"
            if not quietly:
                QMessageBox.information(self, "Plugin Toggled", f"Plugin {plugin_name} has been {state}.")
        else:
            if not quietly:
                QMessageBox.warning(self, "Error", f"Plugin {plugin_name} not found.")

    def forceOffPlugin(self, plugin_name):
        """Forcefully disable a plugin."""
        plugin_module = self.plugins.get(plugin_name)
        if plugin_module:
            # Disable the plugin
            if hasattr(plugin_module, "disable"):
                plugin_module.disable(self)
            else:
                QMessageBox.warning(self, "Error", f"Plugin {plugin_name} does not have a disable method. Cannot Forcefully disable it.")

    def on_tab_changed(self, index):
        """Slot for handling tab changes."""
        current_tab = self.tab_widget.tabText(index)
        self.check_if_on_tab(current_tab)

    def check_if_on_tab(self, current_open_tab):
        """Give all plugins with this attribute the current open tab."""
        for plugin_name, plugin_module in self.plugins.items():
            if hasattr(plugin_module, "on_tab"):
                plugin_module.on_tab(current_open_tab)


    def configure_plugin(self, plugin_name):
        """Configure a plugin."""
        plugin_module = self.plugins.get(plugin_name)
        if plugin_module:
            # Check if the plugin has a configure method
            if hasattr(plugin_module, "configure"):
                # Create a dialog for the plugin's configuration UI
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Configure {plugin_name}")

                # Disable the beep sound when the dialog closes
                def closeEvent(event):
                    event.accept()  # Accept the close event without playing the beep
                dialog.closeEvent = closeEvent

                dialog_layout = QVBoxLayout(dialog)

                # Get the plugin's configuration widget
                config_widget = plugin_module.configure(self)
                dialog_layout.addWidget(config_widget)

                # Add OK and Cancel buttons
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)
                dialog_layout.addWidget(button_box)

                # Show the dialog
                if dialog.exec() == QDialog.Accepted:
                    # Save changes if the user clicks OK
                    if hasattr(plugin_module, "save_config"):
                        plugin_module.save_config(self)
                    QMessageBox.information(self, "Configuration Saved", f"Configuration for {plugin_name} has been saved.")
            else:
                QMessageBox.information(self, "No Configuration", f"Plugin {plugin_name} does not support configuration.")
        else:
            QMessageBox.warning(self, "Error", f"Plugin {plugin_name} not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())