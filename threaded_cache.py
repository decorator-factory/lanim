from dataclasses import dataclass
import threading
from typing import Callable, Generic, Hashable, Union, TypeVar


A = TypeVar("A")
K = TypeVar("K", bound=Hashable)


@dataclass(frozen=True)
class InProgress:
    lock: threading.Lock


@dataclass(frozen=True)
class Available(Generic[A]):
    result: A


CacheStatus = Union[InProgress, Available[A]]


class ThreadedCache(Generic[K, A]):
    """
    A cache for long-running jobs that shouldn't generally be repeated.

    E.g. if thread 1 and thread 2 request the same item, it should only be
    computed once, even if thread 2 "ordered" it later.
    """

    _factory: Callable[[K], A]
    _store: dict[K, CacheStatus[A]]
    _read_lock: threading.Lock

    def __init__(self, factory: Callable[[K], A]):
        self._factory = factory
        self._store = {}
        self._read_lock = threading.Lock()

    def __contains__(self, k: K) -> bool:
        return k in self._store

    def __getitem__(self, k: K) -> A:
        self._read_lock.acquire()
        try:
            value = self._store.get(k)
            if value is None:
                return self._fill_cache(k)
            elif isinstance(value, InProgress):
                value.lock.acquire()
                value.lock.release()
                new_value = self._store.get(k)
                if not isinstance(new_value, Available):
                    raise RuntimeError(f"Getting key {k!r} failed :-(")
                return new_value.result
            elif isinstance(value, Available):
                return value.result
            else:
                assert False
        finally:
            if self._read_lock.locked():
                self._read_lock.release()

    def _fill_cache(self, k: K) -> A:
        lock = threading.Lock()
        self._store[k] = InProgress(lock)
        if self._read_lock.locked():
            self._read_lock.release()
        lock.acquire()
        try:
            new_value = self._factory(k)
        except:
            del self._store[k]
            lock.release()
            raise
        self._store[k] = Available(new_value)
        lock.release()
        return new_value


def threaded_cache(factory: Callable[[K], A]) -> Callable[[K], A]:
    return ThreadedCache(factory).__getitem__
