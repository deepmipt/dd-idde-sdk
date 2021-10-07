import logging
from typing import Optional
import datetime


from dff.core.keywords import GRAPH, RESPONSE, TRANSITIONS, PROCESSING
from dff.core import Context, Actor, Node
import dff.transitions as trn

logging.basicConfig(
    format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


# custom functions
def always_true(ctx: Context, actor: Actor, *args, **kwargs) -> bool:
    return True


def create_transitions():
    return {
        ("left", "step_2"): "left",
        ("right", "step_2"): "right",
        trn.previous(): "previous",
        trn.to_start(): "start",
        trn.forward(): "forward",
        trn.backward(): "back",
        trn.previous(): "previous",
        trn.repeat(): "repeat",
        trn.to_fallback(): always_true,
    }


def add_node_label_processing(
    node_label: str,
    node: Node,
    ctx: Context,
    actor: Actor,
    *args,
    **kwargs,
) -> Optional[tuple[str, Node]]:
    node.response = f"{node_label}: {node.response}"
    return node_label, node


def add_time_processing(
    node_label: str,
    node: Node,
    ctx: Context,
    actor: Actor,
    *args,
    **kwargs,
) -> Optional[tuple[str, Node]]:
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    node.response = f"{timestamp}: {node.response}"
    return node_label, node


# a dialog script
flows = {
    "root": {
        GRAPH: {
            "start": {
                RESPONSE: "",
                TRANSITIONS: {("greeting", "step_0"): always_true},
            },
            "fallback": {RESPONSE: "the end"},
        },
    },
    "greeting": {
        GRAPH: {
            "step_0": {
                PROCESSING: [add_node_label_processing, add_time_processing],
                RESPONSE: "hi",
                TRANSITIONS: {trn.forward(): always_true},
            },
            "step_1": {
                PROCESSING: [add_node_label_processing, add_time_processing],
                RESPONSE: "what's up",
                TRANSITIONS: {trn.forward(): always_true},
            },
            "step_2": {
                PROCESSING: [add_node_label_processing, add_time_processing],
                RESPONSE: "ok",
            },
        },
    },
}

ctx = Context()
actor = Actor(
    flows, start_node_label=("root", "start"), fallback_node_label=("root", "fallback")
)
while True:
    in_text = input("you: ")
    ctx.add_request(in_text)
    ctx = actor(ctx)
    print(f"bot: {ctx.last_response}")
