***************************************************************************************
* $Id: tave.gs,v 1.47 2014/01/24 04:38:40 bguan Exp $
*
* Copyright (c) 2012-2013, Bin Guan
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without modification, are
* permitted provided that the following conditions are met:
*
* 1. Redistributions of source code must retain the above copyright notice, this list
*    of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright notice, this
*    list of conditions and the following disclaimer in the documentation and/or other
*    materials provided with the distribution.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
* OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
* SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
* INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
* TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
* BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
* CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
* ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
* DAMAGE.
***************************************************************************************
function tave(arg)
*
* Time averaging: create lower resolution time series from higher resolution time series; e.g., daily to monthly.
*
rc=gsfallow('on')

* Define system temporary directory.
tmpdir='/tmp'
* Get username and create user-specific temporary directory.
'!echo $USER > .bGASL.txt'
rc=read('.bGASL.txt')
while(sublin(rc,1))
  '!echo $USER > .bGASL.txt'
  rc=read('.bGASL.txt')
endwhile
user=sublin(rc,2)
'!rm .bGASL.txt'
mytmpdir=tmpdir'/bGASL-'user
'!mkdir -p 'mytmpdir
* Get process ID.
pidlock=mytmpdir'/pid.lock'
pidfile=mytmpdir'/pid.txt'
'!while true; do if mkdir 'pidlock'; then break; else echo System busy. Please wait...; sleep 1; fi; done 2> /dev/null'
'!echo $PPID > 'pidfile
rc=read(pidfile)
randnum=sublin(rc,2)
'!rm -r 'pidlock

step=subwrd(arg,1)

*
* Parse -v option.
*
num_var=parseopt(arg,'-','v','var')
if(num_var=0)
  usage()
  return
endif

*
* Initialize other options.
*
cnt=1
while(cnt<=num_var)
  _.name.cnt=_.var.cnt
  _.desc.cnt=_.var.cnt
  cnt=cnt+1
endwhile
_.undef.1=dfile_undef()
_.sum.1=0
_.file.1=''
_.path.1='.'

*
* Parse -n option.
*
rc=parseopt(arg,'-','n','name')

*
* Parse -d option (description to be used in output).
*
rc=parseopt(arg,'-','d','desc')

*
* Parse -re option.
*
num_RegridArg=parseopt(arg,'-','re','RegridArg')

*
* Parse -u option.
*
rc=parseopt(arg,'-','u','undef')

*
* Parse -sum option.
*
rc=parseopt(arg,'-','sum','sum')

*
* Parse -o option.
*
rc=parseopt(arg,'-','o','file')

*
* Parse -p option.
*
rc=parseopt(arg,'-','p','path')

if(num_RegridArg>=1 & num_RegridArg<=5)
  say '[tave ERROR] -re needs 6 arguments: nx lon_start dlon ny lat_start dlat'
  return
endif
if(num_RegridArg>=7)
  say '[tave ERROR] -re can only have 6 arguments: nx lon_start dlon ny lat_start dlat'
  return
endif

if(_.sum.1=1)
  method='sum'
else
  method='ave'
endif

qdims()

*
* Make a .ctl file with new grid (no .dat file).
*
ctllines=10
ctlline.1='DSET ^%y4.dat'
ctlline.2='UNDEF -9999'
if(_cal='')
  ctlline.3='options template'
else
  ctlline.3='options template '_cal
endif
ctlline.4='xdef '_.RegridArg.1' linear '_.RegridArg.2' '_.RegridArg.3
ctlline.5='ydef '_.RegridArg.4' linear '_.RegridArg.5' '_.RegridArg.6
ctlline.6=_zdef
ctlline.7=_tdef
ctlline.8='VARS 1'
ctlline.9='newgrid '_nz' 99 New Grid'
ctlline.10='ENDVARS'
cnt=1
while(cnt<=ctllines)
  status=write(mytmpdir'/tavegrid.ctl.'randnum,ctlline.cnt)
  cnt=cnt+1
endwhile
status=close(mytmpdir'/tavegrid.ctl.'randnum)

'set gxout fwrite'
if(_.file.1='')
  'set fwrite 'mytmpdir'/tave.dat.'randnum
else
  'set fwrite '_.path.1'/'_.file.1'.dat'
endif

'set x 1'
'set y 1'
'set z 1'
'set t '_ts' '_te+1
'tavetmp1=sum(1,t='_ts',t+0)+'_ts'-1'
cnt=0
t_start=_ts
'set x 1'
'set y 1'
'set z 1'
'set t 't_start
'tavetmp2=tavetmp1(time+'step')-1'
t_end=getval('tavetmp2','%.12g')
if(t_end='NaN')
  say '[tave ERROR] Time span too short. Use "set time" or "set t" to set time dimension.'
  return
endif
while(t_end!='NaN' & t_end<=_te)
  'set x 1'
  'set y 1'
  'set z 1'
  'set t 't_start
  'tavetmp2=tavetmp1(time+'step')-1'
  t_end=getval('tavetmp2','%.12g')
  vcnt=1
  while(vcnt<=num_var)
    zcnt=_zs
    while(zcnt<=_ze)
      if(num_RegridArg=0)
        'set x '_xs' '_xe
        'set y '_ys' '_ye
        'set z 'zcnt
        'display const('method'('_.var.vcnt',t='t_start',t='t_end'),'_.undef.1',-u)'
      else
        'set x '_xs' '_xe
        'set y '_ys' '_ye
        'set z 'zcnt
        'set t 't_start' 't_end
        'tavetmp3='_.var.vcnt
        'set t 't_start
        dfile_old=dfile()
        'open 'mytmpdir'/tavegrid.ctl.'randnum
        file_num=file_number()
        'set dfile 'file_num
        'set lon '_.RegridArg.2' '_.RegridArg.2+(_.RegridArg.1-1)*_.RegridArg.3
        'set lat '_.RegridArg.5' '_.RegridArg.5+(_.RegridArg.4-1)*_.RegridArg.6
        if(_.RegridArg.3*_.RegridArg.6>_dlon*_dlat)
          'display const(lterp('method'(tavetmp3,t='t_start',t='t_end'),newgrid.'file_num',aave),'_.undef.1',-u)'
        else
          'display const(lterp('method'(tavetmp3,t='t_start',t='t_end'),newgrid.'file_num',bilin),'_.undef.1',-u)'
        endif
        'set dfile 'dfile_old
        'close 'file_num
      endif
      zcnt=zcnt+1
    endwhile
    vcnt=vcnt+1
  endwhile
  cnt=cnt+1
  'set t 't_start' 't_end
  'query dims'
  line5=sublin(result,5)
  tims_tmp=subwrd(line5,6)
  time_tmp=subwrd(line5,8)
  say method' 'cnt' ['tims_tmp','time_tmp']: done.'
  t_start=t_end+1
  'set x 1'
  'set y 1'
  'set z 1'
  'set t 't_start
  'tavetmp2=tavetmp1(time+'step')-1'
  t_end=getval('tavetmp2','%.12g')
endwhile

'disable fwrite'
'set gxout contour'

'set x '_xs' '_xe
'set y '_ys' '_ye
'set z '_zs' '_ze
'set t '_ts' '_te

if(num_RegridArg=0)
  if(_.file.1='')
    writectl(mytmpdir'/tave.ctl.'randnum,'^tave.dat.'randnum,cnt,num_var,name,desc,step,_nx,_lons,_dlon,_ny,_lats,_dlat)
  else
    writectl(_.path.1'/'_.file.1'.ctl','^'_.file.1'.dat',cnt,num_var,name,desc,step,_nx,_lons,_dlon,_ny,_lats,_dlat)
  endif
else
  if(_.file.1='')
    writectl(mytmpdir'/tave.ctl.'randnum,'^tave.dat.'randnum,cnt,num_var,name,desc,step,_.RegridArg.1,_.RegridArg.2,_.RegridArg.3,_.RegridArg.4,_.RegridArg.5,_.RegridArg.6)
  else
    writectl(_.path.1'/'_.file.1'.ctl','^'_.file.1'.dat',cnt,num_var,name,desc,step,_.RegridArg.1,_.RegridArg.2,_.RegridArg.3,_.RegridArg.4,_.RegridArg.5,_.RegridArg.6)
  endif
endif

if(_.file.1='')
  dfile_old=dfile()
  'open 'mytmpdir'/tave.ctl.'randnum
  file_num=file_number()
  'set dfile 'file_num
  vcnt=1
  while(vcnt<=num_var)
    _.name.vcnt'='_.name.vcnt'.'file_num
    vcnt=vcnt+1
  endwhile
  'set dfile 'dfile_old
  '!rm 'mytmpdir'/tave.dat.'randnum
endif

'undefine tavetmp1'
'undefine tavetmp2'
if(num_RegridArg!=0)
'undefine tavetmp3'
endif

*
* Restore original dimension environment.
*
_resetx
_resety
_resetz
_resett

return
***************************************************************************************
function writectl(ctlfile,datfile,nt,nv,var,desc,step,nx,lon_start,dlon,ny,lat_start,dlat)
*
* Write the .ctl file for the temporary .dat file
*
lines=10
line.1='DSET 'datfile
line.2='UNDEF '_.undef.1
if(_cal='')
  line.3='*OPTIONS Intentionally left blank.'
else
  line.3='OPTIONS '_cal
endif
line.4='TITLE Produced by tave.gs.'
line.5='XDEF 'nx' LINEAR 'lon_start' 'dlon
line.6='YDEF 'ny' LINEAR 'lat_start' 'dlat
line.7=_zdef
* Note: 'nt' below is an argument of function 'writectl', not the global variable '_nt'.
line.8='TDEF 'nt' LINEAR '_tims' 'step

*Change TDEF to 00z15 for monthly averages (FDS 01/2014)
*if(step="1mo")
*xxx=00Z15%substr(_tims,6,7)
*say "fds "_tims" "xxx
*line.8='TDEF 'nt' LINEAR 'xxx' 'step
*endif

line.9='VARS 'nv
line.10='ENDVARS'
cnt=1
while(cnt<=lines-1)
  status=write(ctlfile,line.cnt)
  cnt=cnt+1
endwhile
cnt=1
while(cnt<=nv)
  varline=_.var.cnt' '_nz0' 99 '_.desc.cnt
  status=write(ctlfile,varline)
  cnt=cnt+1
endwhile
status=write(ctlfile,line.lines)
status=close(ctlfile)

return
***************************************************************************************
function dfile()
*
* Get the default file number.
*
'q file'

line1=sublin(result,1)
dfile=subwrd(line1,2)

return dfile
***************************************************************************************
function file_number()
*
* Get the number of files opened.
*
'q files'
line1=sublin(result,1)
if(line1='No files open')
  return 0
endif

lines=1
while(sublin(result,lines+1)!='')
  lines=lines+1
endwhile

return lines/3
***************************************************************************************
function dfile_undef()
*
* Get undef value from the default .ctl file. (Not 'q undef', which is for output.)
*
'q ctlinfo'
if(result='No Files Open')
  return 'unknown'
endif

lines=1
while(1)
  lin=sublin(result,lines)
  if(subwrd(lin,1)='undef'|subwrd(lin,1)='UNDEF')
    return subwrd(lin,2)
  endif
  lines=lines+1
endwhile

return
***************************************************************************************
function getval(expr,fmt)
*
* Return value of a GrADS expression in designated format.
*
* Note 1: By default, GrADS only displays 6 significant digits (%.6g) when using 'display ...' or 'query defval ...'.
*         A trick is used below to overcome that limitation (up to 15 significant digits can be returned).
* Note 2: 'display ...' or 'set gxout print' is not used here for getting variable values since that will trigger a bug that prevents the base map from being displayed in contour plots.
*
* Example: sst=getval('sst','%.1f')
*          Note that sst is quoted.
*
'nonexistentvar='expr
'query defval nonexistentvar 1 1'
part1=subwrd(result,3)
if(part1='missing');return 'NaN';endif
'nonexistentvar='expr'-'part1
'query defval nonexistentvar 1 1'
part2=subwrd(result,3)
'nonexistentvar='expr'-'part1'-'part2
'query defval nonexistentvar 1 1'
part3=subwrd(result,3)
'undefine nonexistentvar'

return math_format(fmt,part1+part2+part3)
***************************************************************************************
function parseopt(instr,optprefix,optname,outname)
*
* Parse an option, store argument(s) in a global variable array.
*
rc=gsfallow('on')
cnt=1
cnt2=0
while(subwrd(instr,cnt)!='')
  if(subwrd(instr,cnt)=optprefix''optname)
    cnt=cnt+1
    word=subwrd(instr,cnt)
    while(word!='' & (valnum(word)!=0 | substr(word,1,1)''999!=optprefix''999))
      cnt2=cnt2+1
      _.outname.cnt2=parsestr(instr,cnt)
      if(_end_wrd_idx=-9999);return cnt2;endif
      cnt=_end_wrd_idx+1
      word=subwrd(instr,cnt)
    endwhile
  endif
  cnt=cnt+1
endwhile
return cnt2
***************************************************************************************
function usage()
*
* Print usage information.
*
say '  Time averaging: create lower resolution time series from higher resolution time series; e.g., daily to monthly.'
say ''
say '  USAGE: tave <step> -v <var1> [<var2>...] [-n <name1> [<name2>...]] [-re <nx> <lon_start> <dlon> <ny> <lat_start> <dlat>] [-u <undef>] [-sum 1] [-o <file>] [-p <path>]'
say '    <step>: time step for averaging. MUST be specified in world coordinate, e.g., 6hr, 5dy, 3mo, 1yr, etc.'
say '    <var>: input variable. Can be any GrADS expression.'
say '    <name>: name for output variable. Same as <var> if unset.'
say '    <nx>...<dlat>: arguments for horizontal regridding. Box averaging is used when regridding to coarser grid.'
say '                   Bilinear interpolation is used when regridding to finer grid.'
say '    <undef>: undef value for .dat and .ctl. Value from default file is used if unset.'
say '    -sum 1: summing instead of averaging.'
say '    <file>: common name for output .dat and .ctl files. If set, no variable is defined, only file output.'
say '    <path>: path to output files. Do NOT include trailing "/". Current path is used if unset.'
say ''
say '  NOTE: averaging starts at the first time step of the current dimension, and ends at/before the last time step of the current dimension.'
say '        E.g., if input is 6-hourly, time is set to 06Z01JAN2000-18Z31JAN2000, and <step>=1dy, then averaging starts at 06Z01JAN2000, and ends at 00Z31JAN2000.'
say ''
say '  EXAMPLE 1: create weekly mean and save to variable "sstweek".'
say '    set time 01JAN2000 31DEC2010'
say '    tave 7dy -v sst -n sstweek'
say ''
say '  EXAMPLE 2: as example 1 but with horizontal regridding.'
say '    set time 01JAN2000 31DEC2010'
say '    tave 7dy -re 144 0 2.5 73 -90 2.5 -v sst -n sstweek'
say ''
say '  EXAMPLE 3: create monthly sum and save to files "precipmon.ctl" and "precipmon.dat".'
say '    set time 00Z01JAN2000 23Z31DEC2010'
say '    tave 1mo -v precip -sum 1 -o precipmon'
say ''
say '  DEPENDENCIES: parsestr.gsf qdims.gsf'
say ''
say '  Copyright (c) 2012-2013, Bin Guan'
return
