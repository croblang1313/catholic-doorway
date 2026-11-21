// Copies the Rosary prayer texts out of site/assets/js/rosary.js into texts.json,
// so the spoken audio always matches what the page shows. Run from the repo root:
//   node scripts/rosary_audio/extract_texts.js
const fs=require('fs');
const src=fs.readFileSync('site/assets/js/rosary.js','utf8');
const a=src.indexOf('var P = {'), b=src.indexOf('var latin = false;');
const body=src.slice(a,b);
const out={};
for (const lang of ['en','es','pt','tl']){
  const document={documentElement:{lang}};
  const f=new Function('document', body+'; return {P:P,SETS:SETS};');
  out[lang]=f(document);
}
fs.writeFileSync(__dirname+'/texts.json',JSON.stringify(out,null,1)+'\n');
