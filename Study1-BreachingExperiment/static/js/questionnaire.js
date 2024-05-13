document.getElementById("questionnaireForm").addEventListener("submit", function(event) {
    event.preventDefault();

    var formData = {};
    this.querySelectorAll('input[type="radio"]:checked').forEach(function(input) {
        formData[input.name] = input.value;
    });


    var isComplete = Object.keys(formData).length === 9;
    if (!isComplete) {
        alert("Please answer all questions.");
        return;
    }

    console.log(formData);

    fetch(`/questionnaire/${condition}`, { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            console.error('Response Error:', response.status, response.statusText);
            return response.text().then(text => {
                throw new Error(`Failed to submit questionnaire: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Questionnaire submitted:', data);
        window.location.href = "/apply-random-condition";
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
