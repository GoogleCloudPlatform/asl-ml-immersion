""" Application logic: Assemble data from all services.

Note: The _extract_link_from_source function assumes
the existence of a `url` and a `title` column among
the metadata columns defined in settings.py
"""

from app.services import create_rag_service

_NO_PROMPT = """
As a technical expert overseeing app support, you will review and assess two responses using the criteria outlined below

    1.  The given answer must correctly and relevantly address the question or issue, as compared to the true answer.
    2.  The answer should be clear and easy to understand, with any technical terms or jargon explained adequately.
    3.  The answer should be pertinent to the specific application or context of the query and focused on the issue at hand.
    4.  The response should provide practical and actionable guidance that effectively helps resolve the issue.
    5.  The answer should be well-structured and logically organized, with a clear introduction, body, and conclusion.
"""

# _SUFFIX is appended to the end of every prompt and
# can be modified to format answers for example.
_SUFFIX = """
Format your answer in HTML and not in markdown.
Make sure every markdown tags in the answer are
converted into HTML tags.
"""


class Rag:
    """Main controller."""

    def __init__(self, rag_svc):
        self._rag_svc = rag_svc

    def query(self, prompt):
        if not prompt:
            answer = _NO_PROMPT
        else:
            prompt = self._preprocess_prompt(prompt)
            response = self._rag_svc.query(prompt)
            answer = self._postprocess_response(response)
        return answer

    def _preprocess_prompt(self, prompt):
        return f"{prompt} {_SUFFIX}"

    def _postprocess_response(self, response):
        answer = _generate_answer_html(response["result"])
        return f"{answer} \n "


def create_rag():
    rag_svc = create_rag_service()
    return Rag(rag_svc)

def _generate_answer_html(result):
    return f"<h1>Rag:</h1>\n {result}"
