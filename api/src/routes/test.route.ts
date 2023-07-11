import {Application, Request, Response} from 'express';

export default function (serverInstance: Application) {
  serverInstance.get('/test', async (_: Request, res: Response) => {
    return res.status(200).json({
      success: true,
      message: 'Test route is working!',
    });
  });
}
