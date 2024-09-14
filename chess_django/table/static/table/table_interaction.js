let moveListeners = {};  // To store event listeners for moves
let intervalId;  // To manage interval for timers
let isDragging = false;  // Flag to track if a piece is being dragged
let draggedPiece = {};

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
        console.log(state)
        updateUI(tableSocket, state);
    };
}

function updateUI(tableSocket, state) {
    clearBoard();  // Clear the board of pieces and listeners
    colorBoard();  // Color the board
    showPlayers(state);  // Update player names
    showTimes(state);  // Update player times
    addRemovePlayers(tableSocket, state);  // Manage player buttons
    displayWinner(state);  // Display winner if any
    updateMoves(state);  // Update move counter
    displayLastMove(state);  // Function to display last move
    highlightChecks(state);  // Highlight checking squares
    setBoardMoveListeners();  // Set event listeners for move actions
    renderBoard(tableSocket, state);  // Render the board based on state
    renderLastMoves(state)
    console.log("received updated board");
}

function reloadUI(tableSocket, state) {
    clearBoard();  // Re-clear the board of pieces and listeners
    colorBoard();  // Re-color the board
    displayLastMove(state);  // Function to display last move
    highlightChecks(state);  // Highlight checking squares
    renderBoard(tableSocket, state);  // Re-render the board when theme changes
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
    clearLastMovesTable()
}

function clearLastMovesTable() {
    document.getElementById("last_moves").innerHTML = ""
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
        { element: document.getElementById("white_player"), time: document.getElementById("white_time"), name: state.white_player, ready: state.white_player_ready },
        { element: document.getElementById("black_player"), time: document.getElementById("black_time"), name: state.black_player, ready: state.black_player_ready }
    ];
    
    // Update each player's display
    players.forEach(player => {
        player.element.innerHTML = `${player.name}`;
        player.element.classList.toggle("unready", !player.ready);
        player.time.classList.toggle("unready", !player.ready);
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
        { player: "white", sit: "white_player_sit_button", stand: "white_player_stand_button", ready: "white_player_ready_button", unready: "white_player_unready_button" },
        { player: "black", sit: "black_player_sit_button", stand: "black_player_stand_button", ready: "black_player_ready_button", unready: "black_player_unready_button" }
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
    if (player === "white" && state.white_player === "Player 1" || player === "black" && state.black_player === "Player 2") {
        // Show sit button for the appropriate player
        sitButton.classList.remove("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.add("hidden");
        
        sitButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, true, null, null, null);  // Sit down player
        });
    } else if (player === "white" && state.white_player === state.user && state.white_player_ready === false || player === "black" && state.black_player === state.user && state.black_player_ready === false) {
        // Show stand and ready buttons for the appropriate player
        sitButton.classList.add("hidden");
        standButton.classList.remove("hidden");
        readyButton.classList.remove("hidden");
        unreadyButton.classList.add("hidden");
        
        standButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, false, null, null, null);  // Stand up player
        });
        
        readyButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, null, true, null, null);  // Mark player as ready
        });
    } else if (player === "white" && state.white_player === state.user && state.white_player_ready === true || player === "black" && state.black_player === state.user && state.black_player_ready === true) {
        // Show stand and unready buttons for the appropriate player
        sitButton.classList.add("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.remove("hidden");
        
        unreadyButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, null, false, null, null);  // Mark player as unready
        });
    }
}

// Function to reset a button by removing all listeners
function resetButton(buttonId) {
    const button = document.getElementById(buttonId);
    const newButton = button.cloneNode(true);
    button.parentNode.replaceChild(newButton, button);
    return newButton;
}

// Function to update player state on the server
function updatePlayerState(tableSocket, player, playerState, readyState, move, promotion) {
    const update = {
        white_player: player === "white" ? playerState : null,
        black_player: player === "black" ? playerState : null,
        white_player_ready: player === "white" ? readyState : null,
        black_player_ready: player === "black" ? readyState : null,
        move: move,
        promotion: promotion
    };
    tableSocket.send(JSON.stringify(update));
}

// Function to display the winner modal
function displayWinner(state) {
    if (state.winner) {
        const modalWinner = document.getElementById("modal_winner");
        const modalBackground = document.getElementById("modal_background_winner");
        modalWinner.classList.add("show");
        modalBackground.classList.add("show");
        const htmlWinner = document.getElementById("winner");
        if (state.winner === "draw") {
            htmlWinner.innerHTML = `<p>It's a draw!</p>`;
        } else {
            htmlWinner.innerHTML = `<p>${state.winner} has won!</p>`;
        }
    }
}

// Function to update move counter
function updateMoves(state) {
    document.getElementById("moves").innerHTML = `Moves: ${state.total_moves}`;
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
    
    // Prevent default behavior on dragstart to manage custom dragging
    board.addEventListener('dragstart', (event) => event.preventDefault());
    
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
    const symbols_letters = {"00": "h", "01": "g", "02": "f", "03": "e", "04": "d", "05": "c", "06": "b", "07": "a"};
    const symbols_numbers = {"07": "1", "17": "2", "27": "3", "37": "4", "47": "5", "57": "6", "67": "7", "77": "8"};

    // Points for each type of piece
    const points = {"pawn": 1, "bishop": 3, "knight": 3, "rook": 5, "queen": 9};

    // Track the number of each type of piece captured by white and black
    let white_captured = {"pawn": 8, "bishop": 2, "knight": 2, "rook": 2, "queen": 1, "sum": 39};
    let black_captured = {"pawn": 8, "bishop": 2, "knight": 2, "rook": 2, "queen": 1, "sum": 39};

    // Iterate over each square and set pieces or events
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.querySelector(`#square${row}${col}`);
            
            // Add letter symbols at the bottom of the board (for row 0)
            if (row == 0) {
                addSymbolLetters(square, row, col, symbols_letters);
            }
            
            // Add number symbols at the right of the board (for column 7)
            if (col == 7) {
                addSymbolNumbers(square, row, col, symbols_numbers);
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
    document.getElementById("white_captured").innerHTML = white_captured["sum"];
    document.getElementById("black_captured").innerHTML = black_captured["sum"];
}

// Function to add letter symbols to the bottom-right of the squares (for the letter coordinates)
function addSymbolLetters(square, row, col, symbols_letters) {
    square.classList.add("square");  // Ensure square has the "square" class
    let bottomRightSymbol = document.createElement("div");  // Create a div for the letter symbol
    bottomRightSymbol.classList.add("bottom_right_symbol");  // Add the class to position the symbol
    bottomRightSymbol.textContent = symbols_letters[`${row}${col}`];  // Set the letter symbol as content
    square.appendChild(bottomRightSymbol);  // Append the symbol to the square
}

// Function to add number symbols to the top-left of the squares (for the number coordinates)
function addSymbolNumbers(square, row, col, symbols_numbers) {
    square.classList.add("square");  // Ensure square has the "square" class
    let topLeftSymbol = document.createElement("div");  // Create a div for the number symbol
    topLeftSymbol.classList.add("top_left_symbol");  // Add the class to position the symbol
    topLeftSymbol.textContent = symbols_numbers[`${row}${col}`];  // Set the number symbol as content
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
    
    // Enable dragging and click events if it's the player's turn
    if (state.turn === player && state.winner === null && ((player === "white" && state.user === state.white_player) || (player === "black" && state.user === state.black_player))) {
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
        updatePlayerState(tableSocket, null, null, null, move, null);  // Update player state without promotion
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
        updatePlayerState(tableSocket, null, null, null, move, pieceSymbol);  // Update player state with the selected promotion piece
    });
}

// Function to hide promotion modal
function hidePromotionModal() {
    document.querySelector("#modal_promotion").classList.remove("show");  // Hide promotion modal
    document.getElementById("modal_background_promotion").classList.remove("show");  // Hide modal background
}

function renderLastMoves(state) {
    const letters = {7: "a", 6: "b", 5: "c", 4: "d", 3: "e", 2: "f", 1: "g", 0: "h"};
    let count = 1;
    let round;
    last_moves_table = document.getElementById("last_moves");

    for (const board of state.prev_boards_id_moves) {
        if (count % 1 === 0) {
            round = `<br>${parseInt(count)}: `;
        } else {
            round = "";
        }
        last_moves_table.innerHTML += `${decodeMoves(board[1], round, letters)} `;
        count += 0.5;
    }
}

function decodeMoves(move, round, letters) {

    const col1 = letters[move.charAt(1)];
    const row1 = parseInt(move.charAt(0)) + 1;
    const col2 = letters[move.charAt(3)];
    const row2 = parseInt(move.charAt(2)) + 1;

    return `${round}${col1}${row1}-${col2}${row2}`
}