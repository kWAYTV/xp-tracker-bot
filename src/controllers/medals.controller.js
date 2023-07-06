const fs = require('fs');

// Read medal ids file and create an object mapping ids to names
const medalData = fs.readFileSync( "../medals/ids.txt", 'utf8');
const medalIdsToNames = {};
medalData.split('\n').forEach(line => {
    const [id, name] = line.split(';');
    medalIdsToNames[id] = name;
});

module.exports.get_medal_ids = function(medal_ids) {

    // Map the ids to names and PNG file names
    let medals = medal_ids.map(id => ({
        medal_id: id,
        medal_name: medalIdsToNames[id],
        medal_file: `${id}.png`,
    }));
    return medals;

}