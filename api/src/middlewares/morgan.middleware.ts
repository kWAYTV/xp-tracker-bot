import {morganStream} from '../utils/logger.util';
import {Application} from 'express';
import morgan from 'morgan';

export default function (serverInstance: Application) {
  serverInstance.use(morgan('combined', {stream: morganStream}));
}
