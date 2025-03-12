let moveListeners = {};  // To store event listeners for moves
let intervalId;  // To manage interval for timers
let isDragging = false;  // Flag to track if a piece is being dragged
let draggedPiece = {};  // Object to store the dragged piece details
var move_sound;  // Variable to hold the sound for move actions

// Runs when the DOM content is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    setupWebSocket();  // Setup WebSocket for real-time updates
});

// Function to setup WebSocket connection
function setupWebSocket() {
    const tableID = JSON.parse(document.getElementById('table_id').textContent);
    const tableSocket = new WebSocket(`ws://${window.location.host}/ws/table/${tableID}/`);
    let state;  // Store the current state of the game
    
    // Add event listener for theme change button
    document.getElementById('theme').addEventListener('click', () => {
        reloadUI(tableSocket, state);
    });
    
    // Handle incoming messages from the server
    tableSocket.onmessage = function(e) {
        state = JSON.parse(e.data); // Parse the received game state
        console.log(state);  // Log the received state for debugging
        updateUI(tableSocket, state);
    };
}

function updateUI(tableSocket, state) {
    clearBoard();  // Clear the board of pieces and listeners
    rotateBoard(state);  // Rotate the board for the black player
    colorBoard();  // Color the board
    showPlayers(state);  // Update player names
    showTimes(state);  // Update player times
    addRemovePlayers(tableSocket, state);  // Manage player buttons
    displayWinner(state);  // Display winner if any
    displayLastMove(state);  // Function to display last move
    highlightChecks(state);  // Highlight checking squares
    setBoardMoveListeners();  // Set event listeners for move actions
    renderBoard(tableSocket, state);  // Render the board based on state
    renderPrevMoves(tableSocket, state);  // Display the previous moves made in the game
    playMoveSound(state);  // Play sound related to the last move
    renderResignButton(tableSocket, state);  // Show or update the "Resign" button depending on the game state
    renderDrawButton(tableSocket, state);  // Show or update the "Draw" button depending on the game state
    renderNotLoggedModal(state);  // Render NotLoggedModal for guest user
    showLegend();  // Show the game legend
    console.log("Received updated board");
}

function reloadUI(tableSocket, state) {
    clearBoard();  // Re-clear the board of pieces and listeners
    rotateBoard(state);  // Rotate the board for the black player
    colorBoard();  // Re-color the board
    displayLastMove(state);  // Function to display last move
    highlightChecks(state);  // Highlight checking squares
    renderBoard(tableSocket, state);  // Re-render the board when theme changes
    renderPrevMoves(tableSocket, state);  // Re-render the previous moves made in the game
    renderResignButton(tableSocket, state);  // Re-render the "Resign" button depending on the game state
    renderDrawButton(tableSocket, state);  // Display NotLoggedModal when the user is not logged in
    renderNotLoggedModal(state);  // Render NotLoggedModal for guest user
}

// Function to clear the board of pieces and listeners
function clearBoard() {
    for(let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            // Remove all listeners by replacing the element
            let square = document.querySelector(`#square${row}${col}`);
            let newElement = square.cloneNode(true);
            square.parentNode.replaceChild(newElement, square);
            // Remove all pieces by resetting class list
            newElement.className = ''; 
        }
    }
    clearPrevMovesTable();
    clearResignDrawButtons();
    document.getElementById("grid").className = '';
    document.getElementById("modal_not_logged").className = '';
    document.getElementById("white_captured").innerHTML = '';
    document.getElementById("black_captured").innerHTML = '';
}

// Function to rotate the board
function rotateBoard(state) {
    // Rotate the board if the current user is the black player and both players are ready
    if (
        state.black_player === state.user &&
        state.white_player_ready && state.black_player_ready
        ) {
        document.getElementById("grid").classList.add("rotated");

        const table = document.getElementById("chess-board");
        table.innerHTML = '';  // Clear the old table
            
        // Create a new table body
        const new_table = document.createElement("tbody");
        
        // Loop through rows and columns to build the new table
        for (let i = 0; i < 8; i++) {
            const row_element = document.createElement("tr");
            for (let j = 0; j < 8; j++) {
                const column_element = document.createElement("td");
                column_element.id = `square${i}${j}`;  // Set the ID of each square
                row_element.appendChild(column_element);  // Append the square to the row
            }
            new_table.appendChild(row_element);  // Append the row to the table body
        }
        table.appendChild(new_table);  // Append the new table body to the board
    }
}

// Function to clear the table of previous moves (used for move history)
function clearPrevMovesTable() {
    document.getElementById("prev_moves").innerHTML = "";  // Clear the previous moves section

    // Clone the previous button to reset it
    let previous_button = document.getElementById("previous_button");
    let newElement = previous_button.cloneNode(true);
    previous_button.parentNode.replaceChild(newElement, previous_button);
    newElement.className = '';

    // Clone the next button to reset it
    let next_button = document.getElementById("next_button");
    newElement = next_button.cloneNode(true);
    next_button.parentNode.replaceChild(newElement, next_button);
    newElement.className = '';
}

// Function to clear the resign and draw buttons
function clearResignDrawButtons() {
    // Clone the resign button to reset it
    let resign_button = document.getElementById("resign_button");
    let newResignElement = resign_button.cloneNode(true);
    resign_button.parentNode.replaceChild(newResignElement, resign_button);
    newResignElement.className = '';

    // Clone the resign button to reset it
    let draw_button = document.getElementById("draw_button");
    let newDrawElement = draw_button.cloneNode(true);
    draw_button.parentNode.replaceChild(newDrawElement, draw_button);
    newDrawElement.className = '';
}

// Function to color the board with alternating colors
function colorBoard() {
    const colors = ['darkGreen', 'lightGreen', 'darkRed', 'lightRed'];
    for (let row = 0; row < 8; row++){
        for (let col = 0; col < 8; col++) {
            const htmlSquare = document.querySelector(`#square${row}${col}`);
            // Remove any existing color classes
            for (let i = 0; i < colors.length; i++) {
                if (htmlSquare.classList.contains(colors[i])) {
                    htmlSquare.classList.remove(colors[i]);
                }
            }
            // Add dark or light class based on position
            if ((row + col) % 2 == 0) {
                htmlSquare.classList.add('dark');
            } else {
                htmlSquare.classList.add('light');
            }
        }
    }
}
// Function to update player names
function showPlayers(state) {
    const players = [
        {
            player_element: document.getElementById("white_player"),
            name_element: document.getElementById("white_name"),
            avatar_element: document.getElementById("white_avatar"),
            time: document.getElementById("white_time"),
            name: state.white_player,
            avatar: state.white_avatar,
            ready: state.white_player_ready
        },
        {
            player_element: document.getElementById("black_player"),
            name_element: document.getElementById("black_name"),
            avatar_element: document.getElementById("black_avatar"),
            time: document.getElementById("black_time"),
            name: state.black_player,
            avatar: state.black_avatar,
            ready: state.black_player_ready
        }
    ];
    
    // Update each player's display
    players.forEach(player => {
        player.name_element.innerHTML = `${player.name}`;
        player.player_element.classList.toggle("unready", !player.ready);
        player.time.classList.toggle("unready", !player.ready);
        player.avatar_element.classList = "";
        if (player.avatar) {
            player.avatar_element.classList = `avatar-${player.avatar}`;
        } else {
            player.avatar_element.classList = "hidden";
        }
    });
}

// Function to update player times and manage countdown
function showTimes(state) {
    if (intervalId) {
        clearInterval(intervalId);  // Clear any existing interval
    }
    
    let whiteTimeInSeconds = state.white_time_left  // Time left for white player
    let blackTimeInSeconds = state.black_time_left  // Time left for black player
    const whiteTime = document.getElementById("white_time");
    const blackTime = document.getElementById("black_time");
    
    updateDisplay();  // Update the initial display
    
    if (!state.winner) {
        intervalId = setInterval(countDown, 1000);  // Start countdown if there's no winner yet
    }
    
    // Function to decrement time based on current turn
    function countDown() {
        if (state.turn === "white") {
            whiteTimeInSeconds--;
        } else {
            blackTimeInSeconds--;
        }
        updateDisplay();
    }
    
    // Function to update the time display
    function updateDisplay() {
        whiteTime.innerHTML = formatTime(whiteTimeInSeconds);
        blackTime.innerHTML = formatTime(blackTimeInSeconds);
    }
    
    // Function to format time as MM:SS
    function formatTime(time) {
        if (time < 0) time = 0;
        let minutes = Math.floor(time / 60);
        let seconds = Math.trunc(time % 60);
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Function to manage player buttons for sitting, standing, and ready states
function addRemovePlayers(tableSocket, state) {
    const buttonsConfig = [
        {
            player: "white",
            sit: "white_player_sit_button",
            stand: "white_player_stand_button",
            ready: "white_player_ready_button",
            unready: "white_player_unready_button"
        },
        {
            player: "black",
            sit: "black_player_sit_button",
            stand: "black_player_stand_button",
            ready: "black_player_ready_button",
            unready: "black_player_unready_button"
        }
    ];
    
    // Show start modal if players are not ready
    if (!state.white_player_ready || !state.black_player_ready) {
        document.getElementById("modal_background_start").classList.add("show");
        buttonsConfig.forEach(config => {
            setButtonState(tableSocket, state, config);
        });
    } else {
        // Hide start modal if both players are ready
        document.getElementById("modal_background_start").classList.remove("show");
        buttonsConfig.forEach(config => {
            document.getElementById(config.sit).classList.add("hidden");
            document.getElementById(config.stand).classList.add("hidden");
            document.getElementById(config.ready).classList.add("hidden");
            document.getElementById(config.unready).classList.add("hidden");
        });
    }
}

// Function to set the state of player buttons based on current state
function setButtonState(tableSocket, state, config) {
    const { player, sit, stand, ready, unready } = config;
    // Remove old listeners
    const sitButton = resetButton(sit);
    const standButton = resetButton(stand);
    const readyButton = resetButton(ready);
    const unreadyButton = resetButton(unready);
    
    // Configure buttons based on the player's role and readiness
    if (!state.user) {
        sitButton.classList.add("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.add("hidden");
    } else if (
        player === "white" && state.white_player === "Player 1" ||
        player === "black" && state.black_player === "Player 2"
    ) {
        // Show sit button for the appropriate player
        sitButton.classList.remove("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.add("hidden");
        
        sitButton.addEventListener("click", function() {
            currentGameButton(true);  // Remove inactive class from current game button
            updateState(tableSocket, player, true, null, null, null, null, null, null);  // Sit down player
        });
    } else if (
        player === "white" && state.white_player === state.user && state.white_player_ready === false ||
        player === "black" && state.black_player === state.user && state.black_player_ready === false
    ) {
        // Show stand and ready buttons for the appropriate player
        sitButton.classList.add("hidden");
        standButton.classList.remove("hidden");
        readyButton.classList.remove("hidden");
        unreadyButton.classList.add("hidden");
        
        standButton.addEventListener("click", function() {
            currentGameButton(false);  // Add inactive class to current game button
            updateState(tableSocket, player, false, null, null, null, null, null, null);  // Stand up player
        });
        
        readyButton.addEventListener("click", function() {
            updateState(tableSocket, player, null, true, null, null, null, null, null);  // Mark player as ready
        });
    } else if (
        player === "white" && state.white_player === state.user && state.white_player_ready === true ||
        player === "black" && state.black_player === state.user && state.black_player_ready === true
    ) {
        // Show stand and unready buttons for the appropriate player
        sitButton.classList.add("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.remove("hidden");
        
        unreadyButton.addEventListener("click", function() {
            updateState(tableSocket, player, null, false, null, null, null, null, null);  // Mark player as unready
        });
    } else {
        // Hide all buttons
        sitButton.classList.add("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.add("hidden");
    }

    // Hide sit button to ensure a user cannot join two tables in same time
    if (state.already_in_game) {
        sitButton.classList.add("hidden");
    }
}

// Function to reset a button by removing all listeners
function resetButton(buttonId) {
    const button = document.getElementById(buttonId);
    const newButton = button.cloneNode(true);
    button.parentNode.replaceChild(newButton, button);
    return newButton;
}

// Function to update state on the server
function updateState(tableSocket, player, playerState, readyState, move, promotion, requested_board, resign, draw) {
    const update = {
        white_player: player === "white" ? playerState : null,
        black_player: player === "black" ? playerState : null,
        white_player_ready: player === "white" ? readyState : null,
        black_player_ready: player === "black" ? readyState : null,
        move: move,
        promotion: promotion,
        requested_board: requested_board,
        resign: resign,
        draw: draw
    };
    tableSocket.send(JSON.stringify(update));
}

// Function to toggles the "inactive" class on the "current-game-button" element
function currentGameButton(active) {
    // Get the DOM element of the current-game-button
    const gameButton = document.getElementById("current-game-button");

    if (active) {
        // Remove the "inactive" class to indicate an active state
        gameButton.classList.remove("inactive");
    } else {
        // Add the "inactive" class to indicate an inactive state
        gameButton.classList.add("inactive");
    }
}

// Function to display the winner modal
function displayWinner(state) {
    // Check if the state object contains a winner
    if (state.winner) {
        // Get the modal element for displaying the winner
        const modalWinner = document.getElementById("modal_winner");
        // Add the "show" class to make the modal visible
        modalWinner.classList.add("show");

        // Get the modal background element (used for click outside to close)
        const modalBackground = document.getElementById("modal_background_winner");
        // Add the "show" class to the background to display it
        modalBackground.classList.add("show");

        // Get the HTML element where the winner's message will be shown
        const htmlWinner = document.getElementById("winner");

        // Get the root HTML element to add classes indicating the winner
        const htmlElement = document.documentElement;

        // Check if the game was a draw
        if (state.winner === "draw") {
            // If it's a draw, display the draw message in the modal
            htmlWinner.innerHTML = `<p>It's a draw!</p>`;
        } else {
            // If there's a winner, check if it's the white player
            if (state.winner === "white") {
                // Display the white player's name as the winner
                htmlWinner.innerHTML = `<p>${state.white_player} has won!</p>`;
                
                // Add a class to style the page indicating white as the winner - change images to bones
                htmlElement.classList.add("white-winner");
            } else {
                // Otherwise, display the black player's name as the winner
                htmlWinner.innerHTML = `<p>${state.black_player} has won!</p>`;

                // Add a class to style the page indicating black as the winner - change images to bones
                htmlElement.classList.add("black-winner");
            }
        }

        // Add an event listener to the background so that clicking it will close the modal
        modalBackground.addEventListener("click", function() {
            // Remove the "show" class from both the modal and background to hide them
            modalWinner.classList.remove("show");
            modalBackground.classList.remove("show");

            // Remove any winner styling classes from the root element
            htmlElement.classList.remove("white-winner");
            htmlElement.classList.remove("black-winner");
        })
    }
}

// Function to display last move
function displayLastMove(state) {
    // Check if state is not the starting position
    if (state.last_move) {
        // Extract the starting row and column from the last move string
        const fromRow = state.last_move.charAt(0);
        const fromCol = state.last_move.charAt(1);

        // Extract the ending row and column from the last move string
        const toRow = state.last_move.charAt(2);
        const toCol = state.last_move.charAt(3);

        // Add the 'last_move_from' class to the square from which the piece was moved
        document.querySelector(`#square${fromRow}${fromCol}`).classList.add("last_move_from")

        // Add the 'last_move_to' class to the square to which the piece was moved
        document.querySelector(`#square${toRow}${toCol}`).classList.add("last_move_to")
    }
}

// Function to highlight squares that are under check
function highlightChecks(state) {
    if (state.checking) {  // Check if any piece is currently checking the opponent's king
        state.checking.forEach(function([row, col]) {
            document.querySelector(`#square${row}${col}`).classList.add("checking")  // Highlight the squares putting the king in check
        });
    }
}

// Function to set listeners for piece movements
function setBoardMoveListeners() {
    const movingPiece = document.querySelector('.movingPiece');
    const board = document.getElementById("chess-board");
    const grid = document.getElementById("grid");
    
    // Prevent default behavior on dragstart to manage custom dragging
    board.addEventListener('dragstart', (event) => event.preventDefault());
    if (window.matchMedia('(pointer: coarse)').matches) {
        grid.addEventListener('contextmenu', (event) => event.preventDefault());
    }
    
    // Handle mouse or touch release event
    function handleEndDrag() {
        if (isDragging) {
            const {piece, player, square} = draggedPiece;
            isDragging = false;
            board.classList.remove("dragging");
            movingPiece.classList.remove("showPiece", piece, player);
            colorBoard();  // Reset board colors
            removeMoveListeners();  // Remove existing move listeners
            setTimeout(function() {square.classList.remove("marked")}, 50);  // Remove square highlight with a delay
        }
    }
    
    // Handle mouse or touch move event to update the piece's position
    function handleDrag(event) {
        if (isDragging) {
            const { clientX, clientY } = event.type === 'touchmove' ? event.touches[0] : event;
            movingPiece.style.top = `${clientY - (0.5 * movingPiece.clientWidth)}px`;
            movingPiece.style.left = `${clientX - (0.5 * movingPiece.clientHeight)}px`;
        }
    }
    
    // Set listeners for mouse and touch release
    document.addEventListener('mouseup', handleEndDrag);
    document.addEventListener('touchend', handleEndDrag);
    
    // Set listeners for mouse and touch move
    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('touchmove', handleDrag);
}

// Function to render the board based on the current state
function renderBoard(tableSocket, state) {
    // Define the symbols for the letters and numbers on the chessboard
    const symbols_letters = {"0": "h", "1": "g", "2": "f", "3": "e", "4": "d", "5": "c", "6": "b", "7": "a"};
    const symbols_numbers = {"0": "1", "1": "2", "2": "3", "3": "4", "4": "5", "5": "6", "6": "7", "7": "8"};

    // Points for each type of piece
    const points = {"pawn": 1, "bishop": 3, "knight": 3, "rook": 5, "queen": 9};

    // Track the number of each type of piece captured by white and black
    let white_captured = {"pawn": 8, "bishop": 2, "knight": 2, "rook": 2, "queen": 1, "sum": 39};
    let black_captured = {"pawn": 8, "bishop": 2, "knight": 2, "rook": 2, "queen": 1, "sum": 39};

    // Iterate over each square and set pieces or events
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.querySelector(`#square${row}${col}`);
            
            if (
                state.black_player === state.user &&
                state.white_player_ready && state.black_player_ready
                ) {
                // Add letter symbols at the bottom of the board (for row 0)
                if (row == 7) {
                    addSymbolLetters(square, row, col, symbols_letters);
                }
                
                // Add number symbols at the right of the board (for column 7)
                if (col == 0) {
                    addSymbolNumbers(square, row, col, symbols_numbers);
                }
            } else {
                // Add letter symbols at the bottom of the board (for row 0)
                if (row == 0) {
                    addSymbolLetters(square, row, col, symbols_letters);
                }
                
                // Add number symbols at the right of the board (for column 7)
                if (col == 7) {
                    addSymbolNumbers(square, row, col, symbols_numbers);
                }
            }
            
            // Setup events for each square
            setupSquareEvents(square);
            
            const square_object = state.board[row][col];
            
            // If there's a piece on the square, manage captured pieces and render it
            if (square_object) {
                manageCaptured(square_object, points, white_captured, black_captured);
                renderSquare(state, square, row, col, tableSocket);  // Render pieces on the board
            }
        }
    }
    
    // Update the displayed captured points
    updateCaptured(white_captured, black_captured);
}

// Function to update the display of captured pieces for both white and black players
function updateCaptured (white_captured, black_captured) {
    // Get the HTML elements where captured pieces will be displayed
    const white_captured_element = document.getElementById("white_captured");
    const black_captured_element = document.getElementById("black_captured");

    // Adds the extra pawn after promotion
    addPawns(white_captured);
    addPawns(black_captured);

    // Add captured white pieces to the HTML (black pieces captured by white)
    addCapturedToHTML(white_captured["pawn"], "black", "pawn", white_captured_element);
    addCapturedToHTML(white_captured["knight"], "black", "knight", white_captured_element);
    addCapturedToHTML(white_captured["bishop"], "black", "bishop", white_captured_element);
    addCapturedToHTML(white_captured["rook"], "black", "rook", white_captured_element);
    addCapturedToHTML(white_captured["queen"], "black", "queen", white_captured_element);

    // Add captured black pieces to the HTML (white pieces captured by black)
    addCapturedToHTML(black_captured["pawn"], "white", "pawn", black_captured_element);
    addCapturedToHTML(black_captured["knight"], "white", "knight", black_captured_element);
    addCapturedToHTML(black_captured["bishop"], "white", "bishop", black_captured_element);
    addCapturedToHTML(black_captured["rook"], "white", "rook", black_captured_element);
    addCapturedToHTML(black_captured["queen"], "white", "queen", black_captured_element);

    // Add a score difference indicator if white is ahead in captured points
    if (white_captured["sum"] > black_captured["sum"]) {
        const newDiv = document.createElement("div");
        newDiv.innerHTML = `+${white_captured["sum"] - black_captured["sum"]}`;
        white_captured_element.appendChild(newDiv);
    }

    // Add a score difference indicator if black is ahead in captured points
    if (black_captured["sum"] > white_captured["sum"]) {
        const newDiv = document.createElement("div");
        newDiv.innerHTML = `+${black_captured["sum"] - white_captured["sum"]}`;
        black_captured_element.appendChild(newDiv);
    }
}

// Function to adjust the number of pawns if the player makes athe promotion
function addPawns(list) {
    for (let piece of ["knight", "bishop", "rook", "queen"]) {
        if (list[piece] < 0) {
            list["pawn"] += list[piece];
        }
    }
}

// Function to add a specified quantity of captured pieces to the HTML
function addCapturedToHTML(quantity, player, class_name, element) {
    for (let i = 0; i < quantity; i++) {
        const newDiv = document.createElement("div");  // Common class for captured pieces
        newDiv.classList.add("captured_piece", "small_piece");
        newDiv.classList.add(player, class_name);
        if (i === 0) {
            newDiv.classList.add("first");  // Mark the first piece for styling
        }
        element.appendChild(newDiv);  // Append the new piece to the specified element
    }
}

// Function to add letter symbols to the bottom-right of the squares (for the letter coordinates)
function addSymbolLetters(square, row, col, symbols_letters) {
    square.classList.add("square");  // Ensure square has the "square" class
    let bottomRightSymbol = document.createElement("div");  // Create a div for the letter symbol
    bottomRightSymbol.classList.add("bottom_right_symbol");  // Add the class to position the symbol
    bottomRightSymbol.textContent = symbols_letters[`${col}`];  // Set the letter symbol as content
    square.appendChild(bottomRightSymbol);  // Append the symbol to the square
}

// Function to add number symbols to the top-left of the squares (for the number coordinates)
function addSymbolNumbers(square, row, col, symbols_numbers) {
    square.classList.add("square");  // Ensure square has the "square" class
    let topLeftSymbol = document.createElement("div");  // Create a div for the number symbol
    topLeftSymbol.classList.add("top_left_symbol");  // Add the class to position the symbol
    topLeftSymbol.textContent = symbols_numbers[`${row}`];  // Set the number symbol as content
    square.appendChild(topLeftSymbol);  // Append the symbol to the square
}

// Function to setup basic events for each square
function setupSquareEvents(square) {
    square.classList.remove("draggableElement");  // Remove draggable class to reset square state
}

// Function to manage captured pieces and update the captured points
function manageCaptured(square_object, points, white_captured, black_captured) {
    // Only manage pieces that are not kings
    if (square_object.piece !== "king") {
        if (square_object.player === "white") {
            // Update black's captured pieces and their sum
            black_captured[square_object.piece] -= 1
            black_captured["sum"] -= points[square_object.piece]
        } else {
            // Update white's captured pieces and their sum
            white_captured[square_object.piece] -= 1
            white_captured["sum"] -= points[square_object.piece]
        }
    }
}

// Function to render a specific square with a piece
function renderSquare(state, square, row, col, tableSocket) {
    const {piece, player, moves} = state.board[row][col];
    square.classList.add(piece, player);  // Add piece and player class to the square
    
    // Enable dragging and click events if it's the player's turn, there is no winner and it's not a previous board
    if (
        state.turn === player &&
        state.winner === null &&
        (
            state.prev_boards_id_moves.length === 0 ||
            state.board_id === state.prev_boards_id_moves[state.prev_boards_id_moves.length - 1][0]
        ) &&
        (
            (player === "white" && state.user === state.white_player) ||
            (player === "black" && state.user === state.black_player)
        )
        
    ) {
        enableDraggable(square, row, col, piece, player, moves, tableSocket);  // Enable dragging for the current piece
    }
}

// Function to enable dragging for a piece
function enableDraggable(square, row, col, piece, player, moves, tableSocket) {
    const movingPiece = document.querySelector('.movingPiece');
    const board = document.getElementById("chess-board");

    square.classList.add("draggableElement");  // Make the square draggable

    // Add listeners for initiating drag on mouse or touch down
    square.addEventListener('mousedown', dragStart);
    square.addEventListener('touchstart', dragStart);
    
    // Handle mouse or touch down event to initiate dragging
    function dragStart(event) {
        isDragging = true;
        draggedPiece = {piece:piece, player:player, square:square}

        board.classList.add("dragging");  // Add dragging class to the board
        movingPiece.classList.add("showPiece", piece, player);
        
        const { clientX, clientY } = event.type === 'touchstart' ? event.touches[0] : event;
        movingPiece.style.top = `${clientY - (0.5 * movingPiece.clientWidth)}px`;
        movingPiece.style.left = `${clientX - (0.5 * movingPiece.clientHeight)}px`;
        
        highlightSelectedSquare(square);  // Highlight selected square

        const isPromotion = moves[2];  // Check if the move is a promotion
        moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "move"));
        moves[1].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "attack"));
    }
}

// Function to remove all move listeners
function removeMoveListeners() {
    Object.keys(moveListeners).forEach(key => {
        const [listener, event, element] = moveListeners[key];
        element.removeEventListener(event, listener);  // Remove each move listener
    });
    moveListeners = {};  // Reset the move listeners object
}

// Function to highlight the selected square
function highlightSelectedSquare(element) {
    if (element.classList.contains('dark')) {
        element.classList.remove('dark');
        element.classList.add('marked');
    } else {
        element.classList.remove('light');
        element.classList.add('marked');
    }
}

// Function to add a possible move event listener
function addPossibleMove(move, oldRow, oldCol, tableSocket, isPromotion, type) {
    const [row, col] = move
    const square = document.querySelector(`#square${row}${col}`);
    const fullMove = [[oldRow, oldCol], [row, col]];
    
    highlightMoveSquare(square, type); // Highlight possible moves or attacks
    addMoveListener(fullMove, square, isPromotion, tableSocket);  // Add listener for executing the move
}

// Function to highlight move or attack squares
function highlightMoveSquare(square, type) {
    if (square.classList.contains('dark')) {
        square.classList.remove('dark');
        square.classList.add(type === "move" ? 'darkGreen' : 'darkRed');  // Highlight the move or attack square
    } else {
        square.classList.remove('light');
        square.classList.add(type === "move" ? 'lightGreen' : 'lightRed');  // Highlight the move or attack square
    }
}

// Function to add move listener to a square
function addMoveListener(move, square, isPromotion, tableSocket) {
    const squareId = square.id;
    const board = document.getElementById("chess-board");
    
    const moveListener = function() {handleMove(move, isPromotion, tableSocket)};  // Listener for mouse events
    const touchListener = function(event) {
        const touch = event.changedTouches[0];
        const rect = square.getBoundingClientRect();
        if (isTouchInsideSquare(touch, rect)) {
                handleMove(move, isPromotion, tableSocket);  // Listener for touch events
            }
    };
    
    // Add listeners for move execution on mouse or touch events
    square.addEventListener("mouseup", moveListener);
    board.addEventListener("touchend", touchListener);
    
    // Store the listeners to remove them later
    moveListeners[`moveListener${squareId}`] = [moveListener, "mouseup", square];
    moveListeners[`touchListener${squareId}`] = [touchListener, "touchend", board];
}

// Function to check if touch is inside a square
function isTouchInsideSquare(touch, rect) {
    return touch.clientX >= rect.left && touch.clientX <= rect.right &&
           touch.clientY >= rect.top && touch.clientY <= rect.bottom;
}
    
// Function to handle move and promotion
function handleMove(move, isPromotion, tableSocket) {
    if (!isPromotion) {
        updateState(tableSocket, null, null, null, move, null, null, null, null);  // Update state without promotion
    } else {
        showPromotionModal(move, tableSocket);  // Show promotion modal if promotion is required
    }
}
    
// Function to show promotion modal and handle promotion selection
function showPromotionModal(move, tableSocket) {
    const promotionObject = {
        queen: { id: "modal_queen", whiteSymbol: "Q", blackSymbol: "q", background: "modal_td_dark" },
        rook: { id: "modal_rook", whiteSymbol: "R", blackSymbol: "r",background: "modal_td_light" },
        knight: { id: "modal_knight", whiteSymbol: "N", blackSymbol: "n", background: "modal_td_dark"},
        bishop: { id: "modal_bishop", whiteSymbol: "B", blackSymbol: "b", background: "modal_td_light" },
    }
    
    document.querySelector("#modal_promotion").classList.add("show");  // Show promotion modal
    document.getElementById("modal_background_promotion").classList.add("show");  // Show modal background
    
    setPromotionOptions(move, promotionObject, tableSocket);
}

function setPromotionOptions(move, promotionObject, tableSocket) {
    // Iterate through possible promotion pieces and set their respective event listeners
    for (const pieceType in promotionObject) {
        const pieceInfo = promotionObject[pieceType];
        let curr_piece = document.getElementById(pieceInfo.id);
        
        // Remove previous listeners by replacing the element
        let removeListeners = curr_piece.cloneNode(true);
        curr_piece.parentNode.replaceChild(removeListeners, curr_piece);
        curr_piece = removeListeners
        
        curr_piece.className = '';  // Reset class list
        curr_piece.classList.add(pieceInfo.background);  // Set the appropriate background
        
        // Set promotion pieces for white or black based on the move
        if (move[0][0] === 6) {
            setPromotionPieceListener(curr_piece, pieceType, "white", pieceInfo.whiteSymbol, move, tableSocket);  // Set promotion piece for white
        } else {
            setPromotionPieceListener(curr_piece, pieceType, "black", pieceInfo.blackSymbol, move, tableSocket);  // Set promotion piece for black
        }
    }
}

function setPromotionPieceListener(curr_piece, pieceType, player, pieceSymbol, move, tableSocket) {
    curr_piece.classList.add(pieceType);
    curr_piece.classList.add(player);
    curr_piece.addEventListener("click", function() {
        hidePromotionModal();
        updateState(tableSocket, null, null, null, move, pieceSymbol, null, null, null);  // Update state with the selected promotion piece
    });
}

// Function to hide promotion modal
function hidePromotionModal() {
    document.querySelector("#modal_promotion").classList.remove("show");  // Hide promotion modal
    document.getElementById("modal_background_promotion").classList.remove("show");  // Hide modal background
}

function renderPrevMoves(tableSocket, state) {
    // Mapping of numeric indices to chess column letters (for decoding moves)
    const columnLetters = {7: "a", 6: "b", 5: "c", 4: "d", 3: "e", 2: "f", 1: "g", 0: "h"};

    // Get the table element where previous moves will be displayed
    const prevMovesTable = document.getElementById("prev_moves");
    let moveContainer;
    
    // Iterate over each move in the previous boards and moves array
    for (let moveIndex = 0; moveIndex < state.prev_boards_id_moves.length; moveIndex++) {
        // Create a new line (div) every two moves (i.e., for each round)
        if (moveIndex % 2 === 0) {
            moveContainer = document.createElement("div");
            moveContainer.classList.add("moves_container"); // Add class for styling the container
        }

        // Decode the current move and append it to the newly created line
        moveContainer = decodeMoves(tableSocket, state, moveIndex, moveContainer, columnLetters);

        // If it's the last move and it's an even index (white's move), add a placeholder for black
        if (moveIndex === state.prev_boards_id_moves.length - 1 && moveIndex % 2 === 0) {
            // Create a placeholder span for the black move
            placeHolder = document.createElement("span");
            placeHolder.classList.add("movesListBlack"); // Add class for black move placeholder styling
            moveContainer.appendChild(placeHolder); // Append the placeholder to the line
        }

        // Append the fully constructed line (with 1 or 2 moves) to the previous moves table
        prevMovesTable.appendChild(moveContainer);
    }
}

function decodeMoves(tableSocket, state, moveIndex, moveContainer, columnLetters) {
    // Destructure the elements of prev_boards_id_moves array into separate variables
    const [ boardId, move, pieceImage ] = state.prev_boards_id_moves[moveIndex];

    // Create a span element to hold the move's details (piece + move)
    let pieceAndMove = document.createElement("span");

    // Determine if the move is made by White (even moveCounter) or Black (odd moveCounter)
    if (moveIndex % 2 === 0) {
        pieceAndMove.classList.add("movesListWhite");  // If White's move, style the move container as 'movesListWhite'
        addRoundNumber(moveContainer, moveIndex);  // Add round number only for White's move
    } else {
        // If Black's move, style the move container as 'movesListBlack'
        pieceAndMove.classList.add("movesListBlack");
    }

    // Add move details (piece type and position)
    addMove(pieceAndMove, move, pieceImage, columnLetters);
    
    // Check if the current moveIndex corresponds to the currently displayed board
    if (boardId === state.board_id) {
        pieceAndMove.classList.add("currentBoard");  // Highlight the current board
        addNavigationButtonsListeners(tableSocket, state, moveIndex);  // Enable navigation between moves
    } else {
        // Add a click event listener to the move that triggers an update of the game state to the selected board
        pieceAndMove.addEventListener('click', () => {
            updateState(tableSocket, null, null, null, null, null, boardId, null, null);  // Update the game state to reflect the selected move/board
        });
    }
    
    // Append the fully constructed pieceAndMove (piece + move) to the current line
    moveContainer.appendChild(pieceAndMove);
    
    // Return the updated moveContainer to be further processed in renderPrevMoves
    return moveContainer;
}

function addRoundNumber(newLine, moveIndex) {
    // Create a span for the round number (e.g., "1:", "2:")
    const roundSpan = document.createElement("span");
    roundSpan.classList.add("round"); // Add class for round number styling
    roundSpan.textContent = `${parseInt((moveIndex / 2) + 1)}:`; // Calculate and set round number
    newLine.appendChild(roundSpan); // Append the round number to the current line
}

function addMove(pieceAndMove, move, pieceImage, columnLetters) {
    // Create a span for the piece involved in the move (e.g., pawn, knight)
    const pieceElement = document.createElement("span");
    pieceElement.classList.add(pieceImage[0]); // Add class for the piece type (e.g., pawn, knight)
    pieceElement.classList.add(pieceImage[1]); // Add class for the color (white/black)
    pieceElement.classList.add("movesListPiece", "small_piece"); // Add class for general piece styling
    pieceAndMove.appendChild(pieceElement); // Append the piece span to the move details
    
    // Create a span for the decoded move (end position)
    const movePositionElement = document.createElement("span");
    const endColumn = columnLetters[move.charAt(3)]; // Get the ending column letter from the move string
    const endRow = parseInt(move.charAt(2)) + 1; // Get the ending row number from the move string
    movePositionElement.textContent = `${endColumn}${endRow}`; // Set the decoded move text (e.g., "e4", "d5")
    movePositionElement.classList.add("movesListMove"); // Add class for styling the move text
    
    // Append the decoded move (e.g., "e4") to the pieceAndMove span
    pieceAndMove.appendChild(movePositionElement);
}

function addNavigationButtonsListeners(tableSocket, state, moveIndex) {
    // Enable previous board button navigation if available
    if (moveIndex > 0) {
        const previous_button = document.getElementById("previous_button");
        const prev_board = state.prev_boards_id_moves[moveIndex - 1][0];
        previous_button.addEventListener('click', () => {
            updateState(tableSocket, null, null, null, null, null, prev_board, null, null);  // Update state to previous board
        });
        previous_button.classList.add("active");  // Activate the button
    }

    // Enable next board button navigation if available
    if (moveIndex < state.prev_boards_id_moves.length - 1) {
        const next_board = state.prev_boards_id_moves[moveIndex + 1][0];
        const next_button = document.getElementById("next_button");
        next_button.addEventListener('click', () => {
            updateState(tableSocket, null, null, null, null, null, next_board, null, null);  // Update state to next board
        });
        next_button.classList.add("active");  // Activate the button
    }
}

function playMoveSound(state) {
    // Check if sound should be played based on the state
    if (state.play_audio) {
        // If there is an existing sound playing, pause it and reset its time to avoid overlap
        if (move_sound) {
            move_sound.pause();
            move_sound.currentTime = 0;
        }

        let piece;  // Variable to store the name of the audio file to play
        let htmlElement = document.documentElement;  // Get the <html> element of the document
        
        // Check if the <html> element has a class of "classic-mode"
        if (htmlElement.classList.contains("classic-mode")) {
            piece = "classic_sound";  // Use a generic classic sound if in "classic-mode"
        } else {
            piece = state.board[state.last_move[2]][state.last_move[3]]["piece"];  // Get the last moved piece
        }

        // Create a new Audio object for the move sound based on the piece's name
        move_sound = new Audio(`/static/table/sounds/${piece}.mp3`);
        move_sound.volume = 0.4;  // Set the volume to a quieter level (40% of maximum)
        move_sound.playbackRate = 1.5;  // Speed up the playback rate of the sound (1.5x faster than normal)
        move_sound.play();  // Play the sound
    }
}

function renderResignButton(tableSocket, state) {
    // Check if the user is either the white or black player, and if there is at least one previous move.
    // Also, ensure that the current board is the latest one and no winner has been determined yet.
    if (
        (state.user === state.white_player || state.user === state.black_player) &&  // Verify user is a player in the game
        state.prev_boards_id_moves.length > 0 &&  // Ensure there are previous moves
        state.board_id === state.prev_boards_id_moves[state.prev_boards_id_moves.length - 1][0] &&  // Confirm this is the latest board
        state.winner == null  // Ensure no winner has been declared yet
        ) {
        const resignButton = document.getElementById("resign_button");  // Get the resign button element from the DOM
        resignButton.classList.add("active");  // Add 'active' class to make the button visible or enabled

        const timeout = 1500;  // Set the timeout duration (1.5 seconds) for holding the button
        let resignTimer;  // Variable to store the timer
        let isHoldingButton;  // Flag to track if the button is being held

        // Function to handle the start of holding the resign button (mousedown or touchstart)
        function resignStart() {
            isHoldingButton = true;  // Set the flag to true, indicating the button is being held
            resignTimer = setTimeout(function() {
                // After 1.5 seconds, execute the resignation by calling updateState with resign=true
                updateState(tableSocket, null, null, null, null, null, null, true, null);
            }, timeout);  // Timer runs after the timeout duration
        };

        // Function to handle the release of the resign button (mouseup or touchend)
        function resignStop(e) {
            if (isHoldingButton) {  // Only clear the timer if the button was being held
                if (resignTimer) {
                    clearTimeout(resignTimer);  // Cancel the resignation if the mouse was released before the timer ended
                }
                e.preventDefault();
                isHoldingButton = false;
            }
        };
        
        // Add event listeners for starting to hold the button (mousedown or touchstart)
        resignButton.addEventListener("mousedown", resignStart);
        resignButton.addEventListener("touchstart", resignStart);

        // Add event listeners for releasing the button (mouseup or touchend)
        window.addEventListener("mouseup", resignStop);
        resignButton.addEventListener("touchend", resignStop);
    }
}

function renderDrawButton(tableSocket, state) {
    // Check if the user is either the white or black player, and if there is at least one previous move.
    // Also, ensure that the current board is the latest one and no winner has been determined yet.
    if (
        (state.user === state.white_player || state.user === state.black_player) &&  // Verify user is a player in the game
        state.prev_boards_id_moves.length > 0 &&  // Ensure there are previous moves
        state.board_id === state.prev_boards_id_moves[state.prev_boards_id_moves.length - 1][0] &&  // Confirm this is the latest board
        state.winner == null  // Ensure no winner has been declared yet
        ) {
        const drawButton = document.getElementById("draw_button");  // Get the draw button element from the DOM
        drawButton.classList.add("active");  // Add 'active' class to make the button visible or enabled
        
        // Check if the current user is the white player
        if (state.user === state.white_player) {
            if (state.white_draw) {  // If the white player has already requested a draw
                drawButton.classList.add("player_draw_request");  // Indicate the player's draw request
            } else if (state.black_draw) {  // If the black player has requested a draw
                drawButton.classList.add("opponent_draw_request");  // Indicate the opponent's draw request
            }
        // Check if the current user is the black player
        } else if (state.user === state.black_player) {
            if (state.black_draw) {  // If the black player has already requested a draw
                drawButton.classList.add("player_draw_request");  // Indicate the player's draw request
            } else if (state.white_draw) {  // If the white player has requested a draw
                drawButton.classList.add("opponent_draw_request");  // Indicate the opponent's draw request
            }
        }

        const timeout = 1500;  // Set the timeout duration (1.5 seconds) for holding the button
        let drawTimer;  // Variable to store the timer
        let isHoldingButton;  // Flag to track if the button is being held

        // Function to handle the start of holding the draw button (mousedown or touchstart)
        function drawStart() {
            isHoldingButton = true;  // Set the flag to true, indicating the button is being held
            drawTimer = setTimeout(function() {
                // After 1.5 seconds, execute the resignation by calling updateState with draw=true
                updateState(tableSocket, null, null, null, null, null, null, null, true);
            }, timeout);  // Timer runs after the timeout duration
        };

        // Function to handle the release of the draw button (mouseup or touchend)
        function drawStop(e) {
            if (isHoldingButton) {  // Only clear the timer if the button was being held
                if (drawTimer) {
                    clearTimeout(drawTimer);  // Cancel the draw proposition if the mouse was released before the timer ended
                }
                e.preventDefault();
                isHoldingButton = false;
            }
        };

        // Add event listeners for starting to hold the button (mousedown or touchstart)
        drawButton.addEventListener("mousedown", drawStart);
        drawButton.addEventListener("touchstart", drawStart);

        // Add event listeners for releasing the button (mouseup or touchend)
        window.addEventListener("mouseup", drawStop);
        drawButton.addEventListener("touchend", drawStop);
    }
}

function renderNotLoggedModal(state) {
    // Check if the user is not logged in, and either white or black player is not ready
    if (!state.user && (!state.white_player_ready || !state.black_player_ready)) {
        // Show the "Not Logged" modal by adding the 'show' class
        document.getElementById("modal_not_logged").classList.add("show");
    }
}

// Function to show and hide the legend modal when interacting with the legend button or background
function showLegend() {
    const legend_button = document.getElementById("legend_button");
    const modal_background_legend = document.getElementById("modal_background_legend");

    legend_button.addEventListener("click", function() {
        modal_background_legend.classList.add("show");
    })
    
    modal_background_legend.addEventListener("click", function() {
        modal_background_legend.classList.remove("show");
    })
}