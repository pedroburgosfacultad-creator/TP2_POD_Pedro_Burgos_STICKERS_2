import React from 'react';
import {AbsoluteFill,interpolate,useCurrentFrame,useVideoConfig} from 'remotion';
import {flow} from './content';
export function Journey(){
 const frame=useCurrentFrame();const {fps}=useVideoConfig();const step=Math.min(5,Math.floor(frame/(4*fps)));const phase=frame%(4*fps);
 return <AbsoluteFill style={{background:'#103f3b',color:'#f6f4e9',fontFamily:'Segoe UI, sans-serif',padding:'44px 54px'}}>
  <div style={{fontSize:15,letterSpacing:3,color:'#a8d5c9'}}>EL VIAJE DE UN STICKER · {String(step+1).padStart(2,'0')} / 06</div>
  <div style={{display:'flex',gap:14,marginTop:32}}>{flow.map((s,i)=><div key={s.title} style={{flex:1,borderTop:`3px solid ${i<=step?'#d3ed9a':'#49706a'}`,paddingTop:12,fontSize:15,color:i===step?'#d3ed9a':'#adc4bd'}}>{i+1}. {s.title}</div>)}</div>
  <div style={{marginTop:38,display:'flex',alignItems:'center',gap:32,opacity:interpolate(phase,[0,12],[0.4,1],{extrapolateRight:'clamp'})}}>
   <div style={{width:142,height:164,background:'#f5f1df',borderRadius:22,color:'#164d43',display:'flex',alignItems:'center',justifyContent:'center',fontSize:65,rotate:interpolate(phase,[0,4*fps],['-5deg','5deg'],{extrapolateRight:'clamp'}),border:'7px solid white',boxShadow:'8px 12px 0 #092e2b'}}>✳</div>
   <div style={{flex:1}}><div style={{fontSize:40,fontWeight:650,letterSpacing:-1}}>{flow[step].title}</div><div style={{fontSize:21,lineHeight:1.45,marginTop:15,color:'#d6e5dd',maxWidth:620}}>{flow[step].body}</div></div>
  </div>
  <div style={{position:'absolute',bottom:54,left:54,right:54,display:'flex',gap:14,alignItems:'center',fontSize:19}}><span style={{padding:'12px 18px',background:'#28544e',borderRadius:10}}>{flow[step].input}</span><span style={{color:'#d3ed9a'}}>→</span><span style={{padding:'12px 18px',background:'#d3ed9a',borderRadius:10,color:'#153c32'}}>{flow[step].output}</span></div>
 </AbsoluteFill>;
}
