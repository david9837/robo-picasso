
"use strict";

let MasterboardDataMsg = require('./MasterboardDataMsg.js');
let Digital = require('./Digital.js');
let RobotModeDataMsg = require('./RobotModeDataMsg.js');
let ToolDataMsg = require('./ToolDataMsg.js');
let IOStates = require('./IOStates.js');
let Analog = require('./Analog.js');
let RobotStateRTMsg = require('./RobotStateRTMsg.js');

module.exports = {
  MasterboardDataMsg: MasterboardDataMsg,
  Digital: Digital,
  RobotModeDataMsg: RobotModeDataMsg,
  ToolDataMsg: ToolDataMsg,
  IOStates: IOStates,
  Analog: Analog,
  RobotStateRTMsg: RobotStateRTMsg,
};
