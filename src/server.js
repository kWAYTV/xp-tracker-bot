const server = require('express')();
require('dotenv').config();

// Setup the server
require('./util/setup').setup(server);

module.exports.start = function(port) {

    server.listen(port, () => {
        console.clear();
        console.log(`Starting server...`)
        console.log(`CSGO Tracker API successfully started on port ${port}.`);
        console.log(`Welcome to CSGO Tracker API!`)
    });

};