let moveListeners = [];  // To store event listeners for moves
let intervalId;  // To manage interval for timers
let style = "dino";  // Default style for pieces

// Runs when the DOM content is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    colorBoard();  // Initialize the board colors
    setupWebSocket();  // Setup WebSocket for real-time updates
});

// Function to color the board with alternating colors
function colorBoard() {
    for (let row = 0; row < 8; row++){
        for (let col = 0; col < 8; col++) {
            const htmlSquare = document.querySelector(`#square${row}${col}`);
            const colors = ['darkGreen', 'lightGreen', 'darkRed', 'lightRed'];
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

// Function to setup WebSocket connection
function setupWebSocket() {
    const tableID = JSON.parse(document.getElementById('table_id').textContent);
    const tableSocket = new WebSocket(`ws://${window.location.host}/ws/table/${tableID}/`);
    
    // Handle incoming messages from the server
    tableSocket.onmessage = function(e) {
        const state = JSON.parse(e.data);
        console.log(state)
    
        clearBoard();  // Clear board and listeners
        showPlayers(state);  // Update player names
        showTimes(state);  // Update player times
        addRemovePlayers(tableSocket, state);  // Manage player buttons
        displayWinner(state);  // Display winner if any
        highlightChecks(state);  // Highlight checking squares
        updateMoves(state);  // Update move counter
        renderBoard(tableSocket, state);  // Render the board based on state
    
        console.log("received updated board");
        
        // ------------------ BUTTONS REMOVE LATER ------------------------
        const board = document.querySelector(".board");
        const rotateButton = document.getElementById("button_rotate");
        const dinoButton = document.getElementById("button_dino");
        
        rotateButton.addEventListener("click", function() {
            if (board.classList.contains("rotate")) {
                board.classList.remove("rotate");
            } else {
                board.classList.add("rotate");
            }
        })
        
        dinoButton.addEventListener("click", function() {
            if (style === "classic") {
                style = "dino";
            } else {
                style = "classic";
            }
            renderBoard(tableSocket, state);
        })
        // ------------------ BUTTONS REMOVE LATER ------------------------
        
    };
}

// Function to update player names
function showPlayers(state) {
    document.getElementById("white_player").innerHTML = `${state.white_player}`;
    document.getElementById("black_player").innerHTML = `${state.black_player}`;
}

// Function to update player times and manage countdown
function showTimes(state) {
    if (intervalId) {
        clearInterval(intervalId);
    }

    let whiteTimeInSeconds = state.white_time_left
    let blackTimeInSeconds = state.black_time_left
    const whiteTime = document.getElementById("white_time");
    const blackTime = document.getElementById("black_time");

    updateDisplay();

    if (state.winner === null) {
        intervalId = setInterval(countDown, 1000);
    }

    function countDown() {
        if (state.turn === "white") {
            whiteTimeInSeconds--;
        } else {
            blackTimeInSeconds--;
        }
        updateDisplay();
    }

    function updateDisplay() {
        whiteTime.innerHTML = formatTime(whiteTimeInSeconds);
        blackTime.innerHTML = formatTime(blackTimeInSeconds);
    }

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

    if (state.white_player_ready !== true || state.black_player_ready !== true) {
        buttonsConfig.forEach(config => {
            setButtonState(tableSocket, state, config);
        });
    } else {
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

    if (player === "white" && state.white_player === "Player 1" || player === "black" && state.black_player === "Player 2") {
        sitButton.classList.remove("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.add("hidden");

        sitButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, true, null, null, null);
        });
    } else if (player === "white" && state.white_player === state.user && state.white_player_ready === false || player === "black" && state.black_player === state.user && state.black_player_ready === false) {
        sitButton.classList.add("hidden");
        standButton.classList.remove("hidden");
        readyButton.classList.remove("hidden");
        unreadyButton.classList.add("hidden");
        
        standButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, false, null, null, null);
        });

        readyButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, null, true, null, null);
        });

    } else if (player === "white" && state.white_player === state.user && state.white_player_ready === true || player === "black" && state.black_player === state.user && state.black_player_ready === true) {
        sitButton.classList.add("hidden");
        standButton.classList.add("hidden");
        readyButton.classList.add("hidden");
        unreadyButton.classList.remove("hidden");
        
        unreadyButton.addEventListener("click", function() {
            updatePlayerState(tableSocket, player, null, false, null, null);
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
    if (state.winner !== null) {
        const modalWinner = document.getElementById("modal_winner");
        modalWinner.classList.add("show");
        const htmlWinner = document.getElementById("winner");
        if (state.winner === "draw") {
            htmlWinner.innerHTML = `<p>It's a draw!</p>`;
        } else {
            htmlWinner.innerHTML = `<p>${state.winner} has won!</p>`;
        }
    }
}

// Function to highlight squares that are under check
function highlightChecks(state) {
    if (state.checking !== null) {
        state.checking.forEach(function([row, col]) {
            const boardSquare = document.querySelector(`#square${row}${col}`);
            boardSquare.classList.add("checking")
        });
    }
}

// Function to update move counter
function updateMoves(state) {
    const moves = document.getElementById("moves");
    moves.innerHTML = `Moves: ${state.total_moves}`;
}

// Function to render the board based on the current state
function renderBoard(tableSocket, state) {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            setupSquareEvents(row, col);  // Setup events for each square
            if (state.board[row][col] !== null) {
                renderSquare(state, row, col, tableSocket);  // Render pieces on the board
            }
        }
    }
}

// Function to setup basic events for each square
function setupSquareEvents(row, col) {
    const square = document.querySelector(`#square${row}${col}`);
    square.removeAttribute("draggable");
    square.classList.remove("draggableElement");
    square.addEventListener("mouseover", () => square.classList.add("mouseover"));
    square.addEventListener("mouseleave", () => square.classList.remove("mouseover"));
}

// Function to render a specific square with a piece
function renderSquare(state, row, col, tableSocket) {
    const {piece, player, moves} = state.board[row][col];
    const image = getImageSource(piece, player);
    const square = document.querySelector(`#square${row}${col}`);
    square.innerHTML = `${image}`;

    // Enable dragging and click events if it's the player's turn
    if (state.turn === player && state.winner === null && ((player === "white" && state.user === state.white_player) || (player === "black" && state.user === state.black_player))) {
        enableDraggable(square, row, col, moves, tableSocket);
    }
}

// Function to get the image source for a piece based on its type and player
function getImageSource(piece, player) {
    const pieceImages = {
        "pawn": {"white": "Pawn_white", "black": "Pawn_black"},
        "rook": {"white": "Rook_white",  "black": "Rook_black"},
        "knight": {"white": "Knight_white",  "black": "Knight_black"},
        "bishop": {"white": "Bishop_white",  "black": "Bishop_black"},
        "queen": {"white": "Queen_white",  "black": "Queen_black"},
        "king": {"white": "King_white",  "black": "King_black"}
    };
    const prefix = style === "classic" ? "" : "d";
    if (piece in pieceImages && player in pieceImages[piece]) {
        return `<img src="/static/table/pieces_images/${prefix}${pieceImages[piece][player]}.png" class="pieceImage" alt="${pieceImages[piece][player]}">`;
    } else {
        return ""
    }
}

// Function to enable dragging for a piece
function enableDraggable(square, row, col, moves, tableSocket) {
    square.setAttribute("draggable", "true");
    square.classList.add("draggableElement");

    square.addEventListener('dragstart', () => {
        square.classList.add("dragging");
        square.click();
    });

    square.addEventListener("dragend", () => square.classList.remove("dragging"));

    square.addEventListener("click", () => {
        colorBoard();  // Reset board colors
        removeMoveListeners();  // Remove existing move listeners
        highlightSelectedSquare(square);  // Highlight selected square
        const isPromotion = moves[2];
        moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "move"));
        moves[1].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "attack"));
    });
}

// Function to remove all move listeners
function removeMoveListeners() {
    console.log(moveListeners)
    moveListeners.forEach(function(item) {
        item.element.removeEventListener("click", item.clickListener);
        item.element.removeEventListener("drop", item.dropListener);
    });
    moveListeners = [];
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

    if (square.classList.contains('dark')) {
        square.classList.remove('dark');
        square.classList.add(type === "move" ? 'darkGreen' : 'darkRed');
    } else {
        square.classList.remove('light');
        square.classList.add(type === "move" ? 'lightGreen' : 'lightRed');
    }
    addMoveListener(fullMove, square, isPromotion, tableSocket);
}

// Function to add move listener to a square
function addMoveListener(move, square, isPromotion, tableSocket) {
    const moveListener = function() {handleMove(move, isPromotion, tableSocket)};

    const dropListener = function(event) {
        event.preventDefault();
        moveListener(event);
    };

    square.addEventListener("click", moveListener);
    square.addEventListener("dragover", function(event) {event.preventDefault();});
    square.addEventListener("drop", dropListener);

    moveListeners.push({element: square, clickListener: moveListener, dropListener: dropListener});
}

// Function to handle move and promotion
function handleMove(move, isPromotion, tableSocket) {
    if (!isPromotion) {
        updatePlayerState(tableSocket, null, null, null, move, null);
    } else {
        showPromotionModal(move, tableSocket);
    }
}

// Function to show promotion modal and handle promotion selection
function showPromotionModal(move, tableSocket) {
    const promotionObject = {
        queen: { id: "modal_queen", white: "Queen_white", whiteSymbol: "Q", black: "Queen_black", blackSymbol: "q" },
        rook: { id: "modal_rook", white: "Rook_white", whiteSymbol: "R", black: "Rook_black", blackSymbol: "r" },
        knight: { id: "modal_knight", white: "Knight_white", whiteSymbol: "N", black: "Knight_black", blackSymbol: "n" },
        bishop: { id: "modal_bishop", white: "Bishop_white", whiteSymbol: "B", black: "Bishop_black", blackSymbol: "b" },
    }

    const modalPromotion = document.querySelector("#modal_promotion");
    modalPromotion.classList.add("show");

    const setPromotionPiece  = function(curr_piece, pieceName, pieceSymbol) {
        curr_piece.innerHTML = `<img src="/static/table/pieces_images/${pieceName}.png" class="pieceImage" alt=${pieceName}></img>`
        curr_piece.addEventListener("click", function() {
            modalPromotion.classList.remove("show");
            updatePlayerState(tableSocket, null, null, null, move, pieceSymbol);
        });
    }

    for (const pieceType in promotionObject) {
        const pieceInfo = promotionObject[pieceType];
        let curr_piece = document.getElementById(pieceInfo.id);
        
        // Remove previous listeners
        let removeListeners = curr_piece.cloneNode(true);
        curr_piece.parentNode.replaceChild(removeListeners, curr_piece);
        curr_piece = removeListeners

        if (move[0][0] === 6) {
            setPromotionPiece(curr_piece, pieceInfo.white, pieceInfo.whiteSymbol);
        } else {
            setPromotionPiece(curr_piece, pieceInfo.black, pieceInfo.blackSymbol);
        }
    }
}

// Function to clear the board of pieces and listeners
function clearBoard() {
    colorBoard();
    for(let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            // Remove all listeners
            let square = document.querySelector(`#square${row}${col}`);
            let newElement = square.cloneNode(true);
            square.parentNode.replaceChild(newElement, square);
            // Remove all pieces
            newElement.innerHTML = "";
            // Remove all checking
            newElement.classList.remove("checking");
        }
    }
}