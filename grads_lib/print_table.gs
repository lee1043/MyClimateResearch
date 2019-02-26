'reinit'

'set display color white'
'c'


'set font 4'

*-----------------------------------------
'set string 1 c 4'
'set strsiz 0.10'
'draw string 0.6 10.0 rgb_rbw.gs'

'run rgb_rbw.gs'
step = 1
while ( step <= 45 )
y1 = 9.5 - (step-1) * 0.2
y2 = y1 + 0.2
x1 = 0.4
x2 = 0.8
s1 = x2 + 0.2
s2 = ( y1 + y2) /2
col = step + 20
'set line 'col
'draw recf 'x1' 'y1' 'x2' 'y2
'set line 1'
'draw rec 'x1' 'y1' 'x2' 'y2
'set string 1 c 3'
'set strsiz 0.1'
'draw string 's1' 's2' 'col
step = step + 1
endwhile
*-----------------------------------------
'set string 1 c 4'
'set strsiz 0.10'
'draw string 2.0 10.0 rgb_red_diff.gs'

'run rgb_red_diff.gs'
step = 1
while ( step <= 31 )
y1 = 9.4 - (step-1) * 0.3
y2 = y1 + 0.3
x1 = 1.8
x2 = 2.2
s1 = x2 + 0.2
s2 = ( y1 + y2) /2
col = step + 20
'set line 'col
'draw recf 'x1' 'y1' 'x2' 'y2
'set line 1'
'draw rec 'x1' 'y1' 'x2' 'y2
'set string 1 c 3'
'set strsiz 0.1'
'draw string 's1' 's2' 'col
step = step + 1
endwhile
*-----------------------------------------
'set string 1 c 4'
'set strsiz 0.10'
'draw string 3.4 10.0 rgb_black.gs'

'run rgb_black.gs'
step = 1
while ( step <= 25 )
y1 = 9.4 - (step-1) * 0.3
y2 = y1 + 0.3
x1 = 3.2
x2 = 3.6
s1 = x2 + 0.2
s2 = ( y1 + y2) /2
col = step + 20
'set line 'col
'draw recf 'x1' 'y1' 'x2' 'y2
'set line 1'
'draw rec 'x1' 'y1' 'x2' 'y2
'set string 1 c 3'
'set strsiz 0.1'
'draw string 's1' 's2' 'col
step = step + 1
endwhile
*-----------------------------------------
'set string 1 c 4'
'set strsiz 0.10'
'draw string 6.3 10.0 rgb_dft.gs'

'run rgb_dft.gs'
ystep = 1
while ( ystep <= 6 )
xstep = 1
while ( xstep <= 9 )

step = (ystep-1)*10 + xstep

y1 = 9.3 - (ystep-1) * 1.5
y2 = y1 + 0.3
x1 = 4.5 + (xstep-1) * 0.4
x2 = x1 + 0.4
s1 = (x1+x2)/2.
s2 = y1 - 0.15
col = step + 20
'set line 'col
'draw recf 'x1' 'y1' 'x2' 'y2
'set line 1'
'draw rec 'x1' 'y1' 'x2' 'y2
'set string 1 c 3'
'set strsiz 0.1'
'draw string 's1' 's2' 'col

xstep = xstep + 1
endwhile
ystep = ystep + 1
endwhile
*-----------------------------------------


'enable print temp.gr'
'print'
'disable print'
'!gxps -c -i temp.gr -o col_table.ps'
'!convert col_table.ps col_table.gif'


