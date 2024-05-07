let globalEmailsData = [];
// for ui
let selectedRows = [];

let startTime = Date.now();

document.addEventListener('DOMContentLoaded', function() {
    generateEmailList(experimentData);
});

function gotoNextStep() {
    let endTime = Date.now();
    let recordTime = endTime - startTime; 
    console.log('Time Recorded:', recordTime);

    saveSelectedRowsToServer(condition,recordTime, selectedRows);

    fetch(`/questionnaire/${condition}`, { 
        method: 'GET'
    })
    .then(response => {
        console.log(response);
        if (!response.ok) {
            throw new Error('Failed to move to questionnaire');
        }

        window.location.replace(`/questionnaire/${condition}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });

}


function generateEmailList(emails) {
    // console.log("Emails data:", emails);
    globalEmailsData = [];
    const emailList = document.querySelector('.emailList__list');
    emailList.innerHTML = '';


    if (condition === 'Date') {
        emails = shuffleArray(emails);
    }

    emails.forEach((email, index) => {
        email.originalIndex = index;
        const emailRow = document.createElement('div');
        emailRow.classList.add('emailRow');
        emailRow.dataset.originalIndex = email.originalIndex;
        // console.log(`Row ${index}, Original Index: ${emailRow.dataset.originalIndex}`); 
        emailRow.onclick = function(event) {
            selectRow(event, email.originalIndex);
        };
        emailRow.innerHTML = `
            <div class="emailRow__index"></div>
            <div class="emailRow__options">
                <input type="checkbox" name="" id="" />
                <span class="material-icons"> star_border </span>
            </div>
            <h3 class="emailRow__sender">${escapeHtml(email.sender)}</h3>
            <div class="emailRow__emoji">${escapeHtml(email.emoji)}</div>
            <div class="emailRow__message">
                <h4>${escapeHtml(email.subject)} <span class="emailRow__description">${escapeHtml(email.body)}</span></h4>
            </div>
            <p class="emailRow__time">${escapeHtml(email.date)}</p>
        `;
        globalEmailsData.push(emailRow);
        emailList.appendChild(emailRow);
    });
}

function escapeHtml(text) {
    if (text === null) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function shuffleArray(array) {
    const shuffledArray = [...array];
    for (let i = shuffledArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledArray[i], shuffledArray[j]] = [shuffledArray[j], shuffledArray[i]];
    }
    return shuffledArray;
}

function sortTable(column) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("emailList__list");
    switching = true;
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[column];
            y = rows[i + 1].getElementsByTagName("TD")[column];
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}



function selectRow(event, originalIndex) {
    event.stopPropagation(); 
    var target = event.target || event.srcElement; 
    var row = target.closest('.emailRow');
    if (!row) return;

    var rowIndex = Array.from(row.parentElement.children).indexOf(row);
    // var rowIndex = originalIndex

    if (!selectedRows.includes(rowIndex)) {
        selectedRows.push(rowIndex);
        row.classList.add('row__selected');
    } else {
        selectedRows = selectedRows.filter(index => index !== rowIndex);
        row.classList.remove('row__selected');
    }

    selectedRows.forEach((selectedRowIndex, index) => {
        var emailRow = document.querySelector(`.emailRow:nth-child(${selectedRowIndex + 1})`);
        var indexElement = emailRow.querySelector(".emailRow__options input");
        indexElement.value = index + 1;
        emailRow.querySelector(".emailRow__index").textContent = index + 1;
    });


    // 選択が解除された時
    var deselectedRows = Array.from(row.parentElement.children).map((child, index) => index).filter(index => !selectedRows.includes(index));

    deselectedRows.forEach((deselectedRowIndex) => {
        var emailRow = document.querySelector(`.emailRow:nth-child(${deselectedRowIndex + 1})`);
        var indexDisplay = emailRow.querySelector(".emailRow__index");
        indexDisplay.textContent = ''; 
    });

    console.log("Selected Order:", selectedRows);
    // updateSelectedNumbers();
    updateInstruction();
}


function updateInstruction() {
    let totalEmails = document.querySelectorAll('.emailRow').length;
    let remaining = totalEmails - selectedRows.length;
    let instructionElement = document.getElementById("instruction");
    let nextButton = document.getElementById("nextButton");

    if (remaining > 0) {
        instructionElement.innerHTML = "Select " + remaining + " more emails.";
        nextButton.style.display = "none";
    } else {
        instructionElement.innerHTML = "";
        nextButton.style.display = "block";
    }
}

function saveSelectedRowsToServer(condition, recordTime, selectedRows) {
    const orderByID = {}; // IDをキーとして選択された順序を記録する



    selectedRows.forEach((rowIndex, order) => {
        // const row = document.querySelector(`.emailRow:nth-child(${rowIndex + 1})`);
        const originalIndex = String(globalEmailsData[rowIndex].dataset.originalIndex);
        orderByID[originalIndex] = parseInt(order) + 1; 
    });

    recordTime = String(recordTime);

    console.log(JSON.stringify({ 'condition': condition, 'selectedRows': orderByID  }));

    fetch('/update-selected-rows', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'condition': condition, 'selectedRows': orderByID  })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Failed to update selected rows: Status ${response.status}, Body: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });

    fetch('/update-time-record', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'condition': condition, 'recordTime': recordTime })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Failed to update time record: Status ${response.status}, Body: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Time Record Updated Successfully:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
