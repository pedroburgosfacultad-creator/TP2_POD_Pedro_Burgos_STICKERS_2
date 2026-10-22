import {build} from 'esbuild';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));
const result=await build({absWorkingDir:root,entryPoints:['src/main.jsx'],bundle:true,write:false,minify:true,format:'iife',define:{'process.env.NODE_ENV':'"production"'},loader:{'.css':'text'},legalComments:'none'});
const js=result.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
const html=`<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Guía visual del TP2 de Pedro Burgos: código, simuladores y defensa."><title>StickerLab · Comprender y defender</title></head><body><div id="root"></div><script>${js}</script></body></html>`;
for(const dir of [path.join(root,'dist'),path.resolve(root,'../../outputs/defensa')]){mkdirSync(dir,{recursive:true});writeFileSync(path.join(dir,'index.html'),html);}
console.log('Guía autocontenida generada: outputs/defensa/index.html');
