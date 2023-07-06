require('dotenv').config();
const SteamUser = require('steam-user');
const GlobalOffensive = require('globaloffensive');
const medals_controller = require('../controllers/medals.controller.js');

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

module.exports.request_player_profile = async function(steamID) {

    if (!csgo.haveGCSession) {
        console.error("GC not started");
        return {success: false, error: "GC not started"};
    } else {
        console.log("GC started, proceeding");
    }

    console.log("Checking ID:", steamID);
    csgo.requestPlayersProfile(steamID, (data, err) => {

        if (err) {
            console.error("Failed to request player profile:", err);
            return {success: false, error: err};
        }

        let medal_ids = data["medals"]["display_items_defidx"];

        // Map the ids to names and PNG file names
        let medals = medals_controller.get_medal_ids(medal_ids);

        return {success: true, steamid64: steamID, medals: medals};

    });
}