const lobbySocket = new WebSocket(`ws://${window.location.host}/ws/lobby/`);

lobbySocket.onmessage = function(e) {
    const state = JSON.parse(e.data);
    console.log(state)
};