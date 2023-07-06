const router = require('express').Router();
const medals_controller = require('../controllers/medals.controller.js');
const steam_controller = require('../controllers/steam.controller.js');

// POST Init
router.get('/getmedals', async function(req, res) {
    const steamID = req.query.id

    // Check if steamID is provided
    if (!steamID) {
        return res.status(400).json({
            success: false,
            message: 'Missing parameters (id)!'
        });
    }

    let data = await steam_controller.request_player_medals(steamID);
    
    if (!data.success) {
        return res.status(400).json(data);
    }

    return res.status(200).json(data);

});

module.exports = router;