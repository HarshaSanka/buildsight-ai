from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt


class State(TypedDict, total=False):
    kind: str
    question: str
    as_of: str
    evidence: dict
    findings: list
    draft: str
    decision: dict
    status: str


def build_graph(knowledge, saver):
    def retrieve(state):
        return {"evidence": knowledge.answer(state["question"])}

    def analyze(state):
        from datetime import date

        findings = knowledge.risks(date.fromisoformat(state["as_of"]))
        return {"findings": findings}

    def rfi(state):
        return {
            "draft": "Draft RFI review: confirm reinforcing conflict disposition with the engineer. "
            + state["evidence"]["answer"]
        }

    def schedule(state):
        return {
            "draft": "Draft schedule review: assess blocked activities and downstream sequencing. "
            + str(state["findings"])
        }

    def risk(state):
        return {
            "draft": "Draft risk register review: verify open blockers with field leadership. " + str(state["findings"])
        }

    def approval(state):
        decision = interrupt(
            {
                "draft": state["draft"],
                "evidence": state["evidence"],
                "notice": "Approve local advisory record only; never authorize field work.",
            }
        )
        return {"decision": decision, "status": "approved" if decision["approve"] else "rejected"}

    graph = StateGraph(State)
    graph.add_node("retrieve", retrieve)
    graph.add_node("analyze", analyze)
    for name, fn in [("rfi", rfi), ("schedule", schedule), ("risk", risk), ("approval", approval)]:
        graph.add_node(name, fn)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "analyze")
    graph.add_conditional_edges("analyze", lambda s: s["kind"], {k: k for k in ["rfi", "schedule", "risk"]})
    for k in ["rfi", "schedule", "risk"]:
        graph.add_edge(k, "approval")
    graph.add_edge("approval", END)
    return graph.compile(checkpointer=saver)
