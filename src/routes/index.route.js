const router = require('express').Router();
module.exports = router;

// GET index
router.get('/', function(req, res) {

    res.end(JSON.stringify({
        success: true,
        message: 'Welcome to kwayservices csgo tracking api!',
    }));

});