"""Local fixtures only: no vendor SDK, credentials, network or actual API writes."""

from typing import Protocol


class ConstructionConnector(Protocol):
    def list_records(self) -> list[dict]: ...


class MockProcore:
    def __init__(self, knowledge):
        self.knowledge = knowledge

    def list_records(self):
        return [{**r, "integration": "mock_procore"} for r in self.knowledge.data["rfis"]]


class MockAutodesk:
    def __init__(self, knowledge):
        self.knowledge = knowledge

    def list_records(self):
        return [{**r, "integration": "mock_autodesk"} for r in self.knowledge.data["elements"]]
