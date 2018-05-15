'use strict';

const spawn = require('child_process').spawn;

const interval = setInterval(checkDate, 60000);

function checkDate() {
    const currentDate = new Date();
    if (currentDate.getDay() === 2 && currentDate.getHours() === 16 && currentDate.getMinutes() === 49) {
        console.log('Started Importing Transnet Data!');
        console.log(currentDate);
        runScript();
    }
}

function runScript() {
    const script = spawn('bash', [__dirname + '/run_import_transnet.sh']);
    script.on('exit', () => {
        console.log('process exit');
    });
    script.stdout.pipe(process.stdout);
    script.stderr.pipe(process.stderr);
}

