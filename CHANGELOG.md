# Changelog

All notable changes to this project will be documented in this file.

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
