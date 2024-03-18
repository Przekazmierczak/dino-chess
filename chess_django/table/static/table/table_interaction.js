let moveListeners = [];

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
        
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                if (state.board[row][col] !== null) {
                    uploadBoard(state, row, col, tableSocket);
                }
            }
        }
        console.log("received updated board");
    }; 

});

function uploadBoard(state, row, col, tableSocket) {
    const boardSquare = state.board[row][col];
    const turn = state.turn;
    const {piece, player, moves} = boardSquare
    
    const image = getImageSource(piece, player);
    const htmlSquare = document.querySelector(`#square${row}${col}`);
    htmlSquare.innerHTML = `${image}`;
    if (turn === player) {
        htmlSquare.addEventListener("click", function() {
            colorBoard();
            removeMoveListeners();
            moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket, "move"));
            moves[1].forEach(move => addPossibleMove(move, row, col, tableSocket, "attack"));
        });
    }
};

function addPossibleMove(move, oldRow, oldCol, tableSocket, type) {
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
    let moveListener = function() {
        const move = [[oldRow, oldCol], [row, col]];
        tableSocket.send(JSON.stringify({
            'move': move
        }));
    }
    htmlPossibleMove.addEventListener("click", moveListener);
    moveListeners.push({element: htmlPossibleMove, listener: moveListener});
}

function clearBoard() {
    colorBoard();
    removeAllListeners();
    removePieces();
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

function removeMoveListeners() {
    moveListeners.forEach(function(item) {
        item.element.removeEventListener("click", item.listener);
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
    
    if (piece in pieceImages && player in pieceImages[piece]) {
        return `<img src="/static/table/pieces_images/${pieceImages[piece][player]}.png" class="pieceImage" alt="${pieceImages[piece][player]}">`;
    } else {
        return ""
    }
}