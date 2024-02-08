mol new step3_assembly.psf
mol addfile step3_assembly.crd type cor

# membrane
mol material AOEdgy
mol rep VDW
mol selection {segid MEMB or segid "H.*"}
mol addrep top

# KCl
mol selection {segid SV1}
mol addrep top

# setup camera
rotate z by  25
rotate x by -65
scale by 1.4

# TODO: remove below?
material change ambient AOChalky 0.15
material change ambient AOEdgy 0.15
material change outline AOEdgy 3.0
material change outlinewidth AOEdgy 0.33

set outfile $image_dir/out/${system}.tga

if {[file exists $outfile]} {
    exec rm $outfile
}

render TachyonInternal $outfile
exec open $outfile

quit
