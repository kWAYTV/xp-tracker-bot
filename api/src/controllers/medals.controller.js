const fs = require('fs');
const path = require('path');

// Read medal ids file and create an object mapping ids to names
const medalDataPath = path.join(__dirname, '..', 'medals', 'ids.txt');
const medalData = fs.readFileSync(medalDataPath, 'utf8');
const medalIdsToNames = {};
medalData.split('\n').forEach(line => {
    const [id, name] = line.split(';');
    medalIdsToNames[id] = name;
});

module.exports.get_medals = function(medal_ids) {

    // Map the ids to names and PNG file names
    let medals = medal_ids.map(id => ({
        medal_id: id,
        medal_name: medalIdsToNames[id],
    }));
    return medals;

}