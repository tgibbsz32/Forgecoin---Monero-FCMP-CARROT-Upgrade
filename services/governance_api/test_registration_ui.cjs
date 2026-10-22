"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const {test}=require("node:test");
const html=fs.readFileSync("docs/member-registration.html","utf8");
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function harness(host,port,path){
 const ids=["role","requirements","mode","login","logout","send","refresh","wallet","history","feedback","application","reference","statement"];
 const el=Object.fromEntries(ids.map(id=>[id,{textContent:"",value:"",disabled:false,handlers:{},addEventListener(type,fn){this.handlers[type]=fn},replaceChildren(){this.textContent="";this.children=[]},appendChild(x){this.children.push(x)},children:[]}]));
 const requests=[];
 const ctx=vm.createContext({document:{getElementById:id=>el[id],createElement:()=>({textContent:"",append(){}})},location:{hostname:host,port,pathname:path},window:{addEventListener(){}},TextEncoder,fetch:(url,opts)=>{requests.push({url,opts});return Promise.reject(Error("Network unavailable"))}});
 vm.runInContext(script,ctx);
 return {el,requests};
}
test("public GitHub Pages preview fails closed",()=>{const {el}=harness("tgibbsz32.github.io","","/forgecoin/member-registration.html");for(const name of ["login","send","refresh"])assert.equal(el[name].disabled,true);assert.match(el.mode.textContent,/disabled/i)});
test("unrelated localhost path fails closed",()=>{const {el}=harness("localhost","8765","/member-registration.html");assert.equal(el.login.disabled,true)});
test("expected development route permits local wallet button",()=>{const {el}=harness("127.0.0.1","8765","/member/registration");assert.equal(el.login.disabled,false);assert.equal(el.send.disabled,true)});
