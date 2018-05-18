"use strict";

const spawn = require('child_process').spawn;
const http = require('http');

let script = null;

const interval = setInterval(checkDate, 60000);

process.on('exit', function () {
    destroyScript();
});

function destroyScript() {
    try {
        if (script !== null && typeof script !== "undefined" && script.hasOwnProperty('kill')) {
            script.kill();
        }
    }
    catch (err) {
        console.error(err);
    }
}

function checkDate() {
    try {
        const currentDate = new Date();
        if (currentDate.getMinutes() === 40) {
            destroyScript();
            runScript();
        }
    }
    catch (err) {
        console.error(err);
        destroyScript();
        runScript();
    }
}

function runScript() {
    try {
        script = spawn('bash', [__dirname + '/rerun_nginx.sh']);
        script.on('exit', () => {
            console.log('process exit');
        });
        script.stdout.pipe(process.stdout);
        script.stderr.pipe(process.stderr);
    }
    catch (err) {
        console.error(err);
    }
}
