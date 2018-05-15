"use strict";

const exec = require('child_process').exec;
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
    http.get('http://vmjacobsen39.informatik.tu-muenchen.de/transnet/export_cim', function (res) {
        if (res.statusCode !== 200) {
            destroyScript();
            runScript();
        }

    }).on('error', function (e) {
        console.error(e);
    });
}

function runScript() {
    script = exec('sh run_pgis_gen.sh',
        (error, stdout, stderr) => {
            console.log(`${stdout}`);
            console.log(`${stderr}`);
            if (error !== null) {
                console.log(`exec error: ${error}`);
            }
        });
}
