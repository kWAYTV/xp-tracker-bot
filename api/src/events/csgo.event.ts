import GlobalOffensive from 'globaloffensive';
import logger from '../utils/logger.util';

export default function (csgoInstance: GlobalOffensive) {
  csgoInstance.on('connectedToGC', () => {
    logger.info('Connected to CS:GO GameCoordinator!');
  });

  csgoInstance.on('disconnectedFromGC', () => {
    logger.info('Disconnected from CS:GO GameCoordinator!');
  });
}
