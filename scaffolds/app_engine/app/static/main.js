async function queryApi(prompt) {
    const endpoint = `/myapp?query=${prompt}`
    const response = await fetch(endpoint)
    const answer = await response.json()
    return answer
}

function displayAnswer(answer) {
    const queryAnswer = document.getElementById("query-answer")
    queryAnswer.innerHTML = `<md-block> ${answer} </md-block>`
}

function getPrompt() {
    const queryInput = document.getElementById("query-input")
    return queryInput.value
}

function getAnswer() {
    const spinner = document.getElementById("spinner")
    const queryAnswer = document.getElementById("query-answer")
    queryAnswer.classList.remove("show")
    spinner.classList.add("show")
    const prompt = getPrompt()
    queryApi(prompt).then(
        response => {
            spinner.classList.remove("show")
            queryAnswer.classList.add("show")
            displayAnswer(response.answer)
        }
    )

}

function init() {
    const queryForm = document.getElementById("query-form")
    queryForm.addEventListener("submit", e => {
        e.preventDefault()
        getAnswer()
    })

    const queryInput = document.getElementById("query-input")
    queryInput.addEventListener("keyup", e => {
        e.preventDefault()
        if (e.KeyCode === 13){
            document.getElementById("ask-button").click()
        }
    })

  }

init()
