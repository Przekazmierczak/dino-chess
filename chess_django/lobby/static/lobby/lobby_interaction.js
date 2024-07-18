const lobbySocket = new WebSocket(`ws://${window.location.host}/ws/lobby/`);

lobbySocket.onmessage = function(e) {
    const state = JSON.parse(e.data);
    console.log(state)

    const freeGamesContainer = document.getElementById('free-games');
    const games = createTable(state.free_games);
    freeGamesContainer.appendChild(games);
    
};

function createTable(data) {
    const table = document.createElement('table');

    // Loop through each row in the data array
    data.forEach(gameData => {
        const gameRow = document.createElement('tr');

        // gameRow.id = 'game-' + gameData[0];

        gameRow.addEventListener('click', () => {
            window.location.href = `table/${gameData[0]}/`;
        });

        const game_id = document.createElement('tr');
        game_id.innerText = 'Table: ' + gameData[0];
        
        gameRow.appendChild(game_id);
        table.appendChild(gameRow);

        const playersRow = document.createElement('tr');
        
        const white_player = document.createElement('td');
        white_player.innerText = 'White: ' + gameData[1];
        playersRow.appendChild(white_player);
        
        const black_player = document.createElement('td');
        black_player.innerText = 'Black: ' + gameData[2];
        playersRow.appendChild(black_player);

        gameRow.appendChild(playersRow);

        table.appendChild(gameRow);
    });

    return table;
}