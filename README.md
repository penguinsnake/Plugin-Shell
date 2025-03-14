# Plugin Shell

Plugin Shell is a lightweight and extensible framework designed to do nothing on its own—but with plugins, it can do anything! Whether you're a developer looking to create custom plugins or a user wanting to enhance functionality, Plugin Shell provides a simple and flexible platform for endless possibilities.
Features

   * Core Simplicity: The base program does nothing, offering a clean slate for customization.

   * Plugin Extensibility: Add plugins to extend functionality—plugins can be literally anything!

   * Easy Plugin Management:

        Install, enable, disable, and configure plugins via a user-friendly GUI.

        Fetch and install plugins from a remote repository.

   * Developer-Friendly:

        Simple plugin API for creating custom plugins.

        Support for plugin metadata (name, description, version).

   * Cross-Platform: Built with Python and PySide6, it works on Windows, macOS, and Linux. (although only devtested on windows.)

# Getting Started
# # For Users

   * Download the Latest Release:

      1) Visit the Releases Page and download the latest version.

   * Run the Program:

      1) Extract the downloaded files and navigate to the project directory:
        1a. bash
        1b. Copy

        1c. cd PluginShell

      2) Run the program:
        2a. bash
        2b. Copy

        2c. python main.py

   * Install Plugins:

      * Use the built-in interface to browse and install plugins from the Global Plugin List.

      * Alternatively, place your plugin files in the plugins directory.

# # For Developers

   * Create a Plugin:

      1. Create a Python file in the plugins directory.

      2. Define your plugin's functionality and metadata:

         PLUGIN_METADATA = {
            "name": "My Awesome Plugin",
            "version": "1.0",
            "description": "This plugin does something amazing!"
         }

         def enable(app):
            print("Plugin enabled!")

         def disable(app):
            print("Plugin disabled!")

   * Test Your Plugin:

        1. Run Plugin Shell and ensure your plugin appears in the "Installed Plugins" tab.

        2. Use the "Enable/Disable" and "Configure" buttons to interact with your plugin.

   * Share Your Plugin:

        * Submit your plugin to the Global Plugin List via a pull request (or just pull the json file).


# # We welcome contributions from the community! Here's how you can help:

   * Core Improvements: Submit pull requests to this repository.

   * Plugins: Add your plugins to the Global Plugin List.

   * Bug Reports: Open an issue if you encounter any problems.

# # Before contributing, please read our Contribution Guidelines.
# License:

This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgments:

   * CreatorLibs: For creating and maintaining Plugin Shell.

   * Contributors: Thanks to everyone who has contributed plugins or improvements.

   * Users: Whether you're a current or future user, thank you for making Plugin Shell possible!

# # FAQ

What is Plugin Shell?

* Plugin Shell is a framework that allows you to extend its functionality through plugins. By itself, it does nothing—but with plugins, it can do anything!

How do I create a plugin?

* Check out the Developer Guide above or refer to the Plugin Template.

Can I suggest a feature or report a bug?

* Yes! Open an issue on the GitHub Issues Page.
