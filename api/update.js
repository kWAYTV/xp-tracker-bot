const {execSync} = require('node:child_process');
const {exit} = require('node:process');

function updateApp() {
  try {
    console.log('Update process started! Fetching latest updates from GitHub!');

    // Pull latest changes from remote repository
    execSync('git pull');
    console.log('Latest updates pulled!');

    // Install or update dependencies if needed
    execSync('npm i');
    console.log('Updating dependencies!');

    console.log('Application successfully updated!');
  } catch (error) {
    console.log(`Error while updating application! ${error}`);
    exit(0);
  }
}

updateApp();
