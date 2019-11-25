const path = require('path');
const secrets = require('./secrets')

const configuration = {
    migrationsDir: path.resolve(__dirname, 'migrations'),
    host: 'localhost',
    db: 'andin_dev',
    user: 'andin_migrate',
    password: secrets.db_password,
    adapter: 'pg'
};
 
require('sql-migrations').run(configuration);