function main(args)

station(127.21,36.30,RKTF)
station(127.10,37.43,RKSM)
station(126.96,37.53,RKSF)
station(127.00,37.23,RKSW)
station(127.03,37.08,RKSO)
station(127.95,37.43,RKNW)
station(127.88,37.01,RKTI)
station(127.50,36.70,RKTU)
station(126.48,36.70,RKTP)
station(127.48,36.55,RKTE)
station(128.95,37.75,RKNN)
station(128.35,36.63,RKTY)
station(128.65,35.88,RKTN)
station(126.61,35.90,RKJK)
station(126.81,35.11,RKJJ)
station(128.93,35.16,RKPK)
station(128.06,35.06,RKPS)
station(130.87,37.50,RKNL)

return

function station(lo,la,spot)

'q w2xy 'lo' 'la
say result
x1 = subwrd(result,3)
y1 = subwrd(result,6)

y2 = y1 - 0.15

*'set string 22 c 6'
*'set strsiz 0.12'
*'draw string 'x1' 'y2' 'spot

*'set line 27'
'set line 99'
'draw mark 3 'x1' 'y1' 0.10'
return

