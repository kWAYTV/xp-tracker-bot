import {Application} from 'express';
import hpp from 'hpp';

export default function (serverInstance: Application) {
  serverInstance.use(hpp());
}
