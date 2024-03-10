document.addEventListener('DOMContentLoaded', function () {
    
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
                    uploadBoard(board.board, row, col);
                }
            }
        }
    }; 

});
    
function uploadBoard(board, row, col) {
    const boardSquare = board[row][col];
    const {piece, player, moves} = boardSquare
    
    const image = getImageSource(piece, player);
    const htmlSquare = document.querySelector(`#square${row}${col}`);
    htmlSquare.innerHTML = `${image}`;
    htmlSquare.addEventListener("click", function() {
        alert(`${moves}`);
    });
};

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

