import {Application, Request, Response} from 'express';

export default function (serverInstance: Application) {
  serverInstance.get('*', async (_: Request, res: Response) => {
    return res.status(404).json({
      success: false,
      message: 'The requested resource was not found!',
    });
  });
}
