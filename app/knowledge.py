import json
from pathlib import Path
from datetime import date
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA = Path(__file__).resolve().parents[1] / "data/project.json"


class Knowledge:
    def __init__(self, path=DATA):
        self.data = json.loads(Path(path).read_text())
        self.docs = self.data["documents"]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([d["title"] + " " + d["text"] for d in self.docs])
        self.graph = nx.DiGraph()
        for a in self.data["activities"]:
            self.graph.add_node(a["id"], kind="activity", **a)
            for predecessor in a["predecessors"]:
                self.graph.add_edge(predecessor, a["id"], relation="precedes")
        for item in self.data["rfis"]:
            self.graph.add_node(item["id"], kind="rfi")
            self.graph.add_node(item["element"], kind="bim_element")
            self.graph.add_edge(item["id"], item["activity"], relation="blocks")
            self.graph.add_edge(item["id"], item["element"], relation="concerns")

    def search(self, question, k=3):
        scores = cosine_similarity(self.vectorizer.transform([question]), self.matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda x: (-x[1], x[0]))
        return [{**self.docs[i], "score": round(float(s), 4)} for i, s in ranked[:k] if s >= 0.05]

    def answer(self, question):
        from app.generation import synthesize

        return synthesize(question, self.extract(question))

    def extract(self, question):
        hits = self.search(question)
        return {
            "answer": "\n".join(f"{d['text']} [{d['id']} §{d['section']}]" for d in hits)
            if hits
            else "Insufficient evidence in the synthetic project corpus.",
            "citations": [
                {"document_id": d["id"], "section": d["section"], "quote": d["text"], "score": d["score"]} for d in hits
            ],
            "mode": "extractive_tfidf",
            "abstained": not bool(hits),
        }

    def risks(self, as_of):
        result = []
        for item in self.data["rfis"]:
            if item["status"] != "open":
                continue
            a = next(a for a in self.data["activities"] if a["id"] == item["activity"])
            days = (date.fromisoformat(a["start"]) - as_of).days
            downstream = sorted(nx.descendants(self.graph, a["id"]))
            result.append(
                {
                    "rfi": item["id"],
                    "activity": a["id"],
                    "days_to_start": days,
                    "overdue": date.fromisoformat(item["due"]) < as_of,
                    "severity": "high" if days <= 7 and a["float_days"] == 0 else "medium",
                    "downstream": downstream,
                    "path": [item["id"], a["id"]],
                    "basis": "Open blocking RFI; high when zero float and start within seven days (including past dates). Heuristic, not probability.",
                }
            )
        return result
