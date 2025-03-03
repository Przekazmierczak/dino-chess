document.addEventListener('DOMContentLoaded', function () {
    var table = document.getElementById("historyTable");
    for (var i = 0, row; row = table.rows[i]; i++) {
        // Calculate the time difference between the current time and the timestamp in the first cell of the row
        var timePast = Date.now() - row.cells[0].innerHTML;

        // Convert the time difference into human-readable units (e.g., days, hours, minutes)

        // Calculate the number of days from the time difference
        var days = Math.floor(timePast/86400000);
        if (days > 0) {
            // If the time difference is in days, update the cell with the corresponding text and continue to the next row
            updateCellWithTime(days, "day", row);
            continue;
        }

        // Calculate the number of hours from the time difference
        var hours = Math.floor(timePast/3600000);
        if (hours > 0) {
            // If the time difference is in hours, update the cell with the corresponding text and continue to the next row
            updateCellWithTime(hours, "hour", row);
            continue;
        }

        // Calculate the number of minutes from the time difference
        var minutes = Math.floor(timePast/60000);
        if (minutes > 0) {
            // If the time difference is in minutes, update the cell with the corresponding text and continue to the next row
            updateCellWithTime(minutes, "minute", row);
            continue;
        }

        // Default case: If the time difference is less than a minute, display "Few seconds ago"
        row.cells[0].innerHTML = "Few seconds ago";
    }

    function updateCellWithTime(quantity, unit, row) {
        // Append an "s" to the unit if the value is greater than 1 (e.g., "days" instead of "day")
        row.cells[0].innerHTML = `${quantity} ${unit}${(quantity == 1) ? "": "s"} ago`;
    }

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
    const csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
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

    // Function to change the avatar's appearance based on the selected value
    function changeAvatar(value) {
        document.querySelector("#avatar").classList = "";
        document.querySelector("#avatar").classList.add(value);
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

    // Event listener to close dropdowns when clicking outside
    document.addEventListener("click", closeAllSelect);
});