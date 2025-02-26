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

    dropdownElement = avatarSelectContainer.getElementsByTagName("select")[0];
    dropdownLength = dropdownElement.length;

    // For each element, create a new DIV that will act as the selected item:
    selectedItem = document.createElement("DIV");
    selectedItem.setAttribute("class", "select-selected");
    selectedItem.innerHTML = dropdownElement.options[dropdownElement.selectedIndex].innerHTML;
    avatarSelectContainer.appendChild(selectedItem);

    // For each element, create a new DIV that will contain the option list:
    dropdownItemsContainer = document.createElement("DIV");
    dropdownItemsContainer.setAttribute("class", "select-items select-hide");

    for (var i = 1; i < dropdownLength; i++) {
        // For each option in the original select element, create a new DIV that will act as an option item:
        dropdownOptionItem = document.createElement("DIV");
        dropdownOptionItem.innerHTML = dropdownElement.options[i].innerHTML;
        dropdownOptionItem.addEventListener("click", function(e) {
            // When an item is clicked, update the original select box, and the selected item:
            var options, optionIndex, siblingNode, selectElement, headerElement, totalOptions, selectedItems;
            selectElement = this.parentNode.parentNode.getElementsByTagName("select")[0];
            totalOptions = selectElement.length;
            headerElement = this.parentNode.previousSibling;
            for (optionIndex = 0; optionIndex < totalOptions; optionIndex++) {
                if (selectElement.options[optionIndex].innerHTML == this.innerHTML) {
                    selectElement.selectedIndex = optionIndex;
                    headerElement.innerHTML = this.innerHTML;
                    options = this.parentNode.getElementsByClassName("same-as-selected");
                    selectedItems = options.length;
                    for (siblingNode = 0; siblingNode < selectedItems; siblingNode++) {
                    options[siblingNode].removeAttribute("class");
                    }
                    this.setAttribute("class", "same-as-selected");
                    break;
                }
            }
            headerElement.click();
        });
        dropdownItemsContainer.appendChild(dropdownOptionItem);
    }
    
    avatarSelectContainer.appendChild(dropdownItemsContainer);
    selectedItem.addEventListener("click", function(e) {
        // When the select box is clicked, close any other select boxes, and open/close the current select box:
        e.stopPropagation();
        closeAllSelect(this);
        this.nextSibling.classList.toggle("select-hide");
        this.classList.toggle("select-arrow-active");
    });


    function closeAllSelect(element) {
    // A function that will close all select boxes in the document, except the current select box:
    var dropdownLists, selectedDisplays, dropdownListsLength, selectedDisplaysLength, skipIndex = [];
    dropdownLists = document.getElementsByClassName("select-items");
    selectedDisplays = document.getElementsByClassName("select-selected");
    dropdownListsLength = dropdownLists.length;
    selectedDisplaysLength = selectedDisplays.length;
    for (var i = 0; i < selectedDisplaysLength; i++) {
        if (element == selectedDisplays[i]) {
        skipIndex.push(i)
        } else {
        selectedDisplays[i].classList.remove("select-arrow-active");
        }
    }
    for (var i = 0; i < dropdownListsLength; i++) {
        if (skipIndex.indexOf(i)) {
        dropdownLists[i].classList.add("select-hide");
        }
    }
    }

    // If the user clicks anywhere outside the select box, then close all select boxes:
    document.addEventListener("click", closeAllSelect);
});