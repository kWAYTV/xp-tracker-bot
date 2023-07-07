const SteamAPI = require('steamapi');
require('dotenv').config();
const steam = new SteamAPI(process.env.STEAM_API_KEY);

module.exports.convert = async function(steamID) {
    // Check if id is /profiles or /id or just a custom id
    const permaReg = /^(((http|https):\/\/(www\.)?)?steamcommunity.com\/profiles\/([0-9]{17}))|([0-9]{17})$/;
    const customReg = /^(((http|https):\/\/(www\.)?)?steamcommunity.com\/id\/)?[a-zA-Z0-9-._]+/;
    
    // Check if id is valid
    const isProfile = permaReg.test(steamID);
    const isCustom = customReg.test(steamID);
    
    // If not valid, return error
    if (!isProfile && !isCustom){
        return {
            success: false,
            message: 'The id you are trying to check is not a valid format.'
        };
    }

    // If it's a custom ID without the full URL, add the URL part
    if(isCustom && !isProfile){
        if(!steamID.includes('steamcommunity.com')){
            steamID = `https://steamcommunity.com/id/${steamID}`;
        }
    }

    // Resolve the id
    try {
        const id = await steam.resolve(steamID);
        const summary = await steam.getUserSummary(id);
        return {
            success: true,
            message: 'Successfully retrieved data!',
            data: {
                id: id,
                name: summary.nickname,
                avatar: summary.avatar.large
            }
        };
    } catch(err) {
        return {success: false, message: 'Failed to retrieve data!', error: err};
    }
}