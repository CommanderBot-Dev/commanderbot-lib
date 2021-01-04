# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Updated license year

## [0.4.0] - 2021-01-03

### Changed

- Adjusted the way package extras are named

## [0.3.0] - 2020-10-30

### Added

- Implemented `VersionedCachedStore` which uses a `VersionedFileDatabase` to persist simple, versioned data
  - This can be used by extensions to maintain a simple, versioned file-based database in a standard, consistent manner
  - Current supported implementations of `VersionedFileDatabase` include `JsonVersionedFileDatabase` for JSON files and `YamlVersionedFileDatabase` for YAML files

## [0.2.0] - 2020-09-29

### Changed

- Updated to discord.py version 1.5.0

## [0.1.0] - 2020-09-24

### Added

- Implemented basic utilities for creating configurable, persistent discord.py CommanderBot extensions

[unreleased]: https://github.com/CommanderBot-Dev/commanderbot-lib/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/CommanderBot-Dev/commanderbot-lib/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/CommanderBot-Dev/commanderbot-lib/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/CommanderBot-Dev/commanderbot-lib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CommanderBot-Dev/commanderbot-lib/releases/tag/v0.1.0
