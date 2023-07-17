import authUA from '../middlewares/non/useragent.middleware';
import {
  requestPlayerMedals,
  requestPlayerLevel,
  requestPlayerData,
} from '../controllers/steam.controller';
import {Application, Request, Response} from 'express';
import getSteam64 from '../utils/steam.util';
import logger from '../utils/logger.util';

export default function (serverInstance: Application) {
  serverInstance.get(
    '/steam/get/steamid',
    // authUA,
    async (req: Request, res: Response) => {
      const idToResolve = req.query.id?.toString();

      if (!idToResolve) {
        return res
          .status(400)
          .json({success: false, message: 'Missing parameters (id)'});
      }

      const data = await getSteam64(idToResolve);
      if (data.success) {
        return res.status(200).json({success: true, data: data.data});
      } else {
        return res.status(500).json({success: false, data: data.data});
      }
    }
  );

  serverInstance.get(
    '/steam/get/medals',
    // authUA,
    async (req: Request, res: Response) => {
      const idToResolve = req.query.id?.toString();
      const queueId = req.query.queueid?.toString();

      if (!idToResolve || !queueId) {
        return res.status(400).json({
          success: false,
          message: 'Missing parameters (id or queueid)',
        });
      }

      logger.info(
        `MEDAL REQUEST: Requested id '${idToResolve}' with queue id '${queueId}'`
      );

      const medalData = await requestPlayerMedals(idToResolve, queueId);
      const playerData = await requestPlayerData(idToResolve);

      return res.status(200).json({
        success: true,
        steamId: idToResolve,
        data: {
          playerData: playerData,
          medalData: medalData,
        },
      });
    }
  );

  serverInstance.get(
    '/steam/get/levels',
    // authUA,
    async (req: Request, res: Response) => {
      const idToResolve = req.query.id?.toString();

      if (!idToResolve) {
        return res.status(400).json({
          success: false,
          message: 'Missing parameters (id)',
        });
      }

      logger.info(`LEVEL REQUEST: Requested id: ${idToResolve}`);

      const levelData = await requestPlayerLevel(idToResolve);

      return res
        .status(200)
        .json({success: true, steam64Id: idToResolve, data: levelData});
    }
  );
}
