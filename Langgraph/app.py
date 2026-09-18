"""
================================================================================
app.py - Interactive LangGraph Visualizer Web Server
================================================================================
Serves an interactive Single-Page Application on port 5001 to visually explore,
execute, and inspect all 9 LangGraph workflows in real time.
"""

import os
import sys
import json
import importlib
from flask import Flask, jsonify, request, send_from_directory

# Ensure current folder is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

# Global storage for HITL paused sessions
HITL_SESSIONS = {}

WORKFLOW_REGISTRY = {
    "01_basic": {
        "id": "01_basic",
        "number": 1,
        "title": "Basic StateGraph (Hello World)",
        "module": "01_basic_graph",
        "description": "Foundational LangGraph concepts: TypedDict State, Nodes, and linear transitions START -> analyze -> summary -> END.",
        "nodes": ["START", "analyze_input", "generate_summary", "END"],
        "edges": [
            {"from": "START", "to": "analyze_input"},
            {"from": "analyze_input", "to": "generate_summary"},
            {"from": "generate_summary", "to": "END"}
        ],
        "default_input": {
            "text": "QuantumNova launched its breakthrough optical quantum platform Q-Core, delivering a 40x speedup in portfolio optimization over classical supercomputers, though cryogenic cooling costs currently remain high for small firms."
        }
    },
    "02_reducers": {
        "id": "02_reducers",
        "number": 2,
        "title": "State Reducers & Parallel Branches",
        "module": "02_state_reducers",
        "description": "Overwrites vs. Appends using Annotated[list, operator.add]. Demonstrates concurrent parallel branches (sentiment + security scanner) converging on a join node.",
        "nodes": ["START", "sentiment_analyzer", "security_scanner", "consolidate_report", "END"],
        "edges": [
            {"from": "START", "to": "sentiment_analyzer"},
            {"from": "START", "to": "security_scanner"},
            {"from": "sentiment_analyzer", "to": "consolidate_report"},
            {"from": "security_scanner", "to": "consolidate_report"},
            {"from": "consolidate_report", "to": "END"}
        ],
        "default_input": {
            "text": "URGENT: Database server db-prod-02 has 99.8% disk utilization! Credentials admin:Quantum$2026! are in /var/log/credentials.txt. Clear space immediately."
        }
    },
    "03_routing": {
        "id": "03_routing",
        "number": 3,
        "title": "Dynamic Conditional Routing",
        "module": "03_conditional_routing",
        "description": "Dynamic branching via add_conditional_edges. Gemini classifies user intent (Technical, Billing, Casual) and routes to specialized expert nodes.",
        "nodes": ["START", "classify_intent", "handle_tech", "handle_billing", "handle_casual", "END"],
        "edges": [
            {"from": "START", "to": "classify_intent"},
            {"from": "classify_intent", "to": "handle_tech", "label": "technical"},
            {"from": "classify_intent", "to": "handle_billing", "label": "billing"},
            {"from": "classify_intent", "to": "handle_casual", "label": "casual"},
            {"from": "handle_tech", "to": "END"},
            {"from": "handle_billing", "to": "END"},
            {"from": "handle_casual", "to": "END"}
        ],
        "default_input": {
            "query": "How do I fix a NullPointerException in my Java Redis cache cluster?"
        }
    },
    "04_cycles": {
        "id": "04_cycles",
        "number": 4,
        "title": "Cyclical Graph & Self-Correction",
        "module": "04_cyclical_agent_loop",
        "description": "Autonomous loops: Drafter creates a version, Critic grades it. If score < 8, loops back with critique until quality meets standards.",
        "nodes": ["START", "drafter", "critic", "END"],
        "edges": [
            {"from": "START", "to": "drafter"},
            {"from": "drafter", "to": "critic"},
            {"from": "critic", "to": "drafter", "label": "score < 8 (revise)"},
            {"from": "critic", "to": "END", "label": "score >= 8 (pass)"}
        ],
        "default_input": {
            "topic": "Announcing QuantumNova's SOC-2 Type II Compliance Certification",
            "criteria": "Must mention auditor Deloitte & Touche, specify Cloud Vault and API Infrastructure, and include a Trust Center CTA."
        }
    },
    "05_react": {
        "id": "05_react",
        "number": 5,
        "title": "ReAct Tool-Calling Agent Loop",
        "module": "05_tool_calling_agent",
        "description": "Self-directed agent with external tools (calculator, cluster telemetry). Reason -> Act -> Observe -> Finish cyclic loop.",
        "nodes": ["START", "agent_reason", "run_tool", "END"],
        "edges": [
            {"from": "START", "to": "agent_reason"},
            {"from": "agent_reason", "to": "run_tool", "label": "tool call needed"},
            {"from": "run_tool", "to": "agent_reason", "label": "observe result"},
            {"from": "agent_reason", "to": "END", "label": "answer ready"}
        ],
        "default_input": {
            "query": "Check the telemetry of singapore-beta cluster, and if CPU > 80%, calculate how many servers to add if each reduces load by 15% to reach < 60%?"
        }
    },
    "06_memory": {
        "id": "06_memory",
        "number": 6,
        "title": "Persistence & Checkpoints (MemorySaver)",
        "module": "06_memory_and_checkpoints",
        "description": "Multi-turn session persistence using MemorySaver and thread_id. Thread isolation and time-travel state history inspection.",
        "nodes": ["START", "chat", "END"],
        "edges": [
            {"from": "START", "to": "chat"},
            {"from": "chat", "to": "END"}
        ],
        "default_input": {
            "thread_id": "user-session-101",
            "message": "Hi, my name is Dr. Alice Chen, Lead Cryptographer at QuantumNova."
        }
    },
    "07_hitl": {
        "id": "07_hitl",
        "number": 7,
        "title": "Human-in-the-Loop (HITL) Interrupts",
        "module": "07_human_in_the_loop",
        "description": "Safe agent execution with interrupt_before. Workflow halts before sensitive financial wire transfer, waiting for human approval.",
        "nodes": ["START", "draft_transaction", "execute_transfer", "END"],
        "edges": [
            {"from": "START", "to": "draft_transaction"},
            {"from": "draft_transaction", "to": "execute_transfer", "label": "⏸️ INTERRUPT"},
            {"from": "execute_transfer", "to": "END"}
        ],
        "default_input": {
            "request": "Please wire transfer $75,000 to Apex Data Centers for Q3 server rack expansion."
        }
    },
    "08_crag": {
        "id": "08_crag",
        "number": 8,
        "title": "Corrective RAG (CRAG) & Self-RAG",
        "module": "08_corrective_rag",
        "description": "Connecting RAG + LangGraph! Evaluates retrieved document relevance. If irrelevant, triggers query rewriting and fallback search before generation.",
        "nodes": ["START", "retrieve", "grade_documents", "corrective_fallback", "generate_answer", "END"],
        "edges": [
            {"from": "START", "to": "retrieve"},
            {"from": "retrieve", "to": "grade_documents"},
            {"from": "grade_documents", "to": "generate_answer", "label": "Relevant"},
            {"from": "grade_documents", "to": "corrective_fallback", "label": "Not Relevant"},
            {"from": "corrective_fallback", "to": "generate_answer"},
            {"from": "generate_answer", "to": "END"}
        ],
        "default_input": {
            "question": "What is the official public launch date and laser link speed for Project NovaStar?"
        }
    },
    "09_multi_agent": {
        "id": "09_multi_agent",
        "number": 9,
        "title": "Multi-Agent Supervisor Collaboration",
        "module": "09_multi_agent_supervisor",
        "description": "Supervisor pattern: Lead LLM orchestrates specialized Researcher and Coder agents, aggregating collaborative outputs into a complete deliverable.",
        "nodes": ["START", "supervisor", "researcher", "coder", "synthesize", "END"],
        "edges": [
            {"from": "START", "to": "supervisor"},
            {"from": "supervisor", "to": "researcher", "label": "delegate research"},
            {"from": "researcher", "to": "supervisor", "label": "return specs"},
            {"from": "supervisor", "to": "coder", "label": "delegate code"},
            {"from": "coder", "to": "supervisor", "label": "return code"},
            {"from": "supervisor", "to": "synthesize", "label": "all complete"},
            {"from": "synthesize", "to": "END"}
        ],
        "default_input": {
            "task": "Build a thread-safe token bucket rate limiter in Python for a REST API."
        }
    }
}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/workflows", methods=["GET"])
def get_workflows():
    """Returns metadata for all available LangGraph workflows."""
    return jsonify({
        "success": True,
        "workflows": list(WORKFLOW_REGISTRY.values())
    })


def execute_and_collect(graph, initial_state):
    """Executes the graph once in streaming mode, collecting node steps and reducing final state."""
    final_state = dict(initial_state)
    steps = []
    for event in graph.stream(initial_state):
        for node, upd in event.items():
            steps.append({"node": node, "update": upd})
            if isinstance(upd, dict):
                for k, v in upd.items():
                    if k in final_state and isinstance(final_state[k], list) and isinstance(v, list):
                        final_state[k] = final_state[k] + v
                    else:
                        final_state[k] = v
    return steps, final_state


@app.route("/api/run/<workflow_id>", methods=["POST"])
def run_workflow(workflow_id):
    """Executes the selected LangGraph workflow and returns step-by-step logs and state."""
    if workflow_id not in WORKFLOW_REGISTRY:
        return jsonify({"success": False, "error": f"Workflow '{workflow_id}' not found"}), 404

    wf_meta = WORKFLOW_REGISTRY[workflow_id]
    user_payload = request.json or {}

    try:
        module = importlib.import_module(wf_meta["module"])

        # Execute workflow-specific logic
        if workflow_id == "01_basic":
            graph = module.build_basic_graph()
            input_text = user_payload.get("text", wf_meta["default_input"]["text"])
            initial_state = {
                "input_text": input_text,
                "analysis": "",
                "summary": "",
                "step_history": []
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

        elif workflow_id == "02_reducers":
            graph = module.build_reducer_graph()
            input_text = user_payload.get("text", wf_meta["default_input"]["text"])
            initial_state = {
                "input_text": input_text,
                "sentiment_findings": "",
                "security_findings": "",
                "final_verdict": "",
                "audit_trail": ["[Audit] Pipeline initialized."]
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

        elif workflow_id == "03_routing":
            graph = module.build_routing_graph()
            query = user_payload.get("query", wf_meta["default_input"]["query"])
            initial_state = {
                "query": query,
                "intent": "",
                "confidence": 0.0,
                "response": "",
                "route_taken": ""
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

        elif workflow_id == "04_cycles":
            graph = module.build_cyclical_graph()
            topic = user_payload.get("topic", wf_meta["default_input"]["topic"])
            criteria = user_payload.get("criteria", wf_meta["default_input"]["criteria"])
            initial_state = {
                "topic": topic,
                "target_criteria": criteria,
                "current_draft": "",
                "critique": "",
                "quality_score": 0,
                "iteration_count": 0,
                "max_iterations": 3,
                "history": []
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

        elif workflow_id == "05_react":
            graph = module.build_react_graph()
            query = user_payload.get("query", wf_meta["default_input"]["query"])
            initial_state = {
                "input_query": query,
                "messages": [{"role": "user", "content": query}],
                "next_tool": "none",
                "tool_args": {},
                "final_answer": "",
                "step_count": 0
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

        elif workflow_id == "06_memory":
            graph = module.build_memory_graph()
            thread_id = user_payload.get("thread_id", "web-session-1")
            message = user_payload.get("message", wf_meta["default_input"]["message"])
            config = {"configurable": {"thread_id": thread_id}}

            state_input = {
                "messages": [{"role": "user", "content": message}]
            }
            final_state = graph.invoke(state_input, config=config)
            history_snapshots = list(graph.get_state_history(config))
            checkpoints_meta = [
                {
                    "checkpoint_id": s.config["configurable"].get("checkpoint_id", "")[:8],
                    "msg_count": len(s.values.get("messages", []))
                }
                for s in history_snapshots
            ]

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "thread_id": thread_id,
                "final_state": final_state,
                "checkpoints_count": len(history_snapshots),
                "checkpoints": checkpoints_meta
            })

        elif workflow_id == "07_hitl":
            graph = module.build_hitl_graph()
            req_text = user_payload.get("request", wf_meta["default_input"]["request"])
            session_id = f"hitl-{os.urandom(4).hex()}"
            config = {"configurable": {"thread_id": session_id}}

            initial_state = {
                "request": req_text,
                "recipient": "",
                "amount_usd": 0.0,
                "reason": "",
                "human_approval": "PENDING",
                "execution_status": "WAITING_FOR_REVIEW",
                "transaction_id": ""
            }

            # Run until interrupt breakpoint
            graph.invoke(initial_state, config=config)
            state_at_bp = graph.get_state(config)

            # Store in session map for interactive resume
            HITL_SESSIONS[session_id] = {
                "graph": graph,
                "config": config
            }

            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "session_id": session_id,
                "is_paused": bool(state_at_bp.next),
                "next_node": list(state_at_bp.next) if state_at_bp.next else [],
                "state_at_breakpoint": state_at_bp.values
            })

        elif workflow_id == "08_crag":
            graph = module.build_crag_graph()
            q = user_payload.get("question", wf_meta["default_input"]["question"])
            initial_state = {
                "question": q,
                "documents": [],
                "relevance_verdict": "",
                "rewritten_query": "",
                "fallback_used": False,
                "generation": "",
                "grounding_grade": ""
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

        elif workflow_id == "09_multi_agent":
            graph = module.build_multi_agent_graph()
            task = user_payload.get("task", wf_meta["default_input"]["task"])
            initial_state = {
                "task": task,
                "research_notes": "",
                "code_artifact": "",
                "final_deliverable": "",
                "next_worker": "supervisor",
                "step_count": 0,
                "worker_log": ["Session initialized via Web API."]
            }
            steps, final_state = execute_and_collect(graph, initial_state)
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "steps": steps,
                "final_state": final_state
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/hitl/resume", methods=["POST"])
def resume_hitl():
    """Resumes an interrupted Human-in-the-Loop workflow with APPROVE or REJECT."""
    payload = request.json or {}
    session_id = payload.get("session_id")
    decision = payload.get("decision", "APPROVED")  # "APPROVED" or "REJECTED"

    if session_id not in HITL_SESSIONS:
        return jsonify({"success": False, "error": f"Session '{session_id}' not found or expired"}), 404

    session = HITL_SESSIONS[session_id]
    graph = session["graph"]
    config = session["config"]

    try:
        # Update state with human approval decision
        graph.update_state(config, {"human_approval": decision}, as_node="draft_transaction")
        # Resume execution
        graph.invoke(None, config=config)
        final_state = graph.get_state(config)

        # Cleanup session
        del HITL_SESSIONS[session_id]

        return jsonify({
            "success": True,
            "decision": decision,
            "final_state": final_state.values
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("🚀 LANGGRAPH VISUALIZER RUNNING ON http://127.0.0.1:5001")
    print("=" * 65 + "\n")
    app.run(host="0.0.0.0", port=5001, debug=False)
