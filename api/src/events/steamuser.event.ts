import {startGC} from '../controllers/steam.controller';
import logger from '../utils/logger.util';
import SteamUser from 'steam-user';

export default function (userInstance: SteamUser) {
  userInstance.on('loggedOn', () => {
    logger.info(`Logged into Steam (${userInstance.steamID})`);
    startGC(userInstance);
  });
}
