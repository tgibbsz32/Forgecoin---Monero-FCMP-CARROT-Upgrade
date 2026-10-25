"use strict";
// Exercise session lifecycle with controllable network completion order.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {test} = require("node:test");
const source = fs.readFileSync(path.join(__dirname, "admin_static/admin.js"), "utf8");
function setup() {
  const ids = ["token", "workspace", "applications", "elections", "identity", "message", "create", "login", "refresh", "lock", "weights", "title", "category"];
  const elements = Object.fromEntries(ids.map(id => [id, {value: "", textContent: "", hidden: false, children: [], replaceChildren() { this.children = []; }}]));
  elements.create.reset = () => { elements.weights.value = ""; elements.title.value = ""; elements.category.value = "community"; };
  const requests = [];
  const context = vm.createContext({
    document: {getElementById: id => elements[id]},
    window: {addEventListener() {}}, AbortController, DOMException,
    fetch: (url, options) => new Promise(resolve => requests.push({url, options, resolve})),
  });
  vm.runInContext(source, context);
  const run = code => vm.runInContext(code, context);
  const reply = (index, status, body) => requests[index].resolve({ok: status === 200, status, json: async () => body});
  return {elements, requests, run, reply};
}

test("locking clears draft weights and cancels outstanding review reads", async () => {
  const {elements, requests, run, reply} = setup();
  elements.weights.value = '{"private-wallet":100}';
  elements.title.value = "Private draft";
  elements.applications.children = ["private evidence"];
  run('token = "old-session"');
  const request = run('api("applications")');
  run("lock()");
  assert.equal(requests[0].options.signal.aborted, true);
  assert.equal(elements.weights.value, "");
  assert.equal(elements.title.value, "");
  assert.equal(elements.workspace.hidden, true);
  assert.equal(elements.applications.children.length, 0);
  reply(0, 200, {applications: [{statement: "sensitive"}]});
  await assert.rejects(request, {name: "AbortError"});
});

test("late unauthorized response cannot lock a newer session", async () => {
  const {run, reply} = setup();
  run('token = "old-session"');
  const old = run('api("elections")');
  run('lock(); token = "new-session"');
  reply(0, 401, {detail: "Old credential expired"});
  await assert.rejects(old, {name: "AbortError"});
  assert.equal(run("token"), "new-session");
});

test("late network error cannot overwrite the locked screen", async () => {
  const {elements, run} = setup();
  const pending = run('action({disabled:false}, () => new Promise((resolve, reject) => { window.rejectOld = reject; }))');
  run("lock()");
  const lockedMessage = elements.message.textContent;
  run('window.rejectOld(new Error("Old network failure"))');
  await pending;
  assert.equal(elements.message.textContent, lockedMessage);
});

test("current unauthorized response still clears credentials and drafts", async () => {
  const {elements, run, reply} = setup();
  elements.weights.value = "sensitive draft";
  run('token = "expired-session"');
  const request = run('api("applications")');
  reply(0, 401, {detail: "Administrator authentication required"});
  await assert.rejects(request, /Administrator authentication required/);
  assert.equal(run("token"), "");
  assert.equal(elements.weights.value, "");
  assert.equal(elements.workspace.hidden, true);
});
