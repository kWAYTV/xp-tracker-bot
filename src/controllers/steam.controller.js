const SteamUser = require('steam-user');
const GlobalOffensive = require('globaloffensive');
const medals_controller = require('../controllers/medals.controller.js');
require('dotenv').config();

let user = new SteamUser();
let csgo = new GlobalOffensive(user);

console.log("Logging into Steam")
user.logOn({
    accountName: process.env.STEAM_ACCOUNT_NAME,
    password: process.env.STEAM_PASSWORD,
});

user.on('loggedOn', () => {
    console.log(`Logged into Steam (${user.steamID})`);
    console.log("Starting CS:GO");
    user.gamesPlayed([730]);
});

csgo.on("connectedToGC", () => {
    console.log("GC started");
});

csgo.on("disconnectedFromGC", () => {
    console.log("GC stopped");
});

module.exports.request_player_medals = function(steamID) {
    return new Promise((resolve, reject) => {
        steamID = steamID.replace(/\s/g, '');

        if (!csgo.haveGCSession) {
            console.error("GC not started");
            reject({success: false, error: "GC not started"});
        }

        console.log("Checking ID:", steamID);
        csgo.requestPlayersProfile(steamID, (data, err) => {

            if (err || data === undefined) {
                console.error("Failed to request player profile:", err);
                reject({success: false, error: err});
            }

            let medal_ids = data["medals"]["display_items_defidx"];

            // Map the ids to names and PNG file names
            let medals = medals_controller.get_medal_ids(medal_ids);

            resolve({success: true, steamid64: steamID, medals: medals});

        });
    });
}