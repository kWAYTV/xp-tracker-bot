import nedb from '@seald-io/nedb';
import {join} from 'node:path';

const db = new nedb({
  filename: join(__dirname, '../database/store/tokens.db'),
  autoload: true,
});

export default db;
