'reinit'

'open /gpfs1/e981hsy/user/agfe/wrf_cal_speed/domain_fig/domain1/domain1.ctl'

'set display color white'
'c'

'set grads off'
'set gxout shaded'
'set xlab off'
'set ylab off'
'run grads_libs/rgb_rbw.gs'
'set clevs   1 5 20 30 40 50 60 70 80 90 100 150  200 250 300 350 400 450  500 550  600 650 700 800 900 1000 1500 2000 2500 3000 3500 4000' 
'set ccols 58  52 51 50 49 48 47 46 45 44 43 42 41 40 39 38 37 36 35 34 33 32 31 30 29 28 27 26 25 24 23 22 21'

'd hgt'

'set gxout contour'
'set clab off'
'set ccolor 15'
'set cint 10'
'd xlat'
'set cint 10'
'set ccolor 15'
'd xlong'

'enable print temp.gr'
'print'
'disable print'

'!gxps -c -i temp.gr -o temp.ps'
