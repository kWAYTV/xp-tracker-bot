import express, {Application} from 'express';
import {join} from 'node:path';

export default function (serverInstance: Application) {
  serverInstance.use(
    '/public',
    express.static(join(__dirname, '../www/public/'))
  );
}
