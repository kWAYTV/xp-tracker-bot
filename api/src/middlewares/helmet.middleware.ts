import {Application} from 'express';
import helmet from 'helmet';

export default function (serverInstance: Application) {
  serverInstance.use(helmet());
}
