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
    console.log(data)

    let medal_ids = data["medals"]["display_items_defidx"];

    // Map the ids to names and PNG file names
    let medals = medals_controller.get_medal_ids(medal_ids);

    return res.status(200).json({
        steamid64: steamID,
        medals: medals,
    });

});

module.exports = router;