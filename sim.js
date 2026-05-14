// Backgammon AI Simulation
// Run 1000 games of Sharp vs Master to gather statistics

// ─── Core game logic (extracted from worker) ───
function cloneState(s){return{board:s.board.slice(),bar:[s.bar[0],s.bar[1]],off:[s.off[0],s.off[1]]}}
function applyMove(state,from,to,player){
  const s=cloneState(state);
  if(from===-1){s.bar[player]--}else{if(player===0)s.board[from]--;else s.board[from]++}
  if(to===25||to===-2){s.off[player]++;return s}
  if(player===0){
    if(s.board[to]===-1){s.board[to]=1;s.bar[1]++}
    else s.board[to]++;
  }else{
    if(s.board[to]===1){s.board[to]=-1;s.bar[0]++}
    else s.board[to]--;
  }
  return s;
}
function playerCheckerAt(b,p,pl){return pl===0?b[p]>0:b[p]<0}
function countAt(b,p,pl){return pl===0?Math.max(0,b[p]):Math.max(0,-b[p])}
function canLand(b,p,pl){return pl===0?b[p]>=-1:b[p]<=1}
function allInHome(s,pl){
  if(s.bar[pl]>0)return false;
  if(pl===0){for(let i=6;i<24;i++)if(s.board[i]>0)return false}
  else{for(let i=0;i<18;i++)if(s.board[i]<0)return false}
  return true;
}
function highestOccupied(s,pl){
  if(pl===0){for(let i=23;i>=0;i--)if(s.board[i]>0)return i;return -1}
  for(let i=0;i<24;i++)if(s.board[i]<0)return i;return -1;
}
function pipCount(s,pl){
  let c=0;
  if(pl===0){c+=s.bar[0]*25;for(let i=0;i<24;i++)if(s.board[i]>0)c+=s.board[i]*(i+1)}
  else{c+=s.bar[1]*25;for(let i=0;i<24;i++)if(s.board[i]<0)c+=(-s.board[i])*(24-i)}
  return c;
}

function generateMoves(state,dice,player){
  const results=[];
  function recurse(st,remaining,moves){
    if(remaining.length===0){results.push({state:st,moves:moves});return}
    const die=remaining[0];const rest=remaining.slice(1);
    let found=false;
    if(st.bar[player]>0){
      const target=player===0?24-die:die-1;
      if(target>=0&&target<24&&canLand(st.board,target,player)){
        const ns=applyMove(st,-1,target,player);
        found=true;
        recurse(ns,rest,moves.concat([{from:-1,to:target,die}]));
      }
      if(!found)recurse(st,rest,moves);
      return;
    }
    const inHome=allInHome(st,player);
    const pts=[];
    for(let i=0;i<24;i++){
      if(playerCheckerAt(st.board,i,player)){
        let target=player===0?i-die:i+die;
        if(target>=0&&target<24){
          if(canLand(st.board,target,player)){pts.push({from:i,to:target});found=true}
        }else if(inHome){
          if(player===0&&target<0){
            if(target===-1||i>=highestOccupied(st,player)){pts.push({from:i,to:-2});found=true}
          }
          if(player===1&&target>=24){
            if(target===24||i<=highestOccupied(st,player)){pts.push({from:i,to:25});found=true}
          }
        }
      }
    }
    if(!found){recurse(st,rest,moves);return}
    for(const mv of pts){
      const ns=applyMove(st,mv.from,mv.to,player);
      recurse(ns,rest,moves.concat([{from:mv.from,to:mv.to,die}]));
    }
  }
  const dl=dice.slice();
  recurse(state,dl,[]);
  if(dl.length===2&&dl[0]!==dl[1])recurse(state,[dl[1],dl[0]],[]);
  let maxLen=0;
  for(const r of results)if(r.moves.length>maxLen)maxLen=r.moves.length;
  let filtered=results.filter(r=>r.moves.length===maxLen);
  if(maxLen===1&&dl.length===2&&dl[0]!==dl[1]){
    const maxDie=Math.max(dl[0],dl[1]);
    const wl=filtered.filter(r=>r.moves[0]&&r.moves[0].die===maxDie);
    if(wl.length>0)filtered=wl;
  }
  const seen={};const unique=[];
  for(const r of filtered){
    const key=r.state.board.join(',')+';'+r.state.bar.join(',')+';'+r.state.off.join(',');
    if(!seen[key]){seen[key]=true;unique.push(r)}
  }
  return unique;
}

// ─── Hit probability ───
function hitProbFull(board,blotIdx,player){
  const opp=1-player;let hits=0;
  for(let d1=1;d1<=6;d1++){for(let d2=1;d2<=6;d2++){
    let hit=false;
    const dists=[d1,d2,d1+d2];
    if(d1===d2){dists.push(d1*3);dists.push(d1*4)}
    for(const dist of dists){
      let from=opp===0?blotIdx+dist:blotIdx-dist;
      if(from>=0&&from<24){
        if(opp===0&&board[from]>0){hit=true;break}
        if(opp===1&&board[from]<0){hit=true;break}
      }
    }
    if(!hit&&d1!==d2){
      const combos=[[d1,d2],[d2,d1]];
      for(const [a,b] of combos){
        for(let src=0;src<24;src++){
          if(!playerCheckerAt(board,src,opp))continue;
          let mid=opp===0?src-a:src+a;
          if(mid<0||mid>=24)continue;
          if(!canLand(board,mid,opp))continue;
          let dest=opp===0?mid-b:mid+b;
          if(dest===blotIdx){hit=true;break}
        }
        if(hit)break;
      }
    }
    if(hit)hits++;
  }}
  return hits/36;
}

function hasContact(state){
  for(let i=0;i<24;i++){
    if(state.board[i]>0){for(let j=i+1;j<24;j++)if(state.board[j]<0)return true}
  }
  return state.bar[0]>0||state.bar[1]>0;
}

const ANCHOR_VAL=[1,3,6,14,18,10];

function evaluateRace(state,player){
  const opp=1-player;
  const myPip=pipCount(state,player);const oppPip=pipCount(state,opp);
  let score=(oppPip-myPip)*1.4;
  score+=state.off[player]*14;score-=state.off[opp]*14;
  for(let i=0;i<24;i++){
    const cnt=countAt(state.board,i,player);
    if(cnt<=0)continue;
    const ptVal=player===0?(i+1):(24-i);
    if(ptVal<=6&&cnt>2)score-=(cnt-2)*(7-ptVal)*1.5;
    if(cnt>3)score-=(cnt-3)*6;if(cnt>4)score-=(cnt-4)*8;if(cnt>5)score-=(cnt-5)*12;
  }
  let gaps=0;
  if(player===0){for(let i=0;i<6;i++)if(state.board[i]<=0)gaps++}
  else{for(let i=18;i<24;i++)if(state.board[i]>=0)gaps++}
  if(gaps<=1)score+=5;
  for(let i=0;i<24;i++){
    const cnt=countAt(state.board,i,player);
    if(cnt<=0)continue;
    const ptVal=player===0?(i+1):(24-i);
    if(ptVal>6)score-=cnt*Math.floor((ptVal-1)/6)*2;
  }
  return score;
}

function evaluateContact(state,player){
  const opp=1-player;
  const myPip=pipCount(state,player);const oppPip=pipCount(state,opp);
  let score=(oppPip-myPip)*0.4;
  score+=state.off[player]*15;score-=state.off[opp]*15;
  score-=state.bar[player]*28;score+=state.bar[opp]*20;
  let blotCount=0;
  for(let i=0;i<24;i++){
    if(player===0&&state.board[i]===1){
      blotCount++;
      const prob=hitProbFull(state.board,i,0);
      const ptVal=i+1;
      let pw;
      if(ptVal<=6){pw=ptVal===5?2.0:ptVal===4?1.8:ptVal===6?1.5:1.0}
      else if(ptVal<=12){pw=1.8}
      else if(ptVal<=18){pw=0.9}
      else{pw=0.4}
      score-=prob*pw*22;
    }else if(player===1&&state.board[i]===-1){
      blotCount++;
      const prob=hitProbFull(state.board,i,1);
      const oppPtVal=24-i;
      let pw;
      if(oppPtVal<=6){pw=oppPtVal===5?2.0:oppPtVal===4?1.8:oppPtVal===6?1.5:1.0}
      else if(oppPtVal<=12){pw=1.8}
      else if(oppPtVal<=18){pw=0.9}
      else{pw=0.4}
      score-=prob*pw*22;
    }
  }
  if(blotCount>=2)score-=(blotCount-1)*8;
  if(blotCount>=3)score-=(blotCount-2)*10;
  if(player===0){
    for(let i=4;i<11;i++){
      if(state.board[i]>=2){
        const ptValue=i+1;
        const pointBonus=ptValue===5?6:ptValue===7?6:ptValue===8?5:ptValue===6?4:3;
        score+=pointBonus;
      }
    }
  }else{
    for(let i=13;i<20;i++){
      if(state.board[i]<=-2){
        const oppPtValue=24-i;
        const pointBonus=oppPtValue===5?6:oppPtValue===7?6:oppPtValue===8?5:oppPtValue===6?4:3;
        score+=pointBonus;
      }
    }
  }
  let consecutive=0,bestPrime=0,primeStart=-1;
  for(let i=0;i<24;i++){
    if(countAt(state.board,i,player)>=2){consecutive++;if(consecutive>bestPrime){bestPrime=consecutive;primeStart=i-consecutive+1}}
    else consecutive=0;
  }
  if(bestPrime>=2)score+=bestPrime*bestPrime*5;
  if(bestPrime>=3){
    let trapped=0;
    for(let i=0;i<24;i++){
      if(countAt(state.board,i,opp)>0){
        if(player===0&&i>primeStart+bestPrime-1)trapped+=countAt(state.board,i,opp);
        if(player===1&&i<primeStart)trapped+=countAt(state.board,i,opp);
      }
    }
    score+=trapped*bestPrime*3;
  }
  let homePoints=0;
  if(player===0){for(let i=0;i<6;i++)if(state.board[i]>=2)homePoints++}
  else{for(let i=18;i<24;i++)if(state.board[i]<=-2)homePoints++}
  const homeMultiplier=state.bar[opp]>0?10:6;
  score+=homePoints*homeMultiplier;
  if(homePoints===6)score+=25;
  if(player===0){for(let i=18;i<24;i++)if(state.board[i]>=2){const oppPt=24-i;score+=ANCHOR_VAL[oppPt-1]}}
  else{for(let i=0;i<6;i++)if(state.board[i]<=-2)score+=ANCHOR_VAL[i]}
  for(let i=0;i<24;i++){const cnt=countAt(state.board,i,player);if(cnt>3)score-=(cnt-3)*6;if(cnt>4)score-=(cnt-4)*8;if(cnt>5)score-=(cnt-5)*12}
  if(player===0){for(let i=4;i<12;i++)if(state.board[i]===3)score+=3}
  else{for(let i=12;i<20;i++)if(-state.board[i]===3)score+=3}
  return score;
}

function evaluateMaster(state,player){
  const isRace=!hasContact(state)&&state.bar[0]===0&&state.bar[1]===0;
  if(isRace)return evaluateRace(state,player);
  let base=evaluateContact(state,player);
  let consecutive=0,bestPrime=0;
  for(let i=0;i<24;i++){
    if(countAt(state.board,i,player)>=2){consecutive++;if(consecutive>bestPrime)bestPrime=consecutive}
    else consecutive=0;
  }
  if(bestPrime>=4)base+=bestPrime*bestPrime*2;
  return base;
}

// ─── 2-ply search (Master) ───
function search2Ply(state,dice,player){
  const opp=1-player;
  const allMoves=generateMoves(state,dice,player);
  if(allMoves.length===0)return null;
  if(allMoves.length===1)return allMoves[0];
  const scored=allMoves.map((m,idx)=>({idx,sc:evaluateMaster(m.state,player)}));
  scored.sort((a,b)=>b.sc-a.sc);
  const topN=Math.min(8,scored.length);
  const ROLLS=[];
  for(let d1=1;d1<=6;d1++)for(let d2=d1;d2<=6;d2++){
    const w=d1===d2?1:2;
    const dl=d1===d2?[d1,d1,d1,d1]:[d1,d2];
    ROLLS.push({dice:dl,weight:w});
  }
  let bestMove=null;let bestAvg=-Infinity;
  for(let c=0;c<topN;c++){
    const cand=allMoves[scored[c].idx];
    let totalScore=0;
    for(const roll of ROLLS){
      const oppMoves=generateMoves(cand.state,roll.dice,opp);
      let oppBestScore=-Infinity;let oppBestState=cand.state;
      if(oppMoves.length===0){
        oppBestScore=evaluateMaster(cand.state,player);
      }else{
        let evalPool=oppMoves;
        if(oppMoves.length>15){
          const oppScored=oppMoves.map((m,i)=>({idx:i,sc:evaluateMaster(m.state,opp)}));
          oppScored.sort((a,b)=>b.sc-a.sc);
          evalPool=oppScored.slice(0,15).map(s=>oppMoves[s.idx]);
        }
        for(const m of evalPool){
          const sc=evaluateMaster(m.state,opp);
          if(sc>oppBestScore){oppBestScore=sc;oppBestState=m.state}
        }
        oppBestScore=evaluateMaster(oppBestState,player);
      }
      totalScore+=oppBestScore*roll.weight;
    }
    const avg=totalScore/36;
    if(avg>bestAvg){bestAvg=avg;bestMove=cand}
  }
  return bestMove;
}

// ─── Monte Carlo Rollouts ───
function pickRolloutMove(state,dice,player){
  // Fast policy used inside rollouts: greedy + small noise
  const moves=generateMoves(state,dice,player);
  if(moves.length===0)return null;
  if(moves.length===1)return moves[0];
  let best=moves[0];let bestSc=-Infinity;
  for(const m of moves){
    const sc=evaluateMaster(m.state,player)+Math.random()*4;
    if(sc>bestSc){bestSc=sc;best=m}
  }
  return best;
}

function rolloutResult(startState,nextPlayer,maxDepth){
  let cur=cloneState(startState);
  let p=nextPlayer;
  for(let t=0;t<maxDepth;t++){
    if(cur.off[0]>=15)return 0; // player 0 wins
    if(cur.off[1]>=15)return 1; // player 1 wins
    const d1=Math.floor(Math.random()*6)+1;
    const d2=Math.floor(Math.random()*6)+1;
    const dl=d1===d2?[d1,d1,d1,d1]:[d1,d2];
    const result=pickRolloutMove(cur,dl,p);
    if(result)cur=result.state;
    p=1-p;
  }
  // Timeout: pick by pip count
  return pipCount(cur,0)<pipCount(cur,1)?0:1;
}

function searchMC(state,dice,player,rollouts,topCandidates,maxDepth){
  const allMoves=generateMoves(state,dice,player);
  if(allMoves.length===0)return null;
  if(allMoves.length===1)return allMoves[0];
  // Filter to top N candidates by static eval
  const scored=allMoves.map((m,i)=>({idx:i,sc:evaluateMaster(m.state,player)}));
  scored.sort((a,b)=>b.sc-a.sc);
  const topN=Math.min(topCandidates||4,scored.length);
  let bestMove=null;let bestWinCount=-1;
  for(let c=0;c<topN;c++){
    const move=allMoves[scored[c].idx];
    let myWins=0;
    for(let i=0;i<rollouts;i++){
      const winner=rolloutResult(move.state,1-player,maxDepth||60);
      if(winner===player)myWins++;
    }
    if(myWins>bestWinCount){bestWinCount=myWins;bestMove=move}
  }
  return bestMove;
}

// ─── AI dispatcher ───
function aiMove(state,dice,player,difficulty){
  const allMoves=generateMoves(state,dice,player);
  if(allMoves.length===0)return null;
  if(allMoves.length===1)return allMoves[0];
  if(difficulty==='rookie'){
    const hitMoves=allMoves.filter(m=>m.state.bar[1-player]>state.bar[1-player]);
    const pool=hitMoves.length>0&&Math.random()<0.4?hitMoves:allMoves;
    return pool[Math.floor(Math.random()*pool.length)];
  }
  if(difficulty==='master')return searchMC(state,dice,player,12,4,60); // 12 rollouts × 4 candidates = 48 rollouts
  if(difficulty==='masterDeep')return searchMC(state,dice,player,40,6,80);
  if(difficulty==='master2ply')return search2Ply(state,dice,player); // old 2-ply for comparison
  // sharp
  let best=null;let bestScore=-Infinity;
  for(const m of allMoves){
    let sc=evaluateMaster(m.state,player);
    sc+=Math.random()*3;
    if(sc>bestScore){bestScore=sc;best=m}
  }
  return best;
}

// ─── Game setup ───
function initBoard(){
  const b=new Array(24).fill(0);
  b[23]=2;b[12]=5;b[7]=3;b[5]=5;
  b[0]=-2;b[11]=-5;b[16]=-3;b[18]=-5;
  return b;
}
function initState(){return{board:initBoard(),bar:[0,0],off:[0,0]}}
function rollDice(){return[Math.floor(Math.random()*6)+1,Math.floor(Math.random()*6)+1]}
function getDiceList(d){return d[0]===d[1]?[d[0],d[0],d[0],d[0]]:[d[0],d[1]]}

// ─── Single game simulator ───
function playOneGame(p0Diff,p1Diff){
  let state=initState();
  // Opening roll
  let d=rollDice();
  while(d[0]===d[1])d=rollDice();
  let player=d[0]>d[1]?0:1;
  let dice=getDiceList(d);
  let turns=0;
  let maxTurns=400;
  while(turns<maxTurns){
    const diff=player===0?p0Diff:p1Diff;
    const result=aiMove(state,dice,player,diff);
    if(result){state=result.state}
    if(state.off[0]>=15)return{winner:0,turns,state};
    if(state.off[1]>=15)return{winner:1,turns,state};
    player=1-player;
    dice=getDiceList(rollDice());
    turns++;
  }
  return{winner:-1,turns,state}; // draw/timeout
}

// ─── Run simulation ───
function run(N,p0Diff,p1Diff){
  const results={
    [p0Diff]:{wins:0,gammons:0,backgammons:0},
    [p1Diff]:{wins:0,gammons:0,backgammons:0},
    timeouts:0,
    totalTurns:0,
    games:0,
  };
  const startTime=Date.now();
  for(let i=0;i<N;i++){
    const r=playOneGame(p0Diff,p1Diff);
    results.totalTurns+=r.turns;
    results.games++;
    if(r.winner===-1){results.timeouts++;continue}
    const winnerDiff=r.winner===0?p0Diff:p1Diff;
    const loserOff=r.winner===0?r.state.off[1]:r.state.off[0];
    if(loserOff===0){
      // gammon or backgammon
      const loserBar=r.winner===0?r.state.bar[1]:r.state.bar[0];
      const loserInWinnerHome=r.winner===0
        ? r.state.board.slice(0,6).some(c=>c<0)
        : r.state.board.slice(18,24).some(c=>c>0);
      if(loserBar>0||loserInWinnerHome){
        results[winnerDiff].backgammons++;
      }else{
        results[winnerDiff].gammons++;
      }
    }
    results[winnerDiff].wins++;
    if((i+1)%100===0){
      const elapsed=(Date.now()-startTime)/1000;
      process.stdout.write(`\rGames: ${i+1}/${N} (${elapsed.toFixed(1)}s)`);
    }
  }
  process.stdout.write('\n');
  return results;
}

// ─── Main ───
const N=parseInt(process.argv[2]||'1000',10);
const p0=process.argv[3]||'sharp';
const p1=process.argv[4]||'master';

console.log(`Running ${N} games: ${p0} (player 0) vs ${p1} (player 1)`);
console.log('---');
const t0=Date.now();
const r=run(N,p0,p1);
const elapsed=(Date.now()-t0)/1000;

console.log(`\n=== RESULTS (${N} games in ${elapsed.toFixed(1)}s) ===`);
console.log(`Avg game length: ${(r.totalTurns/r.games).toFixed(1)} turns`);
console.log(`Timeouts: ${r.timeouts}`);
console.log('');
const fmt=d=>{
  const w=r[d].wins;
  const g=r[d].gammons;
  const bg=r[d].backgammons;
  const total=r.games-r.timeouts;
  const wp=(100*w/total).toFixed(1);
  const points=w+g+(bg*2); // approx EMG points
  return `${d.toUpperCase()}: ${w} wins (${wp}%), ${g} gammons, ${bg} backgammons`;
};
console.log(fmt(p0));
console.log(fmt(p1));
console.log('');

const total=r.games-r.timeouts;
const p0Points=r[p0].wins + r[p0].gammons + r[p0].backgammons*2;
const p1Points=r[p1].wins + r[p1].gammons + r[p1].backgammons*2;
console.log(`EMG-equivalent points: ${p0}=${p0Points}, ${p1}=${p1Points}`);
const diff=p1Points-p0Points;
const ppg=(diff/total).toFixed(3);
console.log(`Net advantage: ${p1} +${ppg} ppg (points per game)`);
