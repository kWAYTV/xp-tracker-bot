const router = require('express').Router();
const medals_controller = require('../controllers/medals.controller.js');
const steam_controller = require('../controllers/steam.controller.js');

// Medals route
router.get('/medals', async function(req, res) {
    const steamID = req.query.id
    const queue_id = req.query.queue_id

    // Check if steamID is provided
    if (!steamID || !queue_id) {
        return res.status(400).json({
            success: false,
            message: 'Missing parameters (steamID or queue_id)'
        });
    }

    console.log("Requested ID:", steamID, "Queue ID:", queue_id);

    let medal_data = await steam_controller.request_player_medals(steamID, queue_id);
    let player_data = await steam_controller.request_player_data(steamID);

    return res.status(200).json({
        success: true,
        steamID: steamID,
        response: {
            player_data: player_data,
            medal_data: medal_data
        }
    });

});

// Level route
router.get('/level', async function(req, res) {
    const steamid64 = req.query.id

    // Check if steamID is provided
    if (!steamid64) {
        return res.status(400).json({
            success: false,
            message: 'Missing parameters (steamID)'
        });
    }

    console.log("Requested ID:", steamid64);

    let level_data = await steam_controller.request_player_level(steamid64);

    return res.status(200).json({
        success: true,
        steamID: steamid64,
        response: level_data
    });
});

module.exports = router;