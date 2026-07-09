# hydro-station-mapping

<p align="center">
  <a href="https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE">
    <img src="https://github.com/ecmwf/codex/raw/refs/heads/main/ESEE/foundation_badge.svg" alt="ECMWF Software EnginE">
  </a>
  <a href="https://github.com/ecmwf/codex/raw/refs/heads/main/Project Maturity">
    <img src="https://github.com/ecmwf/codex/raw/refs/heads/main/Project Maturity/emerging_badge.svg" alt="Maturity Level">
  </a>
  <a href="https://opensource.org/licenses/apache-2-0">
    <img src="https://img.shields.io/badge/Licence-Apache 2.0-blue.svg" alt="Licence">
  </a>
  <a href="https://github.com/ecmwf/hydro-station-mapping/releases">
    <img src="https://img.shields.io/github/v/release/ecmwf/hydro-station-mapping?color=purple&label=Release" alt="Latest Release">
  </a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a>
  •
  <a href="#installation">Installation</a>
  •
  <a href="https://hydro-station-mapping.readthedocs.io">Documentation</a>
</p>

> \[!IMPORTANT\]
> This software is **Emerging** and subject to ECMWF's guidelines on [Software Maturity](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity).

**hydro-station-mapping** is a Python package and commandline tool for conducting automatic mapping of station locations onto river networks.

## Quick Start

Either use the commandline utility:
```bash
hydro-station-mapping config.yml
```

or the Python interface directly:
```python
from hydro_station_mapping import mapper

mapped_df = mapper(config)
```

## Installation

```bash
pip install git+ssh://git@github.com/ecmwf/hydro-station-mapping.git@main
```

## License
[Apache License 2.0](LICENSE) In applying this licence, ECMWF does not waive the privileges and immunities granted to it by virtue of its status as an intergovernmental organisation nor does it submit to any jurisdiction.
