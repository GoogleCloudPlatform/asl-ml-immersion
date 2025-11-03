testing_thing = {
    "gq": "Is the ball red?",
    "ga": "Yes, the ball is red.",
    "gs": "BallRedness.pdf, CommonStuff.pdf",
    "ka": "Yep, it seems like the ball is red.",
    "ks": "BallRedness.pdf",
    "rc": "[Sometimes it is the case that balls are red, this particular ball might be red]"
}

from simulations.auto_tester.app import run_test
from main import get_score_interpretation

scores = run_test(
    g_question=testing_thing["gq"],
    g_answer=testing_thing["ga"],
    g_source=testing_thing["gs"],
    kiq_answer=testing_thing["ka"],
    retrieved_source=testing_thing["ks"],
    retrieval_context=testing_thing["rc"]
)

print(get_score_interpretation(scores))