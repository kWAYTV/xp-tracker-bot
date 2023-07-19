import GlobalOffensive from 'globaloffensive';
import logger from '../utils/logger.util';
import {join} from 'node:path';

const eventHandlerFile = join(__dirname, '../events/csgo.event.ts');
const eventHandler = require(eventHandlerFile).default;

export default function registerCsgoEvents(csgoInstance: GlobalOffensive) {
  if (typeof eventHandler === 'function') {
    eventHandler(csgoInstance);
  } else {
    logger.error('Error while registering csgo events!');
  }
}
