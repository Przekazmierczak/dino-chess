document.addEventListener('DOMContentLoaded', function () {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            uploadBoard(row, col);
        }
    }

    const tableID = JSON.parse(document.getElementById('table_id').textContent);
    
    const tableSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/table/'
        + tableID
        + '/'
    );
    
    function uploadBoard(row, column) {
        let image = "";
    
        fetch(`/table/square?row=${row}&column=${column}`)
        .then(response => response.json())
        .then(data => {
            let image = getImageSource(data.piece, data.player);
            let square = document.querySelector(`#square${row}${column}`);
            square.innerHTML = `${image}`;
            square.addEventListener("click", function() {
                alert(`${data.moves}`);
            });
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
});


