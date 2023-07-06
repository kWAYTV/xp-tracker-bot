const mysql = require('mysql2/promise');
const conOptions = {
    host     : '45.155.36.154',
    port     : '3306',
    user     : 'kwsclub_zaptons',
    password : 'Zaptons123!',
    database : 'kwsclub_auth'
};

const connection = mysql.createPool(conOptions);

module.exports.query = async function(sql, params) {
    const [results,] = await connection.execute(sql, params);
    return results;
};