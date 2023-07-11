import authUA from '../middlewares/non/useragent.middleware';
import {Application, Request, Response} from 'express';

// This route is only to test the functionality of the user-agent middleware
export default function (serverInstance: Application) {
  serverInstance.get('/ua', authUA, async (_: Request, res: Response) => {
    return res.status(200).json({
      success: true,
      message: 'Request comes from GS',
    });
  });
}
