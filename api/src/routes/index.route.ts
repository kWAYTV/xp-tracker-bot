import {Application, Request, Response} from 'express';
import renderPage from '../helpers/view.helper';

export default function (serverInstance: Application) {
  serverInstance.get('/', async (_: Request, res: Response) => {
    return renderPage(res, 'index', {title: 'kWAY - CSGO Tracking API'});
  });
}
