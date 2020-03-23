# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic
Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- Revert commit which was embeding Video-JS player as it breaks build
  and should not be necessary.

## [0.6.0] - 2020-02-13

### Added

- Implement experimental support for BokeCC video provider (legacy feature for
  developped 3 years ago for a white brand) See openfun/libcast-xblock#8

## [0.5.0] - 2018-03-21

### Added

- Add a CHANGELOG (yay)
- Add packaging good practices: all package configuration stands in the
  `setup.cfg` file
- Automate the packaging workflow with CircleCI

### Changed

- Update installation instructions in the README
