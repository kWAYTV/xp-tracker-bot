module.exports = function(req, res, next) {

    // Validate User-Agent
    if (!req.headers['user-agent'].includes('kWS-Auth')) {
        return res.end(JSON.stringify({
            success: false,
            message: 'Request to the api from gs moron!',
        }));
    }

    next();
};