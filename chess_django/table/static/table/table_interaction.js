let moveListeners = [];
let style = "dino";

document.addEventListener('DOMContentLoaded', function () {
    colorBoard();

    const tableID = JSON.parse(document.getElementById('table_id').textContent);
    
    const tableSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/table/'
        + tableID
        + '/'
        );
        
        tableSocket.onmessage = function(e) {
            const state = JSON.parse(e.data);
            console.log(state)
        clearBoard();
        joinRemovePlayers(tableSocket, state)
        winner(state);
        checking(state);
        updateMoves(state);
        uploadBoard(tableSocket, state);


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
            uploadBoard(tableSocket, state);
        })
        // ------------------ BUTTONS REMOVE LATER ------------------------
        
    }; 
});

function joinRemovePlayers(tableSocket, state) {
    const whitePlayer = document.getElementById("white_player");
    whitePlayer.innerHTML = `${state.white_player}`;
    const blackPlayer = document.getElementById("black_player");
    blackPlayer.innerHTML = `${state.black_player}`;

    const whitePlayerSitButton = document.getElementById("white_player_sit_button");
    const whitePlayerStandButton = document.getElementById("white_player_stand_button");

    const blackPlayerSitButton = document.getElementById("black_player_sit_button");
    const blackPlayerStandButton = document.getElementById("black_player_stand_button");

    setButtonState(tableSocket, state, "white", whitePlayerSitButton, whitePlayerStandButton);
    setButtonState(tableSocket, state, "black", blackPlayerSitButton, blackPlayerStandButton);
}

function setButtonState(tableSocket, state, player, sitButton, standButton) {
    // Remove old listeners
    let newElementSit = sitButton.cloneNode(true);
    sitButton.parentNode.replaceChild(newElementSit, sitButton);
    sitButton = newElementSit;
    
    let newElementStand = standButton.cloneNode(true);
    standButton.parentNode.replaceChild(newElementStand, standButton);
    standButton = newElementStand;

    if (player === "white" && state.white_player === "Player 1" || player === "black" && state.black_player === "Player 2") {
        sitButton.classList.remove("hidden");
        standButton.classList.add("hidden");

        sitButton.addEventListener("click", function() {
            let white_player = null
            let black_player = null
            if (player === "white") {
                white_player = true
            } else {
                black_player = true
            }
            tableSocket.send(JSON.stringify({
                'white_player': white_player,
                'black_player': black_player,
                'move': null,
                'promotion': null
            }));
        });
    } else if (player === "white" && state.white_player === state.user || player === "black" && state.black_player === state.user) {
        sitButton.classList.add("hidden");
        standButton.classList.remove("hidden");

        standButton.addEventListener("click", function() {
            let white_player = null
            let black_player = null
            if (player === "white") {
                white_player = false
            } else {
                black_player = false
            }
            tableSocket.send(JSON.stringify({
                'white_player': white_player,
                'black_player': black_player,
                'move': null,
                'promotion': null
            }));
        });
    } else {
        sitButton.classList.add("hidden");
        standButton.classList.add("hidden");
    }
}

function winner(state) {
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

function checking(state) {
    if (state.checking !== null) {
        state.checking.forEach(function(element) {
            const boardSquare = document.querySelector(`#square${element[0]}${element[1]}`);
            boardSquare.classList.add("checking")
        });
    }
}

function updateMoves(state) {
    const moves = document.getElementById("moves");
    moves.innerHTML = `Moves: ${state.total_moves}`;
}

function uploadBoard(tableSocket, state) {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            mouseOver(row, col);
            removeDraggable(row, col);
            if (state.board[row][col] !== null) {
                uploadSquare(state, row, col, tableSocket);
            }
        }
    }
}

function removeDraggable(row, col) {
    const boardSquare = document.querySelector(`#square${row}${col}`);
    boardSquare.removeAttribute("draggable");
    if (boardSquare.classList.contains("draggableElement")) {
        boardSquare.classList.remove("draggableElement");
    }
}

function mouseOver(row, col) {
    const boardSquare = document.querySelector(`#square${row}${col}`);
    boardSquare.addEventListener("mouseover", function(event) {
        event.target.classList.add("mouseover");
    });
    boardSquare.addEventListener("mouseleave", function(event) {
        event.target.classList.remove("mouseover");
    });
}

function uploadSquare(state, row, col, tableSocket) {
    const boardSquare = state.board[row][col];
    const turn = state.turn;
    const {piece, player, moves} = boardSquare
    
    const image = getImageSource(piece, player);
    const htmlSquare = document.querySelector(`#square${row}${col}`);
    htmlSquare.innerHTML = `${image}`;
    if (turn === player && state.winner === null) {
        
        // PUT INTO FUNCTION ---------
        htmlSquare.setAttribute("draggable", "true");
        htmlSquare.classList.add("draggableElement");
    
        // let img = new Image();
        // img.src = "/static/table/pieces_images/Queen_white.png";

        htmlSquare.addEventListener('dragstart', (event) => {
            htmlSquare.classList.add("dragging");
            // event.dataTransfer.setDragImage(img, 100, 100);
            htmlSquare.click();
        });
        htmlSquare.addEventListener("dragend", () => {
            htmlSquare.classList.remove("dragging");
        });
        // --------------------

        htmlSquare.addEventListener("click", function() {
            colorBoard();
            removeMoveListeners();
            addMarked(htmlSquare)
            const iFpromotion = moves[2]
            moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket, iFpromotion, "move"));
            moves[1].forEach(move => addPossibleMove(move, row, col, tableSocket, iFpromotion, "attack"));
        });
    }
};

function addMarked(element) {
    if (element.classList.contains('dark')) {
        element.classList.remove('dark');
        element.classList.add('marked');
    } else {
        element.classList.remove('light');
        element.classList.add('marked');
    }
}

function addPossibleMove(move, oldRow, oldCol, tableSocket, iFpromotion, type) {
    const row = move[0]
    const col = move[1]
    
    const htmlPossibleMove = document.querySelector(`#square${row}${col}`);
    if (htmlPossibleMove.classList.contains('dark')) {
        htmlPossibleMove.classList.remove('dark');
        if (type === "move") {
            htmlPossibleMove.classList.add('darkGreen');
        } else {
            htmlPossibleMove.classList.add('darkRed');
        }
    } else {
        htmlPossibleMove.classList.remove('light');
        if (type === "move") {
            htmlPossibleMove.classList.add('lightGreen');
        } else {
            htmlPossibleMove.classList.add('lightRed');
        }
    }
    pushMove(oldRow, oldCol, row, col, htmlPossibleMove, iFpromotion, tableSocket);
}

function pushMove(oldRow, oldCol, row, col, htmlPossibleMove, iFpromotion, tableSocket) {
    let moveListener = function() {
        const move = [[oldRow, oldCol], [row, col]];
        let promotion

        if (iFpromotion === false) {
            tableSocket.send(JSON.stringify({
                'white_player': null,
                'black_player': null,
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

    htmlPossibleMove.addEventListener("click", moveListener);
    htmlPossibleMove.addEventListener("dragover", function(event) {
        event.preventDefault();
    });
    htmlPossibleMove.addEventListener("drop", dropListener);

    moveListeners.push({element: htmlPossibleMove, clickListener: moveListener, dropListener: dropListener});
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