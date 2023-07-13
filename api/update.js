const {execSync} = require('node:child_process');
const {exit} = require('node:process');

function updateApp() {
  try {
    // Pull latest changes from remote repository
    execSync('git pull');

    // Install or update dependencies if needed
    execSync('npm i');

    console.log('Application successfully updated!');
  } catch (error) {
    console.log(`Error while updating application! ${error}`);
    exit(0);
  }
}

updateApp();
