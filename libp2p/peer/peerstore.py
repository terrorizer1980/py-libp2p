from typing import Any, Dict, List, Sequence

from multiaddr import Multiaddr

from libp2p.crypto.keys import KeyPair, PrivateKey, PublicKey

from .id import ID
from .peerdata import PeerData, PeerDataError
from .peerinfo import PeerInfo
from .peerstore_interface import IPeerStore


class PeerStore(IPeerStore):

    peer_data_map: Dict[ID, PeerData]

    def __init__(self) -> None:
        self.peer_data_map = {}

    def __create_or_get_peer_data(self, peer_id: ID) -> PeerData:
        """
        Returns the peer data for peer_id or creates a new peer data (and
        stores it in peer_data_map) if peer data for peer_id does not yet
        exist.

        :param peer_id: peer ID
        :return: peer data
        """
        if peer_id in self.peer_data_map:
            return self.peer_data_map[peer_id]
        data = PeerData()
        self.peer_data_map[peer_id] = data
        return data

    def peer_info(self, peer_id: ID) -> PeerInfo:
        """
        :param peer_id: peer ID to get info for
        :return: peer info object
        """
        if peer_id in self.peer_data_map:
            peer_data = self.peer_data_map[peer_id]
            return PeerInfo(peer_id, peer_data.get_addrs())
        raise PeerStoreError("peer ID not found")

    def get_protocols(self, peer_id: ID) -> List[str]:
        """
        :param peer_id: peer ID to get protocols for
        :return: protocols (as list of strings)
        :raise PeerStoreError: if peer ID not found
        """
        if peer_id in self.peer_data_map:
            return self.peer_data_map[peer_id].get_protocols()
        raise PeerStoreError("peer ID not found")

    def add_protocols(self, peer_id: ID, protocols: Sequence[str]) -> None:
        """
        :param peer_id: peer ID to add protocols for
        :param protocols: protocols to add
        """
        peer_data = self.__create_or_get_peer_data(peer_id)
        peer_data.add_protocols(list(protocols))

    def set_protocols(self, peer_id: ID, protocols: Sequence[str]) -> None:
        """
        :param peer_id: peer ID to set protocols for
        :param protocols: protocols to set
        """
        peer_data = self.__create_or_get_peer_data(peer_id)
        peer_data.set_protocols(list(protocols))

    def peer_ids(self) -> List[ID]:
        """
        :return: all of the peer IDs stored in peer store
        """
        return list(self.peer_data_map.keys())

    def get(self, peer_id: ID, key: str) -> Any:
        """
        :param peer_id: peer ID to get peer data for
        :param key: the key to search value for
        :return: value corresponding to the key
        :raise PeerStoreError: if peer ID or value not found
        """
        if peer_id in self.peer_data_map:
            try:
                val = self.peer_data_map[peer_id].get_metadata(key)
            except PeerDataError as error:
                raise PeerStoreError(error)
            return val
        raise PeerStoreError("peer ID not found")

    def put(self, peer_id: ID, key: str, val: Any) -> None:
        """
        :param peer_id: peer ID to put peer data for
        :param key:
        :param value:
        """
        # <<?>>
        # This can output an error, not sure what the possible errors are
        peer_data = self.__create_or_get_peer_data(peer_id)
        peer_data.put_metadata(key, val)

    def add_addr(self, peer_id: ID, addr: Multiaddr, ttl: int) -> None:
        """
        :param peer_id: peer ID to add address for
        :param addr:
        :param ttl: time-to-live for the this record
        """
        self.add_addrs(peer_id, [addr], ttl)

    def add_addrs(self, peer_id: ID, addrs: Sequence[Multiaddr], ttl: int) -> None:
        """
        :param peer_id: peer ID to add address for
        :param addrs:
        :param ttl: time-to-live for the this record
        """
        # Ignore ttl for now
        peer_data = self.__create_or_get_peer_data(peer_id)
        peer_data.add_addrs(list(addrs))

    def addrs(self, peer_id: ID) -> List[Multiaddr]:
        """
        :param peer_id: peer ID to get addrs for
        :return: list of addrs
        :raise PeerStoreError: if peer ID not found
        """
        if peer_id in self.peer_data_map:
            return self.peer_data_map[peer_id].get_addrs()
        raise PeerStoreError("peer ID not found")

    def clear_addrs(self, peer_id: ID) -> None:
        """
        :param peer_id: peer ID to clear addrs for
        """
        # Only clear addresses if the peer is in peer map
        if peer_id in self.peer_data_map:
            self.peer_data_map[peer_id].clear_addrs()

    def peers_with_addrs(self) -> List[ID]:
        """
        :return: all of the peer IDs which has addrs stored in peer store
        """
        # Add all peers with addrs at least 1 to output
        output: List[ID] = []

        for peer_id in self.peer_data_map:
            if len(self.peer_data_map[peer_id].get_addrs()) >= 1:
                output.append(peer_id)
        return output

    def add_pubkey(self, peer_id: ID, pubkey: PublicKey) -> None:
        """
        :param peer_id: peer ID to add public key for
        :param pubkey:
        """
        peer_data = self.__create_or_get_peer_data(peer_id)
        # TODO: Check if pubkey matches peer ID
        peer_data.add_pubkey(pubkey)

    def pubkey(self, peer_id: ID) -> PublicKey:
        """
        :param peer_id: peer ID to get public key for
        :return: public key of the peer
        :raise PeerStoreError: if peer ID or peer pubkey not found
        """
        if peer_id in self.peer_data_map:
            peer_data = self.peer_data_map[peer_id]
            try:
                pubkey = peer_data.get_pubkey()
            except PeerDataError:
                raise PeerStoreError("peer pubkey not found")
            return pubkey
        raise PeerStoreError("peer ID not found")

    def add_privkey(self, peer_id: ID, privkey: PrivateKey) -> None:
        """
        :param peer_id: peer ID to add private key for
        :param privkey:
        """
        peer_data = self.__create_or_get_peer_data(peer_id)
        # TODO: Check if privkey matches peer ID
        peer_data.add_privkey(privkey)

    def privkey(self, peer_id: ID) -> PrivateKey:
        """
        :param peer_id: peer ID to get private key for
        :return: private key of the peer
        :raise PeerStoreError: if peer ID or peer privkey not found
        """
        if peer_id in self.peer_data_map:
            peer_data = self.peer_data_map[peer_id]
            try:
                privkey = peer_data.get_privkey()
            except PeerDataError:
                raise PeerStoreError("peer privkey not found")
            return privkey
        raise PeerStoreError("peer ID not found")

    def add_key_pair(self, peer_id: ID, key_pair: KeyPair) -> None:
        """
        :param peer_id: peer ID to add private key for
        :param key_pair:
        """
        self.add_pubkey(key_pair.public_key)
        self.add_privkey(key_pair.private_key)


class PeerStoreError(KeyError):
    """Raised when peer ID is not found in peer store."""
