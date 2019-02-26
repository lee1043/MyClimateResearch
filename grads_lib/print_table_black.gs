'reinit'

'set display color white'
'c'

'set font 4'

*-----------------------------------------
'set string 1 c 4'
'set strsiz 0.14'
'draw string 4.25 10.0 rgb_black.gs'

'run rgb_black.gs'
ystep = 1
while ( ystep <= 3 )
xstep = 1
while ( xstep <= 20 )

step = (ystep-1)*20 + xstep

y1 = 9.3 - (ystep-1) * 1.5
y2 = y1 + 0.3
x1 = 0.5 + (xstep-1) * 0.35
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


