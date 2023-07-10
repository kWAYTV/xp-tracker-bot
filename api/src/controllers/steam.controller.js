const fs = require('fs');
const SteamUser = require('steam-user');
const GlobalOffensive = require('globaloffensive');
const medals_controller = require('../controllers/medals.controller.js');
const canvas_creator = require('../util/canvas.js');
const request = require('request-promise');
require('dotenv').config();

let user = new SteamUser();
let csgo = new GlobalOffensive(user);

function start_gc() {
    csgo.on("connectedToGC", () => {
        console.log("GC started");
    });
    console.log("Starting CS:GO");
    user.gamesPlayed([730]);
}

// Make a function to get a random proxy from /src/data/proxies.txt
function get_random_proxy() {
    let proxies = fs.readFileSync('./src/data/proxies.txt').toString().split("\n");
    let random_proxy = proxies[Math.floor(Math.random() * proxies.length)];
    console.log("Using proxy:", random_proxy)
    return random_proxy;
}

module.exports.startCSGO = function() {
    return new Promise(resolve => {
        console.log("Logging into Steam");
        user.logOn({
            accountName: process.env.STEAM_ACCOUNT_NAME,
            password: process.env.STEAM_PASSWORD,
            rememberPassword: true,
            autoRelogin: true,
            httpProxy: get_random_proxy(),
        });
        user.on('loggedOn', () => {
            console.log(`Logged into Steam (${user.steamID})`);
            start_gc();
            resolve();
        });
    });
}

csgo.on("disconnectedFromGC", () => {
    console.log("GC stopped");
});

module.exports.request_player_data = function (steamID) {
    return new Promise((resolve, reject) => {
        steamID = steamID.replace(/\s/g, '');

        let url = `https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=${process.env.STEAM_API_KEY}&steamids=${steamID}`
        request.get(url, (err, res, body) => {
            if (err) {
                console.error("Failed to get player info:", err);
                return reject({ success: false, error: err });
            }

            let data = JSON.parse(body);
            let player_info = data && data["response"]["players"][0];
            let player_name = player_info && player_info["personaname"];
            let player_avatar = player_info && player_info["avatarfull"];
            let profile_url = player_info && player_info["profileurl"];
            let country_code = player_info && player_info["loccountrycode"];

            let json = {
                name: player_name,
                avatar: player_avatar,
                profile_url: profile_url,
                country_code: country_code
            }

            return resolve(json);
        });
    })
    .catch(err => (reject({ success: false, error: err })));
}

module.exports.request_player_medals = function (steamID, queue_id) {
    return new Promise(async (resolve, reject) => {
        steamID = steamID.replace(/\s/g, '');

        if (!csgo.haveGCSession) {
            console.error("GC not started");
            return reject({ success: false, error: "GC not started" });
        }

        console.log("Checking ID:", steamID, "Queue ID:", queue_id);
        csgo.requestPlayersProfile(steamID, async (data, err) => {
            if (err) {
                console.error("Failed to request player profile:", err);
                return reject({ success: false, error: err });
            }

            let cmd_friendly = data && data["commendation"] && data["commendation"]["cmd_friendly"];
            let cmd_teaching = data && data["commendation"] && data["commendation"]["cmd_teaching"];
            let cmd_leader = data && data["commendation"] && data["commendation"]["cmd_leader"];
            let csgo_level = data && data["player_level"];
            let current_xp = data && data["player_cur_xp"];
            let currentLevel = (current_xp - 327680000) % 5000;
            let currentLevelPercentage = (currentLevel / 5000) * 100;
            let remaining_xp = 5000 - currentLevel - 10;

            try {
                let steam_level = await new Promise((resolve, reject) => {
                    user.getSteamLevels([steamID], (err, users) => {
                        if (err) {
                            console.error("Failed to request player steam level:", err);
                            reject(err);
                        }
                        resolve(users[steamID]);
                    });
                });

                let medal_ids = data && data["medals"] && data["medals"]["display_items_defidx"];

                let json = {
                    steam_level: steam_level,
                    csgo_level: csgo_level,
                    level_percentage: `${currentLevelPercentage.toFixed(2)}%`,
                    remaining_xp: remaining_xp,
                    commends: {
                        friendly: cmd_friendly,
                        teacher: cmd_teaching,
                        leader: cmd_leader
                    }
                };
                
                if (medal_ids) {
                    // Map the ids to names and PNG file names
                    let medals = medals_controller.get_medals(medal_ids);
                    canvas_creator.create(medals, queue_id);
                    json.medals = medals; // add medals to the json object
                } else {
                    console.error("Failed to get medal data");
                }
                
                resolve(json);         
            } catch (err) {
                console.error("Failed to request player steam level:", err);
                reject({ success: false, error: err });
            }
        });
    })
    .catch(err => ({ success: false, error: err }));
}

// Make the same function as above but only returning steamID, csgo_level and current xp    
module.exports.request_player_level = function (steamID) {
    return new Promise(async (resolve, reject) => {
        steamID = steamID.replace(/\s/g, '');

        if (!csgo.haveGCSession) {
            console.error("GC not started");
            return reject({ success: false, error: "GC not started" });
        }

        console.log("Checking ID:", steamID);
        csgo.requestPlayersProfile(steamID, async (data, err) => {
            if (err) {
                console.error("Failed to request player profile:", err);
                return reject({ success: false, error: err });
            }

            let csgo_level = data && data["player_level"];
            let current_xp = data && data["player_cur_xp"];
            let currentLevel = (current_xp - 327680000) % 5000;
            let currentLevelPercentage = (currentLevel / 5000) * 100;
            let remaining_xp = 5000 - currentLevel - 10;

            try {

                let json = {
                    current_level: csgo_level,
                    current_xp: current_xp,
                    level_percentage: `${currentLevelPercentage.toFixed(2)}%`,
                    remaining_xp: remaining_xp,
                };
                
                resolve(json);         
            } catch (err) {
                console.error("Failed to request player steam level:", err);
                reject({ success: false, error: err });
            }
        });
    })
    .catch(err => ({ success: false, error: err }));
}