function cbarc(args)
*
*	circle colar bar
*
*	originally written by Paul Dirmeryer, COLA 
*	for the wx graphics on the COLA Web Page
*
*	generalized by Mike Fiorino, LLNL 26 Jul 1996
*
*	xc and yc are the center of the circle
*	bc is the background color
*
*	if not defined user upper left hand corner
*
*	sample call:
*
*	run cbarc 11 8.5 2
*	
*	or
*
*	run cbarc 
*
*	to use the defaults
*

xc=subwrd(args,1)
yc=subwrd(args,2)

if(xc='' | yc = '')
  'q gxinfo'
  card=sublin(result,2)
  pagex=subwrd(card,4)
  pagey=subwrd(card,6)
  xc=pagex
  yc=pagey
endif 

*
*	use black for the background as a default	
*
bc=subwrd(args,3)
if(bc = '' | bc='bc') ; bc=0; endif 

*
*	get the shades of the last graphic
*

'q shades'
_shades = result
*aa = 1.50
aa = 1.40
*rt = 0.59 * aa
rt = 0.65 * aa
*ro = 0.575 * aa
ro = 0.5 * aa
*ri = 0.30 * aa
ri = 0.25 * aa
xa = xc + 0.05
ya = yc + 0.05
ll = 1
data = sublin(_shades,1)
*ll = subwrd(data,5)
ll = subwrd(data,5)-1
ml=ll
mm = 1
while (mm <= ll)
  mmp1 = mm + 1
  data = sublin(_shades,mmp1)
  col.mm = subwrd(data,1)
  if (col.mm = 0)
    col.mm = bc
  endif
  lim.mm = subwrd(data,3)
  if (lim.mm = '>')
    lim.mm = ' '
    ml=ml-1
    break
  else 
    mm = mm + 1
  endif
endwhile

*dd = 3.1415926*2.15/ll
dd = 3.1415926*2.15/(ll+0.6)
*id = 3.1415926*2/3
id = 3.1415926*1.91/3.1
id2 = 3.1415926*1.91/3.1*1.2

'set line 'bc' 1 12'
xe = xc + aa
x1 = xc + 0.01
y1 = yc - aa
*'draw polyf 'x1' 'yc' 'xe' 'yc' 'xe' 'y1
*'set line 1 1 6'
*'draw line 'x1' 'yc' 'xc' 'y1
*'draw mark 3 'xc+0.03' 'yc+0.05' 2.25'
'draw mark 3 'xc+0.03' 'yc+0.05' 1.7'
'set line 1 1 0.12'
*'draw mark 2 'xc+0.03' 'yc+0.05' 2.25'
'draw mark 2 'xc+0.03' 'yc+0.05' 1.7'

'd 'ro'*cos('id')'
xfo = subwrd(result,4) + xa
'd 'ro'*sin('id')'
yfo = subwrd(result,4) + ya
'd 'ri'*cos('id')'
xfi = subwrd(result,4) + xa
'd 'ri'*sin('id')'
yfi = subwrd(result,4) + ya
mm = 1 

while(mm<=ll)    
  id = id - dd
  id2 = id2 - dd
  'd 'ro'*cos('id')'
  xlo = subwrd(result,4) + xa
  'd 'ro'*sin('id')'
  ylo = subwrd(result,4) + ya
  'd 'ri'*cos('id')'
  xli = subwrd(result,4) + xa
  'd 'ri'*sin('id')'
  yli = subwrd(result,4) + ya
*  'd 'rt'*cos('id')'
  'd 'rt*0.55'*cos('id2')'
*  xft = subwrd(result,4) + xa+0.05
  xft = subwrd(result,4) + xa+0.06
*  'd 'rt'*sin('id')'
  'd 'rt*0.6'*sin('id2')'
  yft = subwrd(result,4) + ya
 
*  did = id * 180 / 3.14159 - 180
  did = 0

  'set line 'col.mm' 1 3'
  'draw polyf 'xfi' 'yfi' 'xfo' 'yfo' 'xlo' 'ylo' 'xli' 'yli
  'set line 'bc
  'draw line 'xfi' 'yfi' 'xfo' 'yfo
  'set string 1 r 4 'did
  'set strsiz 0.10 0.11'


  if(mm<=ml)
*    'draw string 'xft' 'yft' 'lim.mm
*    'draw string 'xft' 'yft' 'lim.mm-0.5
    if(mm=1);label='N';endif
    if(mm=2);label='NE';endif
    if(mm=3);label='E';endif
    if(mm=4);label='SE';endif
    if(mm=5);label='S';endif
    if(mm=6);label='SW';endif
    if(mm=7);label='W';endif
    if(mm=8);label='NW';endif
    'draw string 'xft' 'yft' 'label
  endif

  xfo = xlo
  yfo = ylo
  xfi = xli
  yfi = yli
  mm = mm + 1
endwhile
*
*	default string
*
'set string 1 l 4 0'
*
return
  
