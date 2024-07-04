let moveListeners = [];
let intervalId;
let style = "dino";

document.addEventListener('DOMContentLoaded', function () {
    colorBoard();

    const tableID = JSON.parse(document.getElementById('table_id').textContent);
    
    const tableSocket = new WebSocket(`ws://${window.location.host}/ws/table/${tableID}/`);
        
    tableSocket.onmessage = function(e) {
        const state = JSON.parse(e.data);
        console.log(state)
        clearBoard();
        showPlayers(state);
        showTimes(state);
        addRemovePlayers(tableSocket, state)
        displayWinner(state);
        highlightChecks(state);
        updateMoves(state);
        renderBoard(tableSocket, state);

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
});

function showPlayers(state) {
    const whitePlayer = document.getElementById("white_player");
    whitePlayer.innerHTML = `${state.white_player}`;
    const blackPlayer = document.getElementById("black_player");
    blackPlayer.innerHTML = `${state.black_player}`;
}

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

function addRemovePlayers(tableSocket, state) {
    const buttonsConfig = [
        { player: "white", sit: "white_player_sit_button", stand: "white_player_stand_button", ready: "white_player_ready_button", unready: "white_player_unready_button" },
        { player: "black", sit: "black_player_sit_button", stand: "black_player_stand_button", ready: "black_player_ready_button", unready: "black_player_unready_button" }
    ];

    if (state.white_player_ready !== true || state.black_player_ready !== true) {
        buttonsConfig.forEach(config => {
            setButtonState(tableSocket, state, config.player, config.sit, config.stand, config.ready, config.unready);
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

function setButtonState(tableSocket, state, player, sitButtonId, standButtonId, readyButtonId, unreadyButtonId) {
    // Remove old listeners
    const sitButton = resetButton(sitButtonId);
    const standButton = resetButton(standButtonId);
    const readyButton = resetButton(readyButtonId);
    const unreadyButton = resetButton(unreadyButtonId);

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

function resetButton(buttonId) {
    const button = document.getElementById(buttonId);
    const newButton = button.cloneNode(true);
    button.parentNode.replaceChild(newButton, button);
    return newButton;
}

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

function displayWinner(state) {
    if (state.winner !== null) {
        modal_winner.classList.add("show");
        htmlWinner = document.getElementById("winner");
        if (state.winner === "draw") {
            htmlWinner.innerHTML = `<p>It's a draw!</p>`;
        } else {
            htmlWinner.innerHTML = `<p>${state.winner} has won!</p>`;
        }
    }
}

function highlightChecks(state) {
    if (state.checking !== null) {
        state.checking.forEach(function([row, col]) {
            const boardSquare = document.querySelector(`#square${row}${col}`);
            boardSquare.classList.add("checking")
        });
    }
}

function updateMoves(state) {
    const moves = document.getElementById("moves");
    moves.innerHTML = `Moves: ${state.total_moves}`;
}

function renderBoard(tableSocket, state) {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            setupSquareEvents(row, col);
            if (state.board[row][col] !== null) {
                renderSquare(state, row, col, tableSocket);
            }
        }
    }
}

function setupSquareEvents(row, col) {
    const square = document.querySelector(`#square${row}${col}`);
    square.removeAttribute("draggable");
    square.classList.remove("draggableElement");
    square.addEventListener("mouseover", () => square.classList.add("mouseover"));
    square.addEventListener("mouseleave", () => square.classList.remove("mouseover"));
}

function renderSquare(state, row, col, tableSocket) {
    const {piece, player, moves} = state.board[row][col];
    const image = getImageSource(piece, player);
    const square = document.querySelector(`#square${row}${col}`);
    square.innerHTML = `${image}`;

    if (state.turn === player && state.winner === null && ((player === "white" && state.user === state.white_player) || (player === "black" && state.user === state.black_player))) {
        square.setAttribute("draggable", "true");
        square.classList.add("draggableElement");

        square.addEventListener('dragstart', (event) => {
            square.classList.add("dragging");
            square.click();
        });
        square.addEventListener("dragend", () => square.classList.remove("dragging"));

        square.addEventListener("click", function() {
            colorBoard();
            removeMoveListeners();
            highlightSelectedSquare(square)
            const isPromotion = moves[2]
            moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "move"));
            moves[1].forEach(move => addPossibleMove(move, row, col, tableSocket, isPromotion, "attack"));
        });
    }
}

function highlightSelectedSquare(element) {
    if (element.classList.contains('dark')) {
        element.classList.remove('dark');
        element.classList.add('marked');
    } else {
        element.classList.remove('light');
        element.classList.add('marked');
    }
}

function addPossibleMove(move, oldRow, oldCol, tableSocket, isPromotion, type) {
    const [row, col] = move
    const square = document.querySelector(`#square${row}${col}`);

    if (square.classList.contains('dark')) {
        square.classList.remove('dark');
        if (type === "move") {
            square.classList.add('darkGreen');
        } else {
            square.classList.add('darkRed');
        }
    } else {
        square.classList.remove('light');
        if (type === "move") {
            square.classList.add('lightGreen');
        } else {
            square.classList.add('lightRed');
        }
    }
    addMoveListener(oldRow, oldCol, row, col, square, isPromotion, tableSocket);
}

function addMoveListener(oldRow, oldCol, row, col, square, isPromotion, tableSocket) {
    let moveListener = function() {
        const move = [[oldRow, oldCol], [row, col]];
        let promotion

        if (isPromotion === false) {
            tableSocket.send(JSON.stringify({
                'white_player': null,
                'black_player': null,
                'white_player_ready': null,
                'black_player_ready': null,
                'move': move,
                'promotion': null
            }));
        } else {
            modal_promotion.classList.add("show");
            const promotionObject = {
                queen: ["modal_queen", "Queen_white", "Q", "Queen_black", "q"],
                rook: ["modal_rook", "Rook_white", "R", "Rook_black", "r"],
                knight: ["modal_knight", "Knight_white", "N",  "Knight_black", "n"],
                bishop: ["modal_bishop", "Bishop_white", "B", "Bishop_black", "b"],
            }
            function pickPiece(pickedPiece) {
                promotion = pickedPiece;
                modal_promotion.classList.remove("show");
                tableSocket.send(JSON.stringify({
                    'white_player': null,
                    'black_player': null,
                    'white_player_ready': null,
                    'black_player_ready': null,
                    'move': move,
                    'promotion': promotion
                }));
            }
            for (const piece in promotionObject) {
                if (Object.hasOwnProperty.call(promotionObject, piece)) {
                    const list = promotionObject[piece];
                    let curr_piece = document.getElementById(list[0]);
                    // Remove previous listeners
                    let removeListeners = curr_piece.cloneNode(true);
                    curr_piece.parentNode.replaceChild(removeListeners, curr_piece);
                    curr_piece = removeListeners

                    if (oldRow === 6) {
                        curr_piece.innerHTML = `<img src="/static/table/pieces_images/${list[1]}.png" class="pieceImage" alt=${list[1]}></img>`
                        curr_piece.addEventListener("click", function() {
                            pickPiece(list[2])
                        });
                    } else {
                        curr_piece.innerHTML = `<img src="/static/table/pieces_images/${list[3]}.png" class="pieceImage" alt=${list[3]}></img>`
                        curr_piece.addEventListener("click", function() {
                            pickPiece(list[4])
                        });
                    }
                }
            }
        }
    }
    
    let dropListener= function(event) {
        event.preventDefault();
        moveListener(event);
    }

    square.addEventListener("click", moveListener);
    square.addEventListener("dragover", function(event) {
        event.preventDefault();
    });
    square.addEventListener("drop", dropListener);

    moveListeners.push({element: square, clickListener: moveListener, dropListener: dropListener});
}

function clearBoard() {
    colorBoard();
    removeAllListeners();
    removePieces();
    removeChecking();
}

function colorBoard() {
    for (let row = 0; row < 8; row++){
        for (let col = 0; col < 8; col++) {
            const htmlSquare = document.querySelector(`#square${row}${col}`);
            const colors = ['darkGreen', 'lightGreen', 'darkRed', 'lightRed'];
            for (let i = 0; i < colors.length; i++) {
                if (htmlSquare.classList.contains(colors[i])) {
                    htmlSquare.classList.remove(colors[i]);
                }
            }
            if ((row + col) % 2 == 0) {
                htmlSquare.classList.add('dark');
            } else {
                htmlSquare.classList.add('light');
            }
        }
    }
}

function removeAllListeners() {
    for(let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            let htmlSquare = document.querySelector(`#square${row}${col}`);
            let newElement = htmlSquare.cloneNode(true);
            htmlSquare.parentNode.replaceChild(newElement, htmlSquare);
        }
    }
}

function removePieces() {
    for(let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            let htmlSquare = document.querySelector(`#square${row}${col}`);
            htmlSquare.innerHTML = "";
        }
    }
}

function removeChecking() {
    for(let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            let htmlSquare = document.querySelector(`#square${row}${col}`);
            if (htmlSquare.classList.contains("checking")) {
                htmlSquare.classList.remove("checking");
            }
        }
    }
}

function removeMoveListeners() {
    console.log(moveListeners)
    moveListeners.forEach(function(item) {
        item.element.removeEventListener("click", item.clickListener);
        item.element.removeEventListener("drop", item.dropListener);
    });
    moveListeners = [];
}

function getImageSource(piece, player) {
    const pieceImages = {
        "pawn": {
            "white": "Pawn_white",
            "black": "Pawn_black"
        },
        "rook": {
            "white": "Rook_white",
            "black": "Rook_black"
        },
        "knight": {
            "white": "Knight_white",
            "black": "Knight_black"
        },
        "bishop": {
            "white": "Bishop_white",
            "black": "Bishop_black"
        },
        "queen": {
            "white": "Queen_white",
            "black": "Queen_black"
        },
        "king": {
            "white": "King_white",
            "black": "King_black"
        }
    };
    
    if (style === "classic") {
        if (piece in pieceImages && player in pieceImages[piece]) {
            return `<img src="/static/table/pieces_images/${pieceImages[piece][player]}.png" class="pieceImage" alt="${pieceImages[piece][player]}">`;
        } else {
            return ""
        }
    } else {
        if (piece in pieceImages && player in pieceImages[piece]) {
            return `<img src="/static/table/pieces_images/d${pieceImages[piece][player]}.png" class="pieceImage" alt="${pieceImages[piece][player]}">`;
        } else {
            return ""
        }
    }
}