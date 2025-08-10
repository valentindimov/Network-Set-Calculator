#!/usr/bin/env python3

from argparse import ArgumentParser
from ipaddress import IPv4Network, IPv6Network, collapse_addresses, ip_network
from itertools import chain

class NetworkSet:
    """Represents a set of IPv4 and IPv6 networks."""

    def __init__(self):
        self._v4Networks: set[IPv4Network] = set()
        self._v6Networks: set[IPv6Network] = set()

    def getNetworks(self) -> tuple[list[IPv4Network], list[IPv6Network]]:
        """Get an iterable over the IPv4 and IPv6 networks contained in the set."""
        # Delay actually collapsing the networks until the very end, for efficiency's sake
        self._v4Networks = set(collapse_addresses(self._v4Networks))
        self._v6Networks = set(collapse_addresses(self._v6Networks))
        return (list(self._v4Networks), list(self._v6Networks))

    def includeNetwork(self, networkToInclude: IPv4Network | IPv6Network) -> None:
        """Include a network into the set."""
        # We just add the address to the correct network set - we will collapse the addresses later in getNetworks()
        (self._v4Networks if isinstance(networkToInclude, IPv4Network) else self._v6Networks).add(networkToInclude)
    
    def excludeNetwork(self, networkToExclude: IPv4Network | IPv6Network) -> None:
        """Exclude a network from the set."""
        # Determine the network set to use.
        networks = self._v4Networks if isinstance(networkToExclude, IPv4Network) else self._v6Networks
        # Remove all networks which are subnets of the network to exclude
        adjustedNetworks = filter(lambda n: not networkToExclude.supernet_of(n), networks)
        # Replace all networks which are supernets of the network to exclude with the output of address_exclude(). The other networks are passed as-is.
        adjustedNetworks = chain(*map(lambda n: (n.address_exclude(networkToExclude) if n.supernet_of(networkToExclude) else [n]), adjustedNetworks))
        # Replace the network set with the result of the above computation
        networks.clear()
        networks.update(adjustedNetworks)

if __name__ == "__main__":
    # Argument parsing
    parser = ArgumentParser(prog="Route set calculator", epilog="Copyright (c) 2025 Valentin Dimov. Available under the MIT license: https://mit-license.org/")
    parser.add_argument("-i", "--include", action="append", type=str, dest="included", 
                        help="Include IP range (can be specified multiple times). If this option is never specified, 0.0.0.0/0 (all IPv4 addresses) is included")
    parser.add_argument("-e", "--exclude", action="append", type=str, dest="excluded",
                        help="Exclude IP range (can be specified multiple times)")
    parser.add_argument("--exclude-private-ipv4-ranges", action="store_true", dest="excludePrivateIPv4Ranges", 
                        help="Exclude private/non-routable IPv4 ranges")
    parser.add_argument("--exclude-private-ipv6-ranges", action="store_true", dest="excludePrivateIPv6Ranges", 
                        help="Exclude private/non-routable IPv6 ranges")
    parser.add_argument("-I", "--include-override", action="append", type=str, dest="overrideIncluded", default=[],
                        help="Include IP range even if it's part of an excluded range (can be specified multiple times)")
    args = parser.parse_args()

    # Argument processing. In the end we want to determine what addresses to include, exclude, and include despite the exclusions
    if args.included is None:
        args.included = ["0.0.0.0/0"]
    if args.excluded is None:
        args.excluded = []
    if args.overrideIncluded is None:
        args.overrideIncluded = [] 
    includedRanges = [ip_network(i.strip(), strict=False) for i in args.included]
    excludedRanges = [ip_network(i.strip(), strict=False) for i in args.excluded]
    overrideIncludedRanges = [ip_network(i.strip(), strict=False) for i in args.overrideIncluded]
    if args.excludePrivateIPv4Ranges:
        excludedRanges += [
            ip_network("10.0.0.0/8"), # private
            ip_network("127.0.0.0/8"), # loopback
            ip_network("172.16.0.0/12"), # private
            ip_network("192.168.0.0/16"), # private
            ip_network("169.254.0.0/16"), # APIPA
        ]
    if args.excludePrivateIPv6Ranges:
        excludedRanges += [
            ip_network("fc00::/7"), # Private
            ip_network("ff00::/8"), # Multicast
            ip_network("fe80::/10"), # Link-local
            # Excluding ::1/128 is not necessary as it's already part of the routing tables in Linux
        ]
    
    # Now aggregate all the inclusions and exclusions into a NetworkSet, and get the final lists of IPv4 and IPv6 networks
    s=NetworkSet()
    for p in includedRanges:
        s.includeNetwork(p)
    for p in excludedRanges:
        s.excludeNetwork(p)
    for p in overrideIncludedRanges:
        s.includeNetwork(p)
    (v4Nets, v6Nets) = s.getNetworks()
    
    # Sort the network lists by prefix length (shorter prefixes first), then print them (IPv4 before IPv6)
    v4Nets.sort(key = lambda s: s.prefixlen)
    v6Nets.sort(key = lambda s: s.prefixlen)
    print(",".join(chain((str(n) for n in v4Nets), (str(n) for n in v6Nets))))
