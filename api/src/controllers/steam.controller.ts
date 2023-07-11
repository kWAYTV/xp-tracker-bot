import {getRandomProxy} from '../utils/proxy.util';
import getMedals from '../helpers/medals.helper';
import GlobalOffensive from 'globaloffensive';
import {create} from '../utils/canvas.util';
import logger from '../utils/logger.util';
import SteamUser from 'steam-user';
import axios from 'axios';
import 'dotenv/config';

const user = new SteamUser();
const csgo = new GlobalOffensive(user);

// CS:GO Events
// !TODO - Move to 'events' folder
csgo.on('disconnectedFromGC', () => {
  logger.info('CS:GO GameCoordinator stopped!');
});

csgo.on('connectedToGC', () => {
  logger.info('Connected to CS:GO GameCoordinator!');
});

/**
 * Starts the CS:GO game coordinator (GC) and initiates the connection.
 *
 * @description This function starts the CS:GO game coordinator (GC) and establishes a connection to it.
 * It also logs a message when the connection to the GC is successful.
 *
 * @example
 * // Example usage:
 * startGC();
 */
function startGC(): void {
  logger.info('Starting CS:GO');
  user.gamesPlayed([730]);
}

/**
 * Starts the CS:GO game and establishes a connection to the game coordinator (GC) after logging into Steam.
 *
 * @description This function initiates the CS:GO game by logging into Steam using the provided account credentials.
 * Once logged in, it logs a message indicating the successful login and then proceeds to start the CS:GO game coordinator (GC).
 * The function returns a Promise that resolves once the login and GC connection are complete.
 *
 * @returns {Promise<void>} A Promise that resolves once the login and GC connection are complete.
 *
 * @example
 * // Example usage:
 * startCSGO().then(() => {
 *   logger.info('CS:GO started and connected to GC');
 * });
 */
export function startCSGO(): Promise<void> {
  return new Promise<void>(resolve => {
    logger.info('Logging into Steam');
    const randomProxy = getRandomProxy();
    logger.info(`Using proxy: ${randomProxy}`);
    user.setOption('httpProxy', randomProxy);
    user.logOn({
      accountName: process.env.STEAM_USERNAME!,
      password: process.env.STEAM_PASSWORD!,
      rememberPassword: true,
      autoRelogin: true,
    });
    user.on('loggedOn', () => {
      logger.info(`Logged into Steam (${user.steamID})`);
      startGC();
      resolve();
    });
  });
}

/**
 * Requests player data from the Steam API based on the provided SteamID.
 *
 * @param {string} steamID - The SteamID of the player.
 * @returns {Promise<{success: boolean, error?: any, data?: any}>} A Promise that resolves with an object containing the result of the player data request.
 *
 * @description This function makes a request to the Steam API to fetch player data for the specified SteamID. It retrieves the player's name, avatar URL, and profile URL.
 * The function returns a Promise that resolves with an object containing the success status, along with the fetched player data if successful, or an error object if the request fails.
 *
 * @example
 * // Example usage:
 * requestPlayerData('1234567890').then((response) => {
 *   if (response.success) {
 *     logger.info('Player data:', response.data);
 *   } else {
 *     logger.error('Failed to fetch player data:', response.error);
 *   }
 * });
 */
export async function requestPlayerData(
  steamID: string
): Promise<{success: boolean; error?: any; data?: any}> {
  try {
    steamID = steamID.replace(/\s/g, '');

    const url = `https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=${process.env.STEAM_API_KEY}&steamids=${steamID}`;
    const fetchResponse = await axios.get(url);
    const fetchedData = fetchResponse.data;

    const playerInfo = fetchedData.response?.players[0];
    const playerName = playerInfo?.personaname;
    const playerAvatar = playerInfo?.avatarfull;
    const profileUrl = playerInfo?.profileurl;
    const countryCode = playerInfo?.loccountrycode;

    const json: {
      name: string | undefined;
      avatar: string | undefined;
      profile_url: string | undefined;
      country_code?: string;
    } = {
      name: playerName,
      avatar: playerAvatar,
      profile_url: profileUrl,
    };

    if (countryCode) {
      json.country_code = countryCode;
    }

    return {success: true, data: json};
  } catch (error) {
    logger.error(`Failed to get player info: ${error}`);
    return {success: false, error};
  }
}

/**
 * Requests player medal data for a specific SteamID and queue ID.
 *
 * @param {string} steamId - The SteamID of the player.
 * @param {string} queueId - The ID of the queue.
 * @returns {Promise<{success: boolean, error?: any, data?: any}>} A Promise that resolves with an object containing the result of the player medal data request.
 *
 * @description This function requests medal data for a player based on their SteamID and the specified queue ID.
 * It retrieves information such as commendations, CS:GO level, current XP, current level percentage, remaining XP, Steam level, and medal data.
 * The function returns a Promise that resolves with an object containing the success status, along with the fetched medal data if successful, or an error object if the request fails.
 *
 * @example
 * // Example usage:
 * requestPlayerMedals('1234567890', 'queue123').then((response) => {
 *   if (response.success) {
 *     logger.info('Player medal data:', response.data);
 *   } else {
 *     logger.error('Failed to fetch player medal data:', response.error);
 *   }
 * });
 *
 * // Output (if successful):
 * // Player medal data: {
 * //   steam_level: 50,
 * //   csgo_level: 10,
 * //   level_percentage: '23.56%',
 * //   remaining_xp: 4979,
 * //   commends: {
 * //     friendly: 100,
 * //     teacher: 200,
 * //     leader: 150
 * //   },
 * //   medals: {
 * //     medal1: {
 * //       name: 'Medal 1',
 * //       image: 'http://medal1-image-url.com',
 * //       description: 'Medal 1 description'
 * //     },
 * //     medal2: {
 * //       name: 'Medal 2',
 * //       image: 'http://medal2-image-url.com',
 * //       description: 'Medal 2 description'
 * //     },
 * //     ...
 * //   }
 * // }
 *
 * // Output (if unsuccessful):
 * // Failed to fetch player medal data: { ...error object... }
 */
export async function requestPlayerMedals(
  steamId: string,
  queueId: string
): Promise<{success: boolean; error?: any; data?: any}> {
  try {
    steamId = steamId.replace(/\s/g, '');

    if (!csgo.haveGCSession) {
      logger.error('GC not started');
      return {success: false, error: 'GC not started'};
    }

    logger.info(`Checking ID: ${steamId} - Queue ID: ${queueId}`);
    const data = await new Promise<GlobalOffensive.Profile>(resolve => {
      csgo.requestPlayersProfile(steamId, profile => {
        resolve(profile);
      });
    });

    const cmdFriendly = data?.commendation?.cmd_friendly;
    const cmdTeaching = data?.commendation?.cmd_teaching;
    const cmdLeader = data?.commendation?.cmd_leader;
    const csgoLevel = data?.player_level;
    const currentXP = data?.player_cur_xp;
    const currentLevel = ((currentXP - 327680000) % 5000) + 1;
    const currentLevelPercentage = ((currentLevel / 5000) * 100).toFixed(2);
    const remainingXP = 5000 - currentLevel - 10;

    const steamLevel = await new Promise<number>((resolve, reject) => {
      user.getSteamLevels([steamId], (err, users) => {
        if (err) {
          logger.error(`Failed to request player steam level: ${err}`);
          reject(err);
        }
        resolve(users[steamId]);
      });
    });

    const medalIds = data?.medals?.display_items_defidx;

    const json = {
      steam_level: steamLevel,
      csgo_level: csgoLevel,
      level_percentage: `${currentLevelPercentage}%`,
      remaining_xp: remainingXP,
      commends: {
        friendly: cmdFriendly,
        teacher: cmdTeaching,
        leader: cmdLeader,
      },
      medals: {},
    };

    if (medalIds) {
      const medals = getMedals(medalIds);
      await create(medals, queueId);
      json.medals = medals;
    } else {
      logger.error('Failed to get medal data');
    }

    return {success: true, data: json};
  } catch (error) {
    logger.error(`Failed to request player medals: ${error}`);
    return {success: false, error};
  }
}

/**
 * Requests the CS:GO level and experience points (XP) for a player based on their SteamID.
 *
 * @param {string} steamID - The SteamID of the player.
 * @returns {Promise<{success: boolean, error?: any, data?: any}>} A Promise that resolves with an object containing the result of the player level request.
 *
 * @description This function requests the CS:GO level and experience points (XP) for a player based on their SteamID.
 * It retrieves the current CS:GO level, current XP, current level percentage, and remaining XP to the next level.
 * The function returns a Promise that resolves with an object containing the success status, along with the fetched player level data if successful, or an error object if the request fails.
 *
 * @example
 * // Example usage:
 * requestPlayerLevel('1234567890').then((response) => {
 *   if (response.success) {
 *     logger.info('Player level data:', response.data);
 *   } else {
 *     logger.error('Failed to fetch player level data:', response.error);
 *   }
 * });
 *
 * // Output (if successful):
 * // Player level data: {
 * //   current_level: 10,
 * //   current_xp: 350000,
 * //   level_percentage: '23.56%',
 * //   remaining_xp: 4700
 * // }
 *
 * // Output (if unsuccessful):
 * // Failed to fetch player level data: { ...error object... }
 */
export async function requestPlayerLevel(
  steamID: string
): Promise<{success: boolean; error?: any; data?: any}> {
  try {
    steamID = steamID.replace(/\s/g, '');

    if (!csgo.haveGCSession) {
      logger.error('GC not started');
      return {success: false, error: 'GC not started'};
    }

    logger.info(`Checking ID: ${steamID}`);
    const data: GlobalOffensive.Profile = await new Promise(resolve => {
      csgo.requestPlayersProfile(steamID, profile => {
        resolve(profile);
      });
    });

    const csgoLevel = data?.player_level;
    const currentXP = data?.player_cur_xp;
    const currentLevel = ((currentXP - 327680000) % 5000) + 1;
    const currentLevelPercentage = ((currentLevel / 5000) * 100).toFixed(2);
    const remainingXP = 5000 - currentLevel - 10;

    const json = {
      current_level: csgoLevel,
      current_xp: currentLevel,
      level_percentage: `${currentLevelPercentage}%`,
      remaining_xp: remainingXP,
    };

    return {success: true, data: json};
  } catch (error) {
    logger.error(`Failed to request player level: ${error}`);
    return {success: false, error};
  }
}
