if {[llength $argv]} {
    set system [lindex $argv 0]
} else {
    puts "Missing arguments: system"
    exit
}

set platform [exec uname]
if {$platform == "Darwin"} {
    set renderer "TachonInternal"
    set ext "tga"
} elseif {$platform == "Linux"} {
    set renderer "TachyonLOptiXInternal"
    set ext "ppm"
    render aasamples $renderer 6
    render aosamples $renderer 6
}

set image_dir [pwd]

cd ../../$system

# display settings
display resize 1024 1024
axes location off
display resetview
display shadows off
display ambientocclusion on
display aoambient 0.8
display aodirect 0.3
display cuedensity 0.1

source $image_dir/$system.tcl

## material settings
#material change ambient AOChalky 0.15
#material change ambient AOEdgy 0.15
#material change outline AOEdgy 3.0
#material change outlinewidth AOEdgy 0.33

#set outfile $image_dir/out/$system.$ext
#exec rm $outfile
#render $renderer $outfile
#exec open $outfile

logfile console

#quit
