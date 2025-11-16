# coding=utf-8
from __future__ import absolute_import

import serial
import logging
from typing import List

import octoprint.plugin
from octoprint.settings import settings
from octoprint.util.comm import BufferedReadlineWrapper


class NetworkPrintingPlugin(
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
):
    def get_port_names(self, candidates):
        """Return list of network ports from additional serial ports configuration"""
        additionalPorts = settings().get(["serial", "additionalPorts"])
        network_ports = [port for port in additionalPorts if "://" in port]
        self._logger.debug(f"Discovered network ports: {network_ports}")
        return network_ports

    def get_serial_factory(
        self, machinecom_self, port: str, baudrate: int, timeout_s: int
    ):
        self._logger.info(
            f"Attempting network connection: port={port}, baudrate={baudrate}, timeout={timeout_s}s"
        )

        # check for rfc2217 uri
        if "://" not in port:
            return None

        # connect to network serial port
        machinecom_self._dual_log(
            "Connecting to port {}, baudrate {}".format(port, baudrate),
            level=logging.INFO,
        )

        serial_port_args = {
            "baudrate": baudrate,
            "timeout": timeout_s,
            "write_timeout": 0,
        }

        try:
            serial_obj = serial.serial_for_url(str(port), **serial_port_args)
            self._logger.info(f"Successfully connected to {port}")
            return BufferedReadlineWrapper(serial_obj)
        except Exception as e:
            self._logger.error(f"Failed to connect to {port}: {e}")
            machinecom_self._dual_log(
                f"Network connection failed: {e}",
                level=logging.ERROR,
            )
            return None

    def get_update_information(self):
        # See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html for details.
        return dict(
            network_printing=dict(
                displayName="Network-printing Plugin",
                displayVersion=self._plugin_version,
                # version check: github repository
                type="github_release",
                user="braveness23",
                repo="OctoPrint-Network-Printing",
                current=self._plugin_version,
                # update method: pip
                pip="https://github.com/braveness23/OctoPrint-Network-Printing/archive/{target_version}.zip",
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py.
__plugin_name__ = "Network-Printing Plugin"
__plugin_pythoncompat__ = ">=3,<4"  # only python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NetworkPrintingPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.transport.serial.factory": __plugin_implementation__.get_serial_factory,
        "octoprint.comm.transport.serial.additional_port_names": __plugin_implementation__.get_port_names,
    }
