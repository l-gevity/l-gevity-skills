#!/usr/bin/env node
import { exportCommand } from "./commands/export.js";
import { reportCommand } from "./commands/report.js";
import { printCommand } from "./commands/print.js";

const commands = { export: exportCommand, report: reportCommand, print: printCommand };
const [name, file] = process.argv.slice(2);
const records = file ? JSON.parse(await import("node:fs").then((fs) => fs.readFileSync(file, "utf8"))) : [];
process.stdout.write(commands[name](records) + "\n");
