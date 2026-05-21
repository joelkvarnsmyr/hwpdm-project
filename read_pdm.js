#!/usr/bin/env node
'use strict';

// Read data from Hardwire Electronics PDM25 V2 via USB serial
// Protocol: $,<cmd>,<params>,#\n  @ 9600 baud

const { SerialPort } = require('serialport');
const { DelimiterParser } = require('@serialport/parser-delimiter');

const COM_PORT = 'COM4';
const BAUD = 9600;

let port, parser;
let allResponses = [];
let deviceInfo = null;
let statisticsData = null;
let variableData = [];
let configBlocks = [];
let logEntries = [];

function send(cmd) {
  const msg = cmd.endsWith('\n') ? cmd : cmd + '\n';
  console.log(`  TX: ${msg.trim()}`);
  port.write(msg);
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function parseDeviceInfo(parts) {
  // $,8,ModelVersion,FirmwareVersion,DeviceID,PasswordEnabled,PasswordHash,#
  return {
    modelVersion: parseInt(parts[2]),
    firmwareVersion: parts[3],
    deviceID: parts[4],
    passwordEnabled: parseInt(parts[5]),
    passwordHash: parts[6],
    modelName: getModelName(parseInt(parts[2]))
  };
}

function getModelName(v) {
  if (v <= 9) return 'PDM10';
  if (v <= 19) return 'PDM15 V2';
  if (v <= 29) return 'PDM25 V2';
  if (v <= 39) return 'PDM35';
  if (v <= 79 && v >= 70) return 'PDM28';
  return `Unknown (${v})`;
}

async function main() {
  console.log(`\n=== HARDWIRE PDM25 V2 — DATA READOUT ===`);
  console.log(`Port: ${COM_PORT} @ ${BAUD} baud\n`);

  port = new SerialPort({ path: COM_PORT, baudRate: BAUD, autoOpen: false });
  parser = port.pipe(new DelimiterParser({ delimiter: '\n' }));

  // Collect all incoming data
  parser.on('data', (data) => {
    const line = data.toString().trim();
    if (!line) return;
    allResponses.push({ time: new Date().toISOString(), raw: line });

    const parts = line.split(',');
    const cmd = parts[1];

    switch (cmd) {
      case '8':
        deviceInfo = parseDeviceInfo(parts);
        console.log(`\n--- DEVICE INFO (cmd 8) ---`);
        console.log(`  Model: ${deviceInfo.modelName} (version ${deviceInfo.modelVersion})`);
        console.log(`  Firmware: ${deviceInfo.firmwareVersion}`);
        console.log(`  Device ID: ${deviceInfo.deviceID}`);
        console.log(`  Password: ${deviceInfo.passwordEnabled ? 'ENABLED' : 'disabled'}`);
        break;

      case '5':
        console.log(`\n--- STATISTICS (cmd 5) ---`);
        console.log(`  Raw: ${line}`);
        statisticsData = parts;
        break;

      case '9':
        // Variable data response — parse key values
        variableData.push(parts);
        break;

      case '7':
        // Config data block
        configBlocks.push(line);
        break;

      case '10':
        // Log data
        console.log(`\n--- LOG DATA (cmd 10) ---`);
        console.log(`  Raw: ${line}`);
        logEntries.push(line);
        break;

      case '20':
        console.log(`\n--- FLASH FORMAT STATUS (cmd 20) ---`);
        console.log(`  Raw: ${line}`);
        break;

      case '21':
        console.log(`\n--- LOG INFO (cmd 21) ---`);
        console.log(`  Raw: ${line}`);
        break;

      case '22':
        console.log(`\n--- LOG DATA BLOCK (cmd 22) ---`);
        console.log(`  Raw: ${line.substring(0, 200)}${line.length > 200 ? '...' : ''}`);
        logEntries.push(line);
        break;

      case '23':
        console.log(`\n--- FLASH DUMP (cmd 23) ---`);
        console.log(`  Raw: ${line.substring(0, 200)}${line.length > 200 ? '...' : ''}`);
        break;

      case '16':
        console.log(`\n--- CONFIG CRCs (cmd 16) ---`);
        console.log(`  Raw: ${line}`);
        break;

      case '17':
        console.log(`\n--- AUTO-TUNE RESULT (cmd 17) ---`);
        console.log(`  Raw: ${line}`);
        break;

      default:
        console.log(`  RX [cmd ${cmd}]: ${line.substring(0, 300)}`);
        break;
    }
  });

  // Open port
  await new Promise((resolve, reject) => {
    port.open((err) => {
      if (err) { reject(err); return; }
      console.log(`Connected to ${COM_PORT}\n`);
      resolve();
    });
  });

  // 1. Request Device Information
  console.log('=== STEP 1: Device Information ===');
  send('$,8,#');
  await sleep(2000);

  // 2. Request variable data (sends current date/time)
  console.log('\n=== STEP 2: Variable Data (live snapshot) ===');
  const now = new Date();
  send(`$,9,0,0,0,0,0,${now.getFullYear()-2000},${now.getMonth()+1},${now.getDate()},${now.getHours()},${now.getMinutes()},${now.getSeconds()},#`);
  await sleep(2000);

  // Parse variable data if received
  if (variableData.length > 0) {
    console.log(`  Received ${variableData.length} variable response(s)`);
    // Print first response raw for inspection
    console.log(`  First response: ${variableData[0].join(',').substring(0, 300)}`);
  }

  // 3. Request a few more variable snapshots to get statistics
  console.log('\n=== STEP 3: Requesting more data... ===');
  for (let i = 0; i < 5; i++) {
    send(`$,9,0,0,0,0,0,${now.getFullYear()-2000},${now.getMonth()+1},${now.getDate()},${now.getHours()},${now.getMinutes()},${now.getSeconds()},#`);
    await sleep(500);
  }

  // 4. Request config CRCs
  console.log('\n=== STEP 4: Config CRCs ===');
  send('$,16,#');
  await sleep(2000);

  // 5. Try to get log info
  console.log('\n=== STEP 5: Flash Log Info ===');
  // Request log info — from loggingView.js the request format
  send('$,10,0,#');
  await sleep(2000);

  // 6. Summary
  console.log('\n\n========================================');
  console.log('=== READOUT SUMMARY ===');
  console.log('========================================');
  console.log(`Total responses received: ${allResponses.length}`);
  console.log(`Variable snapshots: ${variableData.length}`);
  console.log(`Config blocks: ${configBlocks.length}`);
  console.log(`Log entries: ${logEntries.length}`);

  if (deviceInfo) {
    console.log(`\nDevice: ${deviceInfo.modelName}`);
    console.log(`Firmware: ${deviceInfo.firmwareVersion}`);
    console.log(`ID: ${deviceInfo.deviceID}`);
  }

  if (statisticsData) {
    console.log(`\nStatistics raw data: ${statisticsData.join(',')}`);
  }

  // Save all raw data to file
  const fs = require('fs');
  const outFile = `pdm_readout_${now.toISOString().replace(/[:.]/g, '-')}.json`;
  const outPath = require('path').join(__dirname, 'Builds', outFile);
  fs.writeFileSync(outPath, JSON.stringify({
    timestamp: now.toISOString(),
    deviceInfo,
    statisticsData,
    variableData,
    configBlocks,
    logEntries,
    allResponses
  }, null, 2));
  console.log(`\nAll raw data saved to: Builds/${outFile}`);

  // Close
  port.close();
  console.log('\nPort closed. Done.');
}

main().catch(err => {
  console.error('ERROR:', err.message);
  if (port && port.isOpen) port.close();
  process.exit(1);
});
