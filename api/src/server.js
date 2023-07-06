const server = require('express')();
const steam_controller = require('./controllers/steam.controller.js');
require('dotenv').config();

// Setup the server
require('./util/setup').setup(server);

module.exports.start = function(port) {
    steam_controller.startCSGO().then(() => {
        server.listen(port, () => {
            console.clear();
            console.log(`Starting server...`)
            console.log(`CSGO Tracker API successfully started on port ${port}.`);
            console.log(`Welcome to CSGO Tracker API!`)
        });
    });
};