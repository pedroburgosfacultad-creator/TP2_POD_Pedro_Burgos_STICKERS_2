import http from 'node:http';
import {readFileSync} from 'node:fs';
const file=new URL('./dist/index.html',import.meta.url);
http.createServer((req,res)=>{if(req.url==='/'||req.url==='/index.html'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});res.end(readFileSync(file));}else{res.writeHead(404);res.end('No encontrado');}}).listen(4173,'127.0.0.1',()=>console.log('http://127.0.0.1:4173'));
