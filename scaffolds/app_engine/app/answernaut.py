""" Application logic: Assemble data from all services.
"""
from app.services import create_rag_service

_NO_PROMPT = "Please enter a question."
_SUFFIX = """
Format your answer in HTML and not in markdown.
Make sure every markdown tags in the answer are
converted into HTML tags.
"""


class Answernaut:
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
        sources = _generate_sources_html(response["source_documents"])
        return f"{answer} \n {sources}"


def create_answernaut():
    rag_svc = create_rag_service()
    return Answernaut(rag_svc)


def _extract_link_from_source(source):
    url = source.metadata.get("url")
    html = None
    if url:
        title = source.metadata["title"]
        html = f"<li><a href='{url}'>{title}</a></li>\n"
    return html


def _generate_sources_html(sources):
    html = "<h1>Analyzed sources ranked by relevance:</h1>\n"
    html += "<ul>\n"
    seen = set()
    for source in sources:
        link = _extract_link_from_source(source)
        if link and not link in seen:
            html += _extract_link_from_source(source)
            seen.add(link)
    html += "</ul>"
    return html


def _generate_answer_html(result):
    return f"<h1>Answernaut:</h1>\n {result}"
