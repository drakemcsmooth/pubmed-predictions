from __future__ import annotations

from typing import Optional, Dict, Set
from pathlib import Path
from collections import Counter
import h5py

import logging

log = logging.getLogger(__name__)


class Abstract:
    SUFFIX = "h5"

    DEFAULT_CATEGORY = "text"

    _KEY_PMID = "pmid"

    def __init__(self, pmid: int, **fields: str):
        self.pmid = int(pmid)
        self.fields = fields

        self.counts: Optional[Counter[str]] = Counter()

    @property
    def terms(self) -> Set[str]:
        """Obtain the terms comprising the abstract's language model"""
        return set(self.counts.keys())

    @property
    def text(self) -> str:
        """Obtain the text of this abstract"""
        return self.fields[self.DEFAULT_CATEGORY]

    def __repr__(self):
        return "<pmid:{}>".format(self.pmid)

    def save(self, directory: str):
        path = Path(directory, "{pmid}.{suffix}".format(pmid=self.pmid, suffix=self.SUFFIX))

        with h5py.File(path, "w") as f:
            f.create_dataset(name=self._KEY_PMID, data=self.pmid, dtype=int)
            for key, value in self.fields.items():
                log.info("save: %s | %s: %s", type(value), key, value)
                f.create_dataset(name=key, data=value)

    @classmethod
    def load(cls, path: str) -> Abstract:
        pmid: int = -1
        fields: Dict[str, str] = {}
        with h5py.File(path, "r") as f:
            for key in f.keys():
                if key == cls._KEY_PMID:
                    pmid = int(f[cls._KEY_PMID][()])
                else:
                    fields[key] = f[key][()]

        assert pmid != -1

        return Abstract(pmid=pmid, **fields)
