const mysql = require('mysql2/promise');
const conOptions = {
    host     : '',
    port     : '',
    user     : '',
    password : '',
    database : ''
};

const connection = mysql.createPool(conOptions);

module.exports.query = async function(sql, params) {
    const [results,] = await connection.execute(sql, params);
    return results;
};
