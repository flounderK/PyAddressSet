from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Optional, Generator

class Address:
    def compare_to(self, other: 'Address') -> int:
        pass

    def subtract(self, other: 'Address') -> int:
        pass

    def next(self) -> 'Address':
        pass

    def previous(self) -> 'Address':
        pass

class AddressRange:
    def get_min_address(self) -> Address:
        pass

    def get_max_address(self) -> Address:
        pass

    def contains(self, addr: Address) -> bool:
        pass

    def get_length(self) -> int:
        pass

class AddressRangeIterator(Iterator[AddressRange]):
    pass

class AddressIterator(Iterator[Address]):
    pass

class AddressSet:
    def add(self, *args):
        pass

class AddressSetView(ABC):
    @abstractmethod
    def contains(self, *args) -> bool:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def get_min_address(self) -> Optional[Address]:
        pass

    @abstractmethod
    def get_max_address(self) -> Optional[Address]:
        pass

    @abstractmethod
    def get_num_address_ranges(self) -> int:
        pass

    @abstractmethod
    def get_address_ranges(self, forward: Optional[bool] = None) -> AddressRangeIterator:
        pass

    @abstractmethod
    def get_addresses(self, start: Optional[Address] = None, forward: bool = True) -> AddressIterator:
        pass

    @abstractmethod
    def get_num_addresses(self) -> int:
        pass

    @abstractmethod
    def intersects(self, *args) -> bool:
        pass

    @abstractmethod
    def intersect(self, view: 'AddressSetView') -> AddressSet:
        pass

    @abstractmethod
    def intersect_range(self, start: Address, end: Address) -> AddressSet:
        pass

    @abstractmethod
    def union(self, addr_set: 'AddressSetView') -> AddressSet:
        pass

    @abstractmethod
    def subtract(self, addr_set: 'AddressSetView') -> AddressSet:
        pass

    @abstractmethod
    def xor(self, addr_set: 'AddressSetView') -> AddressSet:
        pass

    @abstractmethod
    def has_same_addresses(self, view: 'AddressSetView') -> bool:
        pass

    @abstractmethod
    def get_first_range(self) -> Optional[AddressRange]:
        pass

    @abstractmethod
    def get_last_range(self) -> Optional[AddressRange]:
        pass

    @abstractmethod
    def get_range_containing(self, address: Address) -> Optional[AddressRange]:
        pass

    @abstractmethod
    def find_first_address_in_common(self, other: 'AddressSetView') -> Optional[Address]:
        pass

    def get_address_count_before(self, address: Address) -> int:
        count = 0
        for range_ in self.get_address_ranges():
            if range_.get_min_address().compare_to(address) > 0:
                return count
            elif range_.contains(address):
                count += address.subtract(range_.get_min_address())
                return count
            count += range_.get_length()
        return count

    @staticmethod
    def trim_start(set_: 'AddressSetView', addr: Address) -> 'AddressSetView':
        trimmed_set = AddressSet()
        for range_ in set_.get_address_ranges():
            min_addr = range_.get_min_address()
            max_addr = range_.get_max_address()
            if min_addr.compare_to(addr) > 0:
                trimmed_set.add(range_)
            elif max_addr.compare_to(addr) > 0:
                trimmed_set.add(addr.next(), max_addr)
        return trimmed_set

    @staticmethod
    def trim_end(set_: 'AddressSetView', addr: Address) -> 'AddressSetView':
        trimmed_set = AddressSet()
        for range_ in set_.get_address_ranges():
            min_addr = range_.get_min_address()
            max_addr = range_.get_max_address()
            if max_addr.compare_to(addr) < 0:
                trimmed_set.add(range_)
            elif min_addr.compare_to(addr) < 0:
                trimmed_set.add(min_addr, addr.previous())
        return trimmed_set

    def __iter__(self) -> Iterator[AddressRange]:
        return self.get_address_ranges()
