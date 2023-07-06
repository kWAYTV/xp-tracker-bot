const router = require('express').Router();
const sid = require('../util/sid');

router.get('/get', async function(req, res) {
    const steamID = req.query.id

    // Check if steamID is provided
    if (!steamID) {
        return res.status(400).json({
            success: false,
            message: 'Missing parameters (id)!'
        });
    }

    const data = await sid.convert(steamID);

    if (data.success) {
        return res.status(200).json(data);
    } else {
        return res.status(500).json(data);
    }
    
});

module.exports = router;