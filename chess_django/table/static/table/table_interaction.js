let moveListeners = [];  // To store event listeners for moves
let intervalId;  // To manage interval for timers

// Runs when the DOM content is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // PUT IN FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    const board = document.getElementById("chess-board");
    
    board.addEventListener('dragstart', (event) => {
        event.preventDefault();
    });

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
    let state;

    const changeImagesButton = document.getElementById('theme');
    changeImagesButton.addEventListener('click', () => {
        renderBoard(tableSocket, state);
    });
    
    // Handle incoming messages from the server
    tableSocket.onmessage = function(e) {
        state = JSON.parse(e.data);
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
        // const board = document.querySelector(".board");
        // const rotateButton = document.getElementById("button_rotate");
        // const dinoButton = document.getElementById("button_dino");
        
        // rotateButton.addEventListener("click", function() {
        //     if (board.classList.contains("rotate")) {
        //         board.classList.remove("rotate");
        //     } else {
        //         board.classList.add("rotate");
        //     }
        // })
        
        // dinoButton.addEventListener("click", function() {
        //     if (style === "classic") {
        //         style = "dino";
        //     } else {
        //         style = "classic";
        //     }
        //     renderBoard(tableSocket, state);
        // })
        // ------------------ BUTTONS REMOVE LATER ------------------------
        
    };
}

// Function to update player names
function showPlayers(state) {
    const players = [
        { element: document.getElementById("white_player"), time: document.getElementById("white_time"), name: state.white_player, ready: state.white_player_ready },
        { element: document.getElementById("black_player"), time: document.getElementById("black_time"), name: state.black_player, ready: state.black_player_ready }
    ];

    players.forEach(player => {
        player.element.innerHTML = `${player.name}`;
        player.element.classList.toggle("unready", !player.ready);
        player.time.classList.toggle("unready", !player.ready);
    });
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
        document.getElementById("modal_background_start").classList.add("show");
        buttonsConfig.forEach(config => {
            setButtonState(tableSocket, state, config);
        });
    } else {
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
    square.classList.remove("draggableElement");
}

// Function to render a specific square with a piece
function renderSquare(state, row, col, tableSocket) {
    const {piece, player, moves} = state.board[row][col];
    const square = document.querySelector(`#square${row}${col}`);
    square.classList.add(piece);
    square.classList.add(player);

    // Enable dragging and click events if it's the player's turn
    if (state.turn === player && state.winner === null && ((player === "white" && state.user === state.white_player) || (player === "black" && state.user === state.black_player))) {
        enableDraggable(square, row, col, piece, player, moves, tableSocket);
    }
}

// Function to enable dragging for a piece
function enableDraggable(square, row, col, piece, player, moves, tableSocket) {
    let isDragging = false;
    
    square.setAttribute("draggable", "false");
    square.classList.add("draggableElement");

    const movingPiece = document.querySelector('.movingPiece');
    const board = document.getElementById("chess-board");
    
    board.addEventListener('dragstart', (event) => {
        event.preventDefault();
    });

    function handleMouseTouchDown(event) {
        isDragging = true;
        board.classList.add("dragging");
        movingPiece.classList.add("showPiece");
        movingPiece.classList.add(piece);
        movingPiece.classList.add(player);

        const { clientX, clientY } = event.type === 'touchstart' ? event.touches[0] : event;
        movingPiece.setAttribute("style", "top: "+(clientY - (0.5 * movingPiece.clientWidth))+"px; left: "+(clientX - (0.5 * movingPiece.clientHeight))+"px;");

        highlightSelectedSquare(square);  // Highlight selected square
        const isPromotion = moves[2];
        moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "move"));
        moves[1].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "attack"));
    }
    
    function handleMouseTouchUp(event) {
        if (isDragging) { 
            isDragging = false;
            board.classList.remove("dragging");
            movingPiece.classList.remove("showPiece");
            movingPiece.classList.remove(piece);
            movingPiece.classList.remove(player);
            colorBoard();  // Reset board colors
            removeMoveListeners();  // Remove existing move listeners
            setTimeout(function() {square.classList.remove("marked")}, 50);
        }
    }

    function handleMouseTouchMove(event) {
        if (isDragging) {
            const { clientX, clientY } = event.type === 'touchmove' ? event.touches[0] : event;
            movingPiece.setAttribute("style", "top: "+(clientY - (0.5 * movingPiece.clientWidth))+"px; left: "+(clientX - (0.5 * movingPiece.clientHeight))+"px;");
        }
    }

    square.addEventListener('mousedown', handleMouseTouchDown);
    square.addEventListener('touchstart', handleMouseTouchDown);

    document.addEventListener('mouseup', handleMouseTouchUp);
    document.addEventListener('touchend', handleMouseTouchUp);

    document.addEventListener('mousemove', handleMouseTouchMove);
    document.addEventListener('touchmove', handleMouseTouchMove);
}

// Function to remove all move listeners
function removeMoveListeners() {
    console.log(moveListeners)
    moveListeners.forEach(function(item) {
        item.element.removeEventListener("mouseup", item.mouseUpListener);
        item.element.removeEventListener("touchend", item.mouseUpListener);
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
    square.addEventListener("mouseup", moveListener);
    square.addEventListener("touchend", moveListener);
    moveListeners.push({element: square, mouseUpListener: moveListener});
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
        queen: { id: "modal_queen", whiteSymbol: "Q", blackSymbol: "q", background: "modal_td_dark" },
        rook: { id: "modal_rook", whiteSymbol: "R", blackSymbol: "r",background: "modal_td_light" },
        knight: { id: "modal_knight", whiteSymbol: "N", blackSymbol: "n", background: "modal_td_dark"},
        bishop: { id: "modal_bishop", whiteSymbol: "B", blackSymbol: "b", background: "modal_td_light" },
    }

    const modalPromotion = document.querySelector("#modal_promotion");
    const modalBackground = document.getElementById("modal_background_promotion");
    modalPromotion.classList.add("show");
    modalBackground.classList.add("show");

    const setPromotionPiece  = function(curr_piece, pieceType, player, pieceSymbol) {
        curr_piece.classList.add(pieceType);
        curr_piece.classList.add(player);
        curr_piece.addEventListener("click", function() {
            modalPromotion.classList.remove("show");
            modalBackground.classList.remove("show");
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
        
        curr_piece.className = '';
        curr_piece.classList.add(pieceInfo.background)

        if (move[0][0] === 6) {
            setPromotionPiece(curr_piece, pieceType, "white", pieceInfo.whiteSymbol);
        } else {
            setPromotionPiece(curr_piece, pieceType, "black", pieceInfo.blackSymbol);
        }
    }
}

// Function to clear the board of pieces and listeners
function clearBoard() {
    for(let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            // Remove all listeners
            let square = document.querySelector(`#square${row}${col}`);
            let newElement = square.cloneNode(true);
            square.parentNode.replaceChild(newElement, square);
            // Remove all pieces
            newElement.className = '';
        }
    }
    colorBoard();
}