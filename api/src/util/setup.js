module.exports.setup = function(server) {

    // Routes
    server.use('/', require('../routes/index.route'));
    server.use('/sid', require('../routes/sid.route'));
    server.use('/steam', require('../routes/steam.route'));
    server.use('*', (req, res) => {
        res.status(404).json({
            success: false,
            message: 'Route not found!'
        });
    });
    

};