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
        console.log("received updated board");
        const board = JSON.parse(e.data);

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                if (board.board[row][col] !== null) {
                    uploadBoard(board.board, row, col, tableSocket);
                }
            }
        }
    }; 

});

function colorBoard() {
    for (let row = 0; row < 8; row++){
        for (let col = 0; col < 8; col++) {
            const htmlSquare = document.querySelector(`#square${row}${col}`);
            if (htmlSquare.classList.contains('darkGreen')) {
                htmlSquare.classList.remove('darkGreen')
            }
            if (htmlSquare.classList.contains('lightGreen')) {
                htmlSquare.classList.remove('lightGreen')
            }
            if ((row + col) % 2 == 0) {
                htmlSquare.classList.add('dark');
            } else {
                htmlSquare.classList.add('light');
            }
        }
    }
}
    
function uploadBoard(board, row, col, tableSocket) {
    const boardSquare = board[row][col];
    const {piece, player, moves} = boardSquare
    
    const image = getImageSource(piece, player);
    const htmlSquare = document.querySelector(`#square${row}${col}`);
    htmlSquare.innerHTML = `${image}`;
    htmlSquare.addEventListener("click", function() {
        console.log(moves);
        colorBoard();
        moves[0].forEach(move => addPossibleMove(move, row, col, tableSocket));
    });
};

function addPossibleMove(move, oldRow, oldCol, tableSocket) {
    const row = move[0]
    const col = move[1]
    const htmlPossibleMove = document.querySelector(`#square${row}${col}`);
    if (htmlPossibleMove.classList.contains('dark')) {
        htmlPossibleMove.classList.remove('dark');
        htmlPossibleMove.classList.add('darkGreen');
    } else {
        htmlPossibleMove.classList.remove('light');
        htmlPossibleMove.classList.add('lightGreen');
    }
    htmlPossibleMove.addEventListener("click", function() {
        const move = [[oldRow, oldCol], [row, col]]
        console.log(move)
        tableSocket.send(JSON.stringify({
            'move': move
        }));
    })

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

