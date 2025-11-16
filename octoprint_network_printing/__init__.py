# coding=utf-8
from __future__ import absolute_import

import serial
import logging
import socket
from typing import List
from urllib.parse import urlparse

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

        # check for network uri
        if "://" not in port:
            return None

        # Parse the URL to extract hostname and port
        try:
            parsed = urlparse(port)
            hostname = parsed.hostname
            port_number = parsed.port
            
            if not hostname or not port_number:
                error_msg = f"Invalid URL format: {port} (missing hostname or port)"
                self._logger.error(error_msg)
                machinecom_self._dual_log(error_msg, level=logging.ERROR)
                return None
            
            # Test DNS resolution and TCP connectivity with timeout
            connection_timeout = min(timeout_s, 5)  # Cap at 5 seconds for connection attempt
            self._logger.debug(f"Testing connection to {hostname}:{port_number} with {connection_timeout}s timeout")
            
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(connection_timeout)
            
            try:
                test_socket.connect((hostname, port_number))
                test_socket.close()
                self._logger.debug(f"Pre-connection test successful for {hostname}:{port_number}")
            except socket.gaierror as e:
                error_msg = f"DNS resolution failed for {hostname}: {e}"
                self._logger.error(error_msg)
                machinecom_self._dual_log(error_msg, level=logging.ERROR)
                machinecom_self._dual_log(
                    "Aborting connection attempt due to DNS failure",
                    level=logging.ERROR,
                )
                return None
            except socket.timeout:
                error_msg = f"Connection timeout after {connection_timeout}s to {hostname}:{port_number}"
                self._logger.error(error_msg)
                machinecom_self._dual_log(error_msg, level=logging.ERROR)
                machinecom_self._dual_log(
                    "Aborting connection attempt due to timeout",
                    level=logging.ERROR,
                )
                return None
            except OSError as e:
                error_msg = f"Connection refused to {hostname}:{port_number}: {e}"
                self._logger.error(error_msg)
                machinecom_self._dual_log(error_msg, level=logging.ERROR)
                machinecom_self._dual_log(
                    "Aborting connection attempt - host unreachable or port closed",
                    level=logging.ERROR,
                )
                return None
                
        except Exception as e:
            error_msg = f"Failed to parse URL {port}: {e}"
            self._logger.error(error_msg)
            machinecom_self._dual_log(error_msg, level=logging.ERROR)
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
            self._logger.error(f"Failed to establish serial connection to {port}: {e}")
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
