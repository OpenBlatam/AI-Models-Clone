/**
 * TruthGPT Runner Wrapper
 * Bridges npm/yarn start commands to the native OS launch process.
 */

const { spawn } = require('child_process');
const os = require('os');
const path = require('path');

const LOG_PREFIX = '\x1b[35m[Frontier]\x1b[0m'; // Magenta
const IS_WINDOWS = os.platform() === 'win32';
const PROJECT_ROOT = path.resolve(__dirname, '..');

console.log(`${LOG_PREFIX} Starting application...`);

let child;

if (IS_WINDOWS) {
    // On Windows, use the batch file which handles venv activation
    const runScript = path.join(PROJECT_ROOT, 'run.bat');
    child = spawn('cmd.exe', ['/c', runScript], { stdio: 'inherit' });
} else {
    // On Unix, manually activate venv and run the cli
    // standard venv path
    const venvActivate = path.join(PROJECT_ROOT, '.venv', 'bin', 'activate');
    // Using a login shell or just bash -c to source and run
    // We assume 'frontier' entry point is available after activation
    // If 'frontier' is not in path yet, we might need to use python -m optimization_core.cli
    const command = `source "${venvActivate}" && frontier --help`;

    child = spawn('bash', ['-c', command], { stdio: 'inherit' });
}

child.on('error', (err) => {
    console.error(`${LOG_PREFIX} \x1b[31mFailed to launch application:\x1b[0m`, err);
    process.exit(1);
});

child.on('close', (code) => {
    if (code !== 0) {
        console.error(`${LOG_PREFIX} \x1b[31mProcess exited with code ${code}.\x1b[0m`);
        process.exit(code);
    }
});
