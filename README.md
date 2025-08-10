# Network-Set-Calculator
[network-set-calculator.py](./network-set-calculator.py) is a small Python script that computes sets of IP subnets (e.g. for routing tables or WireGuard AllowedIPs settings) using include and exclude operations.
The script requires Python 3 to be installed on your machine - however, it only uses the Python standard library, so it has no further dependenies.

## Usage:
Launch the script using Python 3 (`python`, `python3`, or execute it directly) on your command line.
Supported command-line options include:
```
-h, --help
    Display a help message and exit
-i INCLUDED, --include INCLUDED
    Include IP range (can be specified multiple times). If this option is never specified, 0.0.0.0/0 (all IPv4 addresses) is included
-e EXCLUDED, --exclude EXCLUDED
    Exclude IP range (can be specified multiple times)
--exclude-private-ipv4-ranges
    Exclude private/non-routable IPv4 ranges
--exclude-private-ipv6-ranges
    Exclude private/non-routable IPv6 ranges
-I OVERRIDEINCLUDED, --include-override OVERRIDEINCLUDED
    Include IP range even if it's part of an excluded range (can be specified multiple times)
```
The output (i.e. the final list of subnets) is printed to the console.

## License and Copyright
This script is licensed under the MIT license (see [LICENSE](./LICENSE)).

Copyright (c) 2025 Valentin Dimov.
