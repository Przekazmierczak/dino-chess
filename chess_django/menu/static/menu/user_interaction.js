document.addEventListener('DOMContentLoaded', function () {
    // Get the CSRF token from the input field (required for POST requests)
    const csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    
    // Get the URL for loading more data from the DOM element
    const loadMoreUrl = document.getElementById('load-more-url').getAttribute('data-url');
    
    // Get references to the history table and "Load More" button elements
    const historyTableElement = document.getElementById("historyTable");
    const loadMoreButtonElement = document.getElementById("load-more-button");
    
    // Base URL for navigating to individual game pages
    const tableUrl = document.getElementById('table-url').getAttribute('data-url').slice(0, -2);
    
    // Number of games to fetch and display at a time
    const gamesPerBatch = 10;
    
    // Keep track of the last game ID loaded
    const lastGameID = { last: -1 };

    loadGameHistory(csrf_token, loadMoreUrl, historyTableElement, loadMoreButtonElement, tableUrl, gamesPerBatch, lastGameID);
    setupDropDownMenu(csrf_token);
});

function loadGameHistory(csrf_token, loadMoreUrl, historyTableElement, loadMoreButtonElement, tableUrl, gamesPerBatch, lastGameID) {
    // Initial load of games when the page is first loaded
    loadGames(lastGameID, loadMoreUrl, csrf_token, historyTableElement, loadMoreButtonElement, tableUrl, gamesPerBatch);
    
    // Set up an event listener for the "Load More" button
    document.getElementById("load-more-button").addEventListener("click", function() {
        loadGames(lastGameID, loadMoreUrl, csrf_token, historyTableElement, loadMoreButtonElement, tableUrl, gamesPerBatch);
    });
}

// Function to fetch more games from the server
function loadGames(lastGameID, loadMoreUrl, csrf_token, historyTableElement, loadMoreButtonElement, tableUrl, gamesPerBatch) {
    fetch(loadMoreUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify({ lastID: lastGameID.last })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data.message);
        createHistoryTable(historyTableElement, data.message, loadMoreButtonElement, tableUrl, gamesPerBatch);
        lastGameID.last = data.message[data.message.length - 1]["id"];
    })
    .catch(error => {
        console.error('Error', error);
    })
}

// Function to update the history table with new rows
function createHistoryTable(historyTable, gameDataRows, loadMoreButtonElement, tableUrl, gamesPerBatch) {
    let length = gameDataRows.length;
    
    // Show or hide the "Load More" button based on the number of rows received
    if (length >= gamesPerBatch) {
        loadMoreButtonElement.classList.remove("hidden");
        length = gamesPerBatch;
    } else {
        loadMoreButtonElement.classList.add("hidden");
    }

    // Create and append rows for each data entry
    for (let i = 0; i < length; i++) {
        const tableRow = document.createElement("tr");
        
        // Set custom attributes for the row
        tableRow.setAttribute("data-id", gameDataRows[i]["id"]);
        tableRow.setAttribute("class", `winner_${gameDataRows[i]["winner"]}`);
        
        // Convert the time difference to a human-readable format
        gameDataRows[i]["time"] = convertTime(Date.now() - gameDataRows[i]["time"])
        
        // Add table cells for each data column
        for (const field of ["time", "white", "black"]) {
            const tableCell = document.createElement("td");
            tableCell.innerHTML = gameDataRows[i][field];
            tableRow.appendChild(tableCell);
        }
        
        // Add a click event to navigate to the game details page
        tableRow.addEventListener("click", function(event) {
            const gameId = event.target.closest("tr").getAttribute("data-id");
            window.location.href = tableUrl + `${gameId}`;
        });
        
        // Append the new row to the table
        historyTable.appendChild(tableRow);
    }
}

// Function to convert a time difference into a human-readable format
function convertTime(time) {
    // Calculate the number of days from the time difference
    const days = Math.floor(time/86400000);
    if (days > 0) {
        // If the time difference is in days, update the cell with the corresponding text and continue to the next row
        return convertTimeToString(days, "day");
    }

    // Calculate the number of hours from the time difference
    const hours = Math.floor(time/3600000);
    if (hours > 0) {
        // If the time difference is in hours, update the cell with the corresponding text and continue to the next row
        return convertTimeToString(hours, "hour");
    }

    // Calculate the number of minutes from the time difference
    const minutes = Math.floor(time/60000);
    if (minutes > 0) {
        // If the time difference is in minutes, update the cell with the corresponding text and continue to the next row
        return convertTimeToString(minutes, "minute");
    }
    
    // Default case: If the time difference is less than a minute, display "Few seconds ago"
    return "Few seconds ago";
    
}

// Function to append an "s" to the unit if the value is greater than 1 (e.g., "days" instead of "day")
function convertTimeToString(quantity, unit) {
    return `${quantity} ${unit}${(quantity == 1) ? "": "s"} ago`;
}

function setupDropDownMenu(csrf_token) {
    var avatarSelectContainer, dropdownLength, dropdownElement, selectedItem, dropdownItemsContainer, dropdownOptionItem;
    // Look for any elements with the class "avatar-select":
    avatarSelectContainer = document.getElementById("avatar-select");

    // Get the dropdown <select> element and its options:
    dropdownElement = avatarSelectContainer.getElementsByTagName("select")[0];
    dropdownLength = dropdownElement.length;

    // For each element, create a new DIV that will act as the selected item
    selectedItem = document.createElement("DIV");
    selectedItem.setAttribute("class", "select-selected");
    selectedItem.innerHTML = dropdownElement.options[dropdownElement.selectedIndex].innerHTML;
    avatarSelectContainer.appendChild(selectedItem);

    // For each element, create a new DIV that will contain the option list
    dropdownItemsContainer = document.createElement("DIV");
    dropdownItemsContainer.setAttribute("class", "select-items select-hide");

    // Create a new DIV to contain the custom dropdown items (hidden by default)
    const saveAvatarUrl = document.getElementById('save-avatar-url').getAttribute('data-url');

    for (var i = 1; i < dropdownLength; i++) {
        // For each option in the original select element, create a new DIV that will act as an option item
        dropdownOptionItem = document.createElement("DIV");
        dropdownOptionItem.innerHTML = dropdownElement.options[i].innerHTML;

        // Add click event listener to update the selection when an option is clicked
        dropdownOptionItem.addEventListener("click", function(e) {
            var options, optionIndex, siblingNode, selectElement, headerElement, totalOptions, selectedItems;

            // Get the original <select> element and the total options
            selectElement = this.parentNode.parentNode.getElementsByTagName("select")[0];
            totalOptions = selectElement.length;
            headerElement = this.parentNode.previousSibling;

            // Update the selected option in the original <select> element
            for (optionIndex = 0; optionIndex < totalOptions; optionIndex++) {
                if (selectElement.options[optionIndex].innerHTML == this.innerHTML) {
                    selectElement.selectedIndex = optionIndex;
                    headerElement.innerHTML = this.innerHTML;

                    // Remove the "same-as-selected" class from all options
                    options = this.parentNode.getElementsByClassName("same-as-selected");
                    selectedItems = options.length;
                    for (siblingNode = 0; siblingNode < selectedItems; siblingNode++) {
                    options[siblingNode].removeAttribute("class");
                    }
                    
                    this.setAttribute("class", "same-as-selected");

                    // Update the avatar and save the selection
                    changeAvatar(selectElement[optionIndex].value);
                    saveAvatar(selectElement[optionIndex].value, saveAvatarUrl, csrf_token);

                    break;
                }
            }

            // Close the dropdown list after selection
            headerElement.click();
        });
        dropdownItemsContainer.appendChild(dropdownOptionItem);
    }
    
    // Append the custom dropdown list to the container
    avatarSelectContainer.appendChild(dropdownItemsContainer);

    // Add click event listener to the selected item to toggle dropdown visibility
    selectedItem.addEventListener("click", function(e) {
        e.stopPropagation();
        closeAllSelect(this);
        this.nextSibling.classList.toggle("select-hide");
        this.classList.toggle("select-arrow-active");
    });

    // Event listener to close dropdowns when clicking outside
    document.addEventListener("click", closeAllSelect);
}

// Function to change the avatar's appearance based on the selected value
function changeAvatar(value) {
    const userAvatar = document.querySelector("#avatar");
    const sideBarAvatar = document.querySelector("#sidebar-avatar");

    userAvatar.classList = "";
    userAvatar.classList.add(`avatar-${value}`);

    sideBarAvatar.classList = "";
    sideBarAvatar.classList.add(`avatar-${value}`);
}

// Function to save the selected avatar to the server
function saveAvatar(new_avatar, saveAvatarUrl, csrf_token) {
    fetch(saveAvatarUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token
        },
        body: JSON.stringify({ avatar: new_avatar })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data.message);
    })
    .catch(error => {
        console.error('Error', error);
    })
}

// Function to close all dropdowns except the current one:
function closeAllSelect(element) {
    var dropdownLists, selectedDisplays, dropdownListsLength, selectedDisplaysLength, skipIndex = [];

    // Get all dropdown items and selected displays
    dropdownLists = document.getElementsByClassName("select-items");
    selectedDisplays = document.getElementsByClassName("select-selected");

    dropdownListsLength = dropdownLists.length;
    selectedDisplaysLength = selectedDisplays.length;
    
    // Loop through selected displays and hide dropdowns that are not active
    for (var i = 0; i < selectedDisplaysLength; i++) {
        if (element == selectedDisplays[i]) {
        skipIndex.push(i)
        } else {
        selectedDisplays[i].classList.remove("select-arrow-active");
        }
    }

    // Hide all dropdown lists except the active one
    for (var i = 0; i < dropdownListsLength; i++) {
        if (skipIndex.indexOf(i)) {
        dropdownLists[i].classList.add("select-hide");
        }
    }
}