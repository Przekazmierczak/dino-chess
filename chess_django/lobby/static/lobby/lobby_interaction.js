const lobbySocket = new WebSocket(`ws://${window.location.host}/ws/lobby/`);

lobbySocket.onmessage = function(e) {
    const state = JSON.parse(e.data);
    console.log(state)

    const freeGamesContainer = document.getElementById('free-games');
    freeGamesContainer.innerHTML = '';
    const games = createTable(state.free_games);
    freeGamesContainer.appendChild(games);
    
};

function createTable(data) {
    const table = document.createElement('table');
    table.className = 'free-games-table';

    // Loop through each row in the data array
    data.forEach(gameData => {
        const gameRow = document.createElement('tr');
        gameRow.className = 'default-button';

        gameRow.addEventListener('click', () => {
            window.location.href = `table/${gameData[0]}/`;
        });

        const game_id = document.createElement('td');
        game_id.innerText = 'Table: ' + gameData[0];
        gameRow.appendChild(game_id);

        const white_player = document.createElement('td');
        if (gameData[1] !== null) {
            if (gameData[3] !== true) {
                white_player.className = 'player-unready'
            }
        } else {
            gameData[1] = "-"
        }

        white_player.innerText = gameData[1];
        gameRow.appendChild(white_player);
        
        const black_player = document.createElement('td');
        if (gameData[2] !== null) {
            if (gameData[4] !== true) {
                black_player.className = 'player-unready'
            }
        } else {
            gameData[2] = "-"
        }
        black_player.innerText = gameData[2];
        gameRow.appendChild(black_player);

        table.appendChild(gameRow);
    });

    return table;
}