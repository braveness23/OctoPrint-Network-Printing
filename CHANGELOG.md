# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-11-16

### Added

- Pre-connection validation with DNS resolution test
- Configurable connection timeout (capped at 5 seconds)
- Detailed error messages for DNS, timeout, and connection failures
- URL parsing validation to catch malformed addresses early

### Fixed

- Connection attempts no longer hang indefinitely on DNS failures
- Fast-fail on unreachable hosts instead of waiting for OctoPrint's retry loop
- Improved error reporting for network connectivity issues

## [0.1.1] - 2025-11-16

### Added

- Error handling for network connection failures
- Better logging with connection status messages
- Debug logging for port discovery

### Changed

- Updated repository URLs to forked repository (braveness23)
- Improved error messages for failed connections
- Cleaned up unused imports

### Fixed

- Removed unused imports (os, get_os, set_close_exec)
- Added proper exception handling in serial factory

## [0.1.0] - Initial Release

### Added

- RFC2217 protocol support for network serial connections
- Raw TCP socket protocol support (compatible with ESP3D)
- Integration with OctoPrint's serial port system
- Automatic software update checking via GitHub releases
