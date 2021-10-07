import logging
import re

from dff.core.keywords import TRANSITIONS, GRAPH, RESPONSE, GLOBAL_TRANSITIONS
from dff.core import Context, Actor
import dff.conditions as cnd
import dff.transitions as trn

from examples import example_1_basics

logger = logging.getLogger(__name__)


def always_true_condition(ctx: Context, actor: Actor, *args, **kwargs) -> bool:
    return True


def high_priority_node_transition(flow_label, node_label):
    def transition(
        ctx: Context, actor: Actor, *args, **kwargs
    ) -> tuple[str, str, float]:
        return (flow_label, node_label, 2.0)

    return transition


flows = {
    "global_flow": {
        GLOBAL_TRANSITIONS: {
            ("greeting_flow", "node1", 1.1): cnd.regexp(r"\b(hi|hello)\b", re.I),
            ("music_flow", "node1", 1.1): cnd.regexp(r"talk about music"),
            trn.to_fallback(0.1): always_true_condition,
            trn.forward(): cnd.all(
                [
                    cnd.regexp(r"next\b"),
                    cnd.isin_flow(
                        nodes=[("music_flow", i) for i in ["node2", "node3"]]
                    ),
                ]
            ),
            trn.repeat(0.2): cnd.all(
                [
                    cnd.regexp(r"repeat", re.I),
                    cnd.negation(cnd.isin_flow(flows=["global_flow"])),
                ]
            ),
        },
        GRAPH: {
            "start_node": {  # This is an initial node, it doesn't need an `RESPONSE`
                RESPONSE: "",
            },
            "fallback_node": {  # We get to this node if an error occurred while the agent was running
                RESPONSE: "Ooops",
                TRANSITIONS: {trn.previous(): cnd.regexp(r"previous", re.I)},
            },
        },
    },
    "greeting_flow": {
        GRAPH: {
            "node1": {
                RESPONSE: "Hi, how are you?",  # When the agent goes to node1, we return "Hi, how are you?"
                TRANSITIONS: {"node2": cnd.regexp(r"how are you")},
            },
            "node2": {
                RESPONSE: "Good. What do you want to talk about?",
                TRANSITIONS: {
                    trn.forward(0.5): cnd.regexp(r"talk about"),
                    trn.previous(): cnd.regexp(r"previous", re.I),
                },
            },
            "node3": {
                RESPONSE: "Sorry, I can not talk about that now.",
                TRANSITIONS: {trn.forward(): cnd.regexp(r"bye")},
            },
            "node4": {RESPONSE: "bye"},
        }
    },
    "music_flow": {
        GRAPH: {
            "node1": {
                RESPONSE: "I love `System of a Down` group, would you like to tell about it? ",
                TRANSITIONS: {trn.forward(): cnd.regexp(r"yes|yep|ok", re.I)},
            },
            "node2": {
                RESPONSE: "System of a Downis an Armenian-American heavy metal band formed in in 1994.",
            },
            "node3": {
                RESPONSE: "The band achieved commercial success with the release of five studio albums.",
                TRANSITIONS: {trn.backward(): cnd.regexp(r"back", re.I)},
            },
            "node4": {
                RESPONSE: "That's all what I know",
                TRANSITIONS: {
                    ("greeting_flow", "node4"): cnd.regexp(r"next time", re.I),
                    ("greeting_flow", "node2"): cnd.regexp(r"next", re.I),
                },
            },
        }
    },
}
actor = Actor(
    flows,
    start_node_label=("global_flow", "start_node"),
    fallback_node_label=("global_flow", "fallback_node"),
    default_transition_priority=1.0,  # default_transition_priority == 1 by dafault
)


# testing
testing_dialog = [
    ("hi", "Hi, how are you?"),
    ("i'm fine, how are you?", "Good. What do you want to talk about?"),
    (
        "talk about music.",
        "I love `System of a Down` group, would you like to tell about it? ",
    ),
    (
        "yes",
        "System of a Downis an Armenian-American heavy metal band formed in in 1994.",
    ),
    (
        "next",
        "The band achieved commercial success with the release of five studio albums.",
    ),
    (
        "back",
        "System of a Downis an Armenian-American heavy metal band formed in in 1994.",
    ),
    (
        "repeat",
        "System of a Downis an Armenian-American heavy metal band formed in in 1994.",
    ),
    (
        "next",
        "The band achieved commercial success with the release of five studio albums.",
    ),
    ("next", "That's all what I know"),
    ("next", "Good. What do you want to talk about?"),
    ("previous", "That's all what I know"),
    ("next time", "bye"),
    ("stop", "Ooops"),
    ("previous", "bye"),
    ("stop", "Ooops"),
    ("nope", "Ooops"),
    ("hi", "Hi, how are you?"),
    ("stop", "Ooops"),
    ("previous", "Hi, how are you?"),
    ("i'm fine, how are you?", "Good. What do you want to talk about?"),
    ("let's talk about something.", "Sorry, I can not talk about that now."),
    ("Ok, goodbye.", "bye"),
]


def run_test():
    ctx = {}
    for in_request, true_out_response in testing_dialog:
        _, ctx = example_1_basics.turn_handler(
            in_request, ctx, actor, true_out_response=true_out_response
        )


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s-%(name)15s:%(lineno)3s:%(funcName)20s():%(levelname)s - %(message)s",
        level=logging.INFO,
    )
    run_test()
    example_1_basics.run_interactive_mode(actor)
