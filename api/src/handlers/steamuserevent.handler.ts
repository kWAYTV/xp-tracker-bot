import logger from '../utils/logger.util';
import SteamUser from 'steam-user';
import {join} from 'node:path';

const eventHandlerFile = join(__dirname, '../events/steamuser.event.ts');
const eventHandler = require(eventHandlerFile).default;

export default function registerSteamUserEvents(userInstance: SteamUser) {
  if (typeof eventHandler === 'function') {
    eventHandler(userInstance);
  } else {
    logger.error('Error while registering steamuser events!');
  }
}
