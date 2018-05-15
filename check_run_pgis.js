"use strict";

const spawn = require('child_process').spawn;
const http = require('http');

let script = null;

const interval = setInterval(checkLive, 60000);

process.on('exit', function () {
    destroyScript();
});

function destroyScript() {
    if (script !== null && typeof script !== "undefined" && script.hasOwnProperty('kill')) {
        script.kill();
    }
}

function checkLive() {
    http.get('http://vmjacobsen39.informatik.tu-muenchen.de/', function (res) {
        if (res.statusCode !== 200) {
            destroyScript();
            runScript();
        }

    }).on('error', function (e) {
        console.error(e);
    });
}

function runScript() {
    script = spawn('bash', [__dirname + '/run_pgis.sh']);
    script.on('exit', () => {
        console.log('process exit');
    });
    script.stdout.pipe(process.stdout);
    script.stderr.pipe(process.stderr);
}
