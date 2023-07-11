import {Application, Request, Response} from 'express';

export default function (serverInstance: Application) {
  serverInstance.get('/', async (_: Request, res: Response) => {
    return res.status(200).json({
      success: true,
      message: 'Welcome to kwayservices - CSGO Tracking API',
    });
  });
}
